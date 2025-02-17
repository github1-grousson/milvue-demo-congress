#!/usr/bin/env python3
import sys

# Import the other utility scripts. Adjust the module names if necessary.
from lib import create_csv_groupby_study, update_dcm_from_csv_study, update_folder_names


def interactive_menu():
    """
    Presents an interactive menu to the user. 
    The user can choose to:
      1) Create CSV from DICOM root folder.
      2) Update DICOM from CSV.
      3) Reorganize folders names.
    Enter 'q' to exit.
    """
    menu = (
        "\nPlease enter key to launch or q to exit:\n"
        "1) Create CSV from DICOM folder \n"
        "2) Update DICOMs from CSV\n"
        "3) Reorganize DICOMs folders names \n"
        "\n"
        "q) Exit"
        "\n"
    )
    while True:
        choice = input(menu + "\nYour choice: ").strip()
        if choice.lower() == 'q':
            print("Exiting.")
            break
        elif choice == '1':
            print("\nLaunching 'Create CSV from DICOM root folder' utility...\n")
            create_csv_groupby_study.main()
        elif choice == '2':
            print("\nLaunching 'Update DICOM from CSV' utility...\n")
            update_dcm_from_csv_study.main()
        elif choice == '3':
            print("\nLaunching 'Reorganize folders names' utility...\n")
            update_folder_names.main()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)
