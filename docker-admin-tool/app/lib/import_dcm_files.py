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

def upload_file(path: str, URL: str, headers: dict) -> tuple:
    """
    Upload a single file to the PACS via the REST API.
    
    Returns a tuple: (uploaded_successfully, processed)
      - uploaded_successfully is True if the file was uploaded successfully.
      - processed is True if the file was processed (i.e., not skipped).
    """
    try:
        with open(path, 'rb') as f:
            content = f.read()
    except Exception as e:
        sys.stderr.write(f"Error reading file {path}: {e}\n")
        return (False, False)

    sys.stdout.write(f"Importing {path}")

    try:
        h = httplib2.Http()
        resp, _ = h.request(URL, 'POST', body=content, headers=headers)
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

    # Define headers inside the function.
    headers = {"content-type": "application/dicom"}

    # Define file extensions to skip.
    skip_extensions = {
        '.json', '.csv', '.log', '.py', '.txt', '.docx',
        '.jpeg', '.jpg', '.png', '.pdf', '.zip', '.tar',
        '.gz', '.tgz', '.bz2', '.7z'
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
            uploaded, processed = upload_file(full_path, rest_api_url, headers)
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
