#!/usr/bin/env python3
"""
Recursively upload DICOM files to a PACS server via its REST API.

Default URL is: http://127.0.01/pacs
Default input directory is computed as: <script_dir>/../../assets/DICOM

Usage:
    python upload_dcm.py [--input_dir /path/to/dicom_folder] [--URL http://127.0.01/pacs]
"""

import os
import sys
import httplib2
import argparse
import json
import pydicom

def upload_file(path: str, upload_url: str, find_url: str, headers: dict) -> tuple:
    """
    Upload a single DICOM file to Orthanc via the REST API.
    
    Before uploading, the function extracts the SOP Instance UID from the file and
    sends a query to Orthanc’s /tools/find endpoint. If an instance with the same UID
    is already present, the upload is skipped.
    
    Returns a tuple: (uploaded_successfully, processed)
      - uploaded_successfully is True if the file was uploaded successfully.
      - processed is True if the file was processed (even if skipped).
    """
    # Attempt to read the DICOM header and extract the SOPInstanceUID.
    instance_uid = None
    try:
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        instance_uid = ds.SOPInstanceUID
    except Exception as e:
        sys.stderr.write(f"Error reading DICOM header from {path}: {e}\n")
    
    # If a UID was found, check if the instance already exists in Orthanc.
    if instance_uid:
        query_payload = json.dumps({
            "Level": "Instance",
            "Query": {"SOPInstanceUID": instance_uid}
        })
        try:
            h = httplib2.Http()
            find_headers = {"Content-Type": "application/json"}
            resp, content = h.request(find_url, 'POST', body=query_payload, headers=find_headers)
            if resp.status == 200:
                # Parse the returned JSON array.
                results = json.loads(content.decode('utf-8') if isinstance(content, bytes) else content)
                if isinstance(results, list) and len(results) > 0:
                    sys.stdout.write(f"Skipping {path}: instance {instance_uid} already exists in PACS.\n")
                    return (False, True)  # Processed but not uploaded.
            else:
                sys.stderr.write(f"Error checking instance existence for {path}: HTTP {resp.status}\n")
        except Exception as e:
            sys.stderr.write(f"Error checking instance existence for {path}: {e}\n")
    
    # Read file content for upload.
    try:
        with open(path, 'rb') as f:
            file_content = f.read()
    except Exception as e:
        sys.stderr.write(f"Error reading file {path}: {e}\n")
        return (False, False)
    
    sys.stdout.write(f"Importing {path}")
    
    try:
        h = httplib2.Http()
        resp, _ = h.request(upload_url, 'POST', body=file_content, headers=headers)
        if resp.status == 200:
            sys.stdout.write(" => success\n")
            return (True, True)
        else:
            sys.stdout.write(" => failure (Is it a DICOM file?)\n")
            return (False, True)
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        sys.stdout.write(" => unable to connect\n")
        return (False, True)

def process_folder(root_folder: str, URL: str):
    """
    Process a folder of DICOM files:
      - Walk the directory recursively.
      - Skip files with unwanted extensions.
      - Upload each file to the PACS server.
    
    The function defines the headers internally.
    Prints a summary of the operation.
    """

    #define the endpoint URL which is join of URL and /instances
    rest_api_url = URL + "/instances"

    #define the endpoint URL which is join of URL and /tools/find
    find_url = URL + "/tools/find"

    # Define headers inside the function.
    headers = {"content-type": "application/dicom"}

    # Define file extensions to skip.
    skip_extensions = {
        '.json', '.csv', '.log', '.py', '.txt', '.docx',
        '.jpeg', '.jpg', '.png', '.pdf', '.zip', '.tar',
        '.gz', '.tgz', '.bz2', '.7z', '.md'
    }

    if not os.path.isdir(root_folder):
        sys.stderr.write(f"Error: The input path '{root_folder}' is not a directory or don't exist.\n")
        return

    dicom_count = 0
    skipped_count = 0
    total_file_count = 0

    for root, _, files in os.walk(root_folder):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in skip_extensions:
                print(f"Skipping file {os.path.join(root, filename)} with extension {ext}")
                skipped_count += 1
                continue
            full_path = os.path.join(root, filename)
            uploaded, processed = upload_file(full_path, rest_api_url, find_url , headers)
            total_file_count += 1
            if processed and uploaded:
                dicom_count += 1

    print(f"\nSUCCESS: {dicom_count} DICOM file(s) have been successfully imported on {total_file_count} file(s) found.")
    print(f"Skipped: {skipped_count} file(s) with unsupported extensions\n")

def main():
    # Compute the default root directory relative to the script location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_root_dir = os.path.abspath(os.path.join(script_dir, "../../assets/DICOM"))

    parser = argparse.ArgumentParser(
        description="Upload DICOM files from a given folder to a PACS server via REST API."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default=default_root_dir,
        help=f"Path to the root DICOM input folder (default: {default_root_dir})"
    )
    parser.add_argument(
        "--URL",
        type=str,
        default="http://127.0.01/pacs",
        help="PACS server URL (default: http://127.0.01/pacs)"
    )
    args = parser.parse_args()

    process_folder(args.input_dir, args.URL)

if __name__ == "__main__":
    main()
