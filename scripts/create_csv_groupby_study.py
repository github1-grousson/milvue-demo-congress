#!/usr/bin/env python3
import os
import argparse
import csv
import pydicom

def collect_study_data(input_dir):
    """
    Traverse the input directory recursively, read DICOM files,
    and collect one record per unique StudyInstanceUID.
    """
    studies = {}
    for root, _, files in os.walk(input_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                # Read file with pydicom (skip pixel data for speed)
                ds = pydicom.dcmread(filepath, stop_before_pixels=True, force=True)
                study_uid = getattr(ds, 'StudyInstanceUID', None)
                if not study_uid:
                    continue  # Skip files without a StudyInstanceUID
                # Only add the study if it's not already present
                if study_uid not in studies:
                    studies[study_uid] = {
                        'PatientName': str(getattr(ds, 'PatientName', '')),
                        'PatientID': getattr(ds, 'PatientID', ''),
                        'PatientBirthDate': getattr(ds, 'PatientBirthDate', ''),
                        'PatientAge': getattr(ds, 'PatientAge', ''),
                        'PatientSex': getattr(ds, 'PatientSex', ''),
                        'AccessionNumber': getattr(ds, 'AccessionNumber', ''),
                        'StudyDate': getattr(ds, 'StudyDate', ''),
                        'StudyDescription': getattr(ds, 'StudyDescription', ''),
                        'StudyInstanceUID': study_uid,
                        'ReportTemplateName': ''  # Leave blank as required
                    }
            except Exception as e:
                # If file is not a valid DICOM, skip it.
                continue
    return studies

def write_csv(studies, output_dir):
    """
    Write the collected study data to a CSV file.
    The CSV file is saved as 'studies.csv' in the output directory.
    Studies are ordered by PatientName.
    """
    csv_filename = os.path.join(output_dir, "studies.csv")
    fieldnames = [
        'PatientName',
        'PatientID',
        'PatientBirthDate',
        'PatientAge',
        'PatientSex',
        'AccessionNumber',
        'StudyDate',
        'StudyDescription',
        'StudyInstanceUID',
        'ReportTemplateName'
    ]
    
    # Sort the studies by PatientName
    sorted_studies = sorted(studies.values(), key=lambda x: x['PatientName'])
    
    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for study in sorted_studies:
            writer.writerow(study)
    
    print(f"CSV file successfully created at: {csv_filename}")

def main():
    # Compute the default input directory relative to the script location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input_dir = os.path.abspath(os.path.join(script_dir, "../DICOM/00_inputs"))

    parser = argparse.ArgumentParser(
        description="Generate a CSV file at study level by parsing a DICOM directory."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default=default_input_dir,
        help="Path to the root DICOM input folder (default: ../DICOM/00_inputs)"
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist or is not a directory.")
        exit(1)

    print("Collecting DICOM study data...")
    studies = collect_study_data(input_dir)
    print(f"Found {len(studies)} unique studies.")

    # Output CSV will be placed in the same folder as the input folder.
    write_csv(studies, input_dir)

if __name__ == "__main__":
    main()
