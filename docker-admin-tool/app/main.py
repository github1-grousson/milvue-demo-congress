#!/usr/bin/env python3
"""
Interactive Main Menu for DICOM Utilities

Options:
  1) Create CSV from DICOM folder
  2) Update DICOMs from CSV
  3) Reorganize DICOMs folders names
  4) Create report templates from CSV
  5) Import DICOM folders
  q) Exit

When option 5 is chosen, a sub-menu is presented:
  1) Import '00_inputs'
  2) Import '01_outputs_fr'
  3) Import '02_outputs_en'
  4) Back

Paths are computed relative to the script location.
"""

import os

# Import your utility modules (adjust the module names/path as needed)
from lib import create_csv_groupby_study
from lib import update_dcm_from_csv_study
from lib import update_folder_names
from lib import create_templates_from_csv
from lib.import_dcm_files import process_folder   # process_folder(root_folder: str, URL: str)

def import_dicom_submenu(root_folder: str, default_URL: str):
    """
    Presents a sub-menu for importing DICOM folders.
    The available subdirectories are:
      1) Import '00_inputs'
      2) Import '01_outputs_fr'
      3) Import '02_outputs_en'
      4) Back
    Each selection calls process_folder() with the proper path.
    """
    # Map submenu choices to subdirectory names.
    list_subdirs = {
        "1": "00_inputs",
        "2": "01_outputs_fr",
        "3": "02_outputs_en"
    }
    submenu = (
        "\nPlease enter key to import DICOM folders or '4' to go back:\n"
        "1) Import '00_inputs'\n"
        "2) Import '01_outputs_fr'\n"
        "3) Import '02_outputs_en'\n"
        "4) Back\n"
    )
    while True:
        choice = input(submenu + "\nYour choice: ").strip()
        if choice == '4':
            break
        elif choice in list_subdirs:
            folder = list_subdirs[choice]
            folder_path = os.path.join(root_folder, folder)
            print(f"\nImporting DICOM folder: {folder_path}\n")
            process_folder(folder_path, default_URL)
        else:
            print("Invalid choice, please try again.")

def interactive_menu():
    """
    Presents the interactive menu to the user.
    The user can choose one of several DICOM utilities.
    """

    # We start by fixing default variables
    default_PACS_URL = "http://127.0.0.1/pacs"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_dicom_root = os.path.abspath(os.path.join(script_dir, "assets/DICOM"))
    default_csv_file = os.path.join(default_dicom_root, "studies.csv")
    default_templates_root = os.path.abspath(os.path.join(script_dir, "assets/TEMPLATES"))
    default_output_templates = os.path.abspath(os.path.join(script_dir, "templates"))

    menu = (
        "\nDICOM Utilities 1.3 Main Menu\n"
        "\nPlease enter key to launch or 'q' to exit:\n"
        "1) Create CSV from DICOM folder\n"
        "2) Update DICOMs from CSV\n"
        "3) Reorganize DICOMs folders names\n"
        "4) Create report templates from CSV\n"
        "5) Import DICOM folders\n"
        "\nq) Exit\n"
    )
    while True:
        choice = input(menu + "\nYour choice: ").strip()
        if choice.lower() == 'q':
            print("Exiting.")
            break
        elif choice == '1':
            print("\nLaunching 'Create CSV from DICOM folder' utility...\n")
            create_csv_groupby_study.process_create_csv(default_dicom_root, "00_inputs")
        elif choice == '2':
            print("\nLaunching 'Update DICOMs from CSV' utility...\n")
            update_dcm_from_csv_study.process_update_dcm(default_dicom_root, default_csv_file)
        elif choice == '3':
            print("\nLaunching 'Reorganize DICOMs folders names' utility...\n")
            update_folder_names.process_rename(default_dicom_root)
        elif choice == '4':
            print("\nLaunching 'Create report templates from CSV' utility...\n")
            print("Generating templates...")
            create_templates_from_csv.generate_templates(default_templates_root, default_csv_file, default_output_templates)
            print("Template generation complete.")
        elif choice == '5':
            print("\nLaunching 'Import DICOM folders' utility...\n")
            import_dicom_submenu(default_dicom_root, default_PACS_URL)
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    interactive_menu()
