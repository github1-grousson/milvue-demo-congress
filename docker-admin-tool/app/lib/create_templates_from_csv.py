#!/usr/bin/env python3
import os
import argparse
import csv
import shutil

def generate_templates(templates_folder, csv_file, output_folder):
    """
    For each study in the CSV file, copy the corresponding template file from
    the templates source folder to the output folder. The source file is assumed
    to be {templates_folder}/{ReportTemplateName}.docx and the destination file is
    {output_folder}/{StudyInstanceUID}.docx.
    """
    # Ensure the output folder exists.
    os.makedirs(output_folder, exist_ok=True)
    
    with open(csv_file, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        # Optional: Trim header names if needed:
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        
        for row in reader:
            study_instance_uid = row.get("StudyInstanceUID", "").strip()
            report_template_name = row.get("ReportTemplateName", "").strip()
            
            if not study_instance_uid:
                print("Skipping row with missing StudyInstanceUID.")
                continue
            
            if not report_template_name:
                print(f"The {study_instance_uid} exam doesn't specify a template. Skipping.")
                continue
            
            source_template = os.path.join(templates_folder, report_template_name + ".docx")
            if not os.path.exists(source_template):
                print(f"Template file {source_template} not found for study {study_instance_uid}. Skipping.")
                continue
            
            dest_file = os.path.join(output_folder, study_instance_uid + ".docx")
            try:
                shutil.copy2(source_template, dest_file)
                print(f"Copied template for study {study_instance_uid}: {dest_file}")
            except Exception as e:
                print(f"Error copying template for study {study_instance_uid}: {e}")

def main():
    # Determine the folder of this script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Default paths relative to the script location.
    default_templates_folder = os.path.abspath(os.path.join(script_dir, "..", "..", "assets", "TEMPLATES"))
    default_csv_file = os.path.abspath(os.path.join(script_dir, "..", "..", "assets", "DICOM", "studies.csv"))
    default_output_folder = os.path.abspath(os.path.join(script_dir, "..", "..", "templates"))
    
    parser = argparse.ArgumentParser(
        description="Generate template files from studies CSV and a source templates folder."
    )
    parser.add_argument(
        "--templates_folder",
        type=str,
        default=default_templates_folder,
        help=f"Root TEMPLATES folder (default: {default_templates_folder})"
    )
    parser.add_argument(
        "--csv_file",
        type=str,
        default=default_csv_file,
        help=f"CSV file of studies (default: {default_csv_file})"
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default=default_output_folder,
        help=f"Output folder for final templates (default: {default_output_folder})"
    )
    args = parser.parse_args()
    
    print("Generating templates...")
    generate_templates(args.templates_folder, args.csv_file, args.output_folder)
    print("Template generation complete.")

if __name__ == "__main__":
    main()
