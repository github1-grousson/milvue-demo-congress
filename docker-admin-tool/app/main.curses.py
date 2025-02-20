#!/usr/bin/env python3
"""
Curses-based Interactive Main Menu for DICOM Utilities

Main Menu Options:
  1) Create CSV from DICOM folder
  2) Update DICOMs from CSV
  3) Reorganize DICOMs folders names
  4) Create report templates from CSV
  5) Import DICOM folders (with its own submenu)
  6) Exit

When option 5 is chosen, an import submenu is presented:
  1) Import '00_inputs'
  2) Import '01_outputs_fr'
  3) Import '02_outputs_en'
  4) Back

Paths are computed relative to the script location.
"""

import os
import curses

# Import your utility modules (adjust the module names/path as needed)
from lib import create_csv_groupby_study
from lib import update_dcm_from_csv_study
from lib import update_folder_names
from lib import create_templates_from_csv
from lib.import_dcm_files import process_folder   # process_folder(root_folder: str, URL: str)

# Set the application title
app_title = "Milvue admin Utilities"
# Get version from environment variable (set at build time)
current_app_version = os.getenv("APP_VERSION", "1.0")  # Default to "1.0" if not set

def curses_menu(stdscr, title, menu_items):
    """
    Displays a vertical menu using curses.
    Returns the index of the selected menu item when Enter is pressed.
    
    An extra blank line is inserted above the final option if that option is "Exit" or "Back",
    and additional padding is added between each menu item for clarity.
    """
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.keypad(True)
    current_row = 0

    # Define extra vertical padding between items
    line_padding = 1

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD)
        stdscr.addstr(2, width // 2 - len(title) // 2, "-"*len(title), curses.A_BOLD)
        # Render menu items with padding
        line = 4
        for idx, item in enumerate(menu_items):
            # If this is the final option and it is "Exit" or "Back", insert an extra blank line before it
            if idx == len(menu_items) - 1 and item.lower() in ["exit", "back"]:
                line += 1
            x = width // 2 - len(item) // 2
            y = line
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)
            line += 1 + line_padding  # add extra blank line(s) between menu items

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            return current_row

def run_utility(func, *args, **kwargs):
    """
    Temporarily exits curses to run a given utility function,
    then waits for the user to press Enter before returning.
    """
    curses.endwin()
    try:
        func(*args, **kwargs)
        input("\nPress Enter to return to the menu...")
    except Exception as e:
        print("Error running utility:", e)
        input("\nPress Enter to return to the menu...")

def main():
    # Define default variables (adjust paths as needed)
    default_PACS_URL = "http://127.0.0.1/pacs"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_dicom_root = os.path.abspath(os.path.join(script_dir, "assets/DICOM"))
    default_csv_file = os.path.join(default_dicom_root, "studies.csv")
    default_templates_root = os.path.abspath(os.path.join(script_dir, "assets/TEMPLATES"))
    default_output_templates = os.path.abspath(os.path.join(script_dir, "templates"))

    main_menu_items = [
        "Create CSV from DICOM folder",
        "Update DICOMs from CSV",
        "Reorganize DICOMs folders names",
        "Create report templates from CSV",
        "Import DICOM folders",
        "Exit"
    ]

    import_menu_items = [
        "Import '00_inputs'",
        "Import '01_outputs_fr'",
        "Import '02_outputs_en'",
        "Back"
    ]

    while True:
        # Display the main menu
        choice = curses.wrapper(lambda stdscr: curses_menu(stdscr, f"{app_title} {current_app_version} Main Menu", main_menu_items))
        
        if choice == 0:
            # Option 1: Create CSV from DICOM folder
            run_utility(create_csv_groupby_study.process_create_csv, default_dicom_root, "00_inputs")
        elif choice == 1:
            # Option 2: Update DICOMs from CSV
            run_utility(update_dcm_from_csv_study.process_update_dcm, default_dicom_root, default_csv_file)
        elif choice == 2:
            # Option 3: Reorganize DICOMs folders names
            run_utility(update_folder_names.process_rename, default_dicom_root)
        elif choice == 3:
            # Option 4: Create report templates from CSV
            run_utility(create_templates_from_csv.generate_templates, default_templates_root, default_csv_file, default_output_templates)
        elif choice == 4:
            # Option 5: Import DICOM folders (display the import submenu)
            while True:
                import_choice = curses.wrapper(lambda stdscr: curses_menu(stdscr, "Import DICOM Folders", import_menu_items))
                if import_choice == 3:  # "Back" option
                    break
                else:
                    # Map submenu index to the corresponding folder name
                    subdirs = ["00_inputs", "01_outputs_fr", "02_outputs_en"]
                    folder = subdirs[import_choice]
                    folder_path = os.path.join(default_dicom_root, folder)
                    run_utility(process_folder, folder_path, default_PACS_URL)
        elif choice == 5:
            # Option 6: Exit
            break

if __name__ == "__main__":
    main()
