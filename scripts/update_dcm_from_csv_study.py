#!/usr/bin/env python3
import os
import argparse
import csv
import pydicom
from create_csv_groupby_study import collect_study_data, write_csv

def read_csv_data(csv_file_path):
    """
    Reads the CSV file and returns a dictionary mapping StudyInstanceUID to its row data.
    Before processing, it trims extra spaces from header and each cell value.
    """
    csv_data = {}
    with open(csv_file_path, mode='r', newline='') as csvfile:
        # Use skipinitialspace to ignore spaces after delimiter
        reader = csv.DictReader(csvfile, skipinitialspace=True)
        # Shrink header field names
        reader.fieldnames = [field.strip() for field in reader.fieldnames]
        for row in reader:
            # Trim spaces from both keys and values
            trimmed_row = {k.strip(): (v.strip() if v is not None else '') for k, v in row.items()}
            study_uid = trimmed_row.get('StudyInstanceUID')
            if study_uid:
                csv_data[study_uid] = trimmed_row
    return csv_data

def update_dicom_file(file_path, csv_data):
    """
    For a given DICOM file, update tags based on CSV data if the StudyInstanceUID matches.
    Only update the following tags if they differ:
      PatientName, PatientID, PatientBirthDate, PatientAge,
      AccessionNumber, StudyDate, StudyDescription.
    (ReportTemplateName is ignored.)
    Returns True if the file was updated, False otherwise.
    """
    try:
        ds = pydicom.dcmread(file_path, force=True)
    except Exception:
        # Not a valid DICOM file, so skip it.
        return False

    study_uid = getattr(ds, 'StudyInstanceUID', None)
    if not study_uid or study_uid not in csv_data:
        return False

    csv_row = csv_data[study_uid]
    # Tags to update (ignoring ReportTemplateName)
    tags_to_update = [
        'PatientName',
        'PatientID',
        'PatientBirthDate',
        'PatientAge',
        'PatientSex',
        'AccessionNumber',
        'StudyDate',
        'StudyDescription'
    ]
    updated = False
    updated_tags = []
    for tag in tags_to_update:
        csv_value = csv_row.get(tag, '')
        dicom_value = str(getattr(ds, tag, ''))
        if dicom_value != csv_value:
            setattr(ds, tag, csv_value)
            updated = True
            updated_tags.append(tag)
    if updated:
        try:
            ds.save_as(file_path, write_like_original=True)
            print(f"Updated {file_path}: {', '.join(updated_tags)}")
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    return updated

def update_dicom_tags_in_dir(input_dir, csv_data):
    """
    Traverse the input directory recursively and update all DICOM files based on CSV data.
    Files with extensions in the skip list (.csv, .log, .py, .txt, .docx, .jpeg, .jpg, .png) are skipped.
    Returns the number of files updated.
    """
    updated_files = 0
    skip_extensions = {'.csv', '.log', '.py', '.txt', '.docx', '.jpeg', '.jpg', '.png', '.pdf', '.zip', '.tar', '.gz', '.tgz', '.bz2', '.7z'}
    for root, _, files in os.walk(input_dir):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in skip_extensions:
                continue
            file_path = os.path.join(root, filename)
            if update_dicom_file(file_path, csv_data):
                updated_files += 1
    return updated_files

def main():
    # Compute the default root directory relative to the script location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_root_dir = os.path.abspath(os.path.join(script_dir, "../DICOM/"))

    parser = argparse.ArgumentParser(
        description="Update DICOM tags based on a CSV file at the study level and regenerate CSV if changes occurred."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default=default_root_dir,
        help=f"Path to the root DICOM input folder (default: {default_root_dir})"
    )
    parser.add_argument(
        "--csv_file",
        type=str,
        default=None,
        help="Path to the CSV file (default: <input_dir>/studies.csv)"
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist or is not a directory.")
        exit(1)

    # Use provided CSV file or default to studies.csv in the input directory.
    csv_file = args.csv_file if args.csv_file else os.path.join(input_dir, "studies.csv")
    if not os.path.isfile(csv_file):
        print(f"Error: The CSV file '{csv_file}' does not exist.")
        exit(1)

    print("Reading CSV file...")
    csv_data = read_csv_data(csv_file)
    if len(csv_data) == 0:
        print("Error: No data found in the CSV file.")
        exit(1)
    print(f"CSV data loaded for {len(csv_data)} studies.")

    print("Updating DICOM files...")
    updated_files = update_dicom_tags_in_dir(input_dir, csv_data)
    print(f"Total files updated: {updated_files}")

    if updated_files > 0:
        print("At least one file was updated; regenerating CSV file from updated DICOM files...")
        studies = collect_study_data(input_dir)
        write_csv(studies, input_dir)
    else:
        print("No updates were made; CSV file regeneration is not necessary.")

if __name__ == "__main__":
    main()
