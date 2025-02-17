#!/usr/bin/env python3
import os
import argparse
import shutil
import pydicom

def truncate_text(text, max_length=24):
    """Truncate the text to max_length characters if necessary."""
    if not text:
        return "Unknown"
    text = str(text).strip()
    return text if len(text) <= max_length else text[:max_length]

def sanitize_folder_name(folder_name):
    """Replace invalid characters in folder_name with underscores."""
    invalid_chars = [' ','\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        folder_name = folder_name.replace(char, '_')
    return folder_name

def generate_folder_structure(file_path, root_dir):
    """
    Read DICOM tags from file_path and return the destination folder path
    based on the following structure:
      {root_dir}/Patient-{PatientName}/Study-{StudyDescription}/Series-{SeriesDescription}/
    The StudyDescription and SeriesDescription are truncated to 16 characters if needed.
    """
    try:
        # Read only header information for speed
        ds = pydicom.dcmread(file_path, stop_before_pixels=True, force=True)
    except Exception as e:
        # If the file cannot be read as DICOM, return None.
        print(f"Skipping non-DICOM file: {file_path} ({e})")
        return None

    patient_name = sanitize_folder_name(str(getattr(ds, 'PatientName', 'Unknown')).strip() or "Unknown")
    study_desc   = sanitize_folder_name(truncate_text(getattr(ds, 'StudyDescription', 'Unknown')))
    series_desc  = sanitize_folder_name(truncate_text(getattr(ds, 'SeriesDescription', 'Unknown')))

    # Build the destination folder path
    dest_folder = os.path.join(
        root_dir,
        f"Patient-{patient_name}",
        f"Study-{study_desc}",
        f"Series-{series_desc}"
    )
    return dest_folder

def reorganize_dicom_files(root_dir):
    """
    Walk the root directory, skipping files with extensions listed in skip_extensions.
    For each valid DICOM file, determine its new destination folder and move the file if needed.
    """
    # List of file extensions to skip (case-insensitive)
    skip_extensions = {'.csv', '.log', '.py', '.txt', '.docx', '.jpeg', '.jpg', '.png', 
                       '.pdf', '.zip', '.tar', '.gz', '.tgz', '.bz2', '.7z'}

    # Create a list of files to process (to avoid modifying the tree while walking)
    files_to_process = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in skip_extensions:
                continue
            files_to_process.append(os.path.join(dirpath, filename))

    # Process each file
    for file_path in files_to_process:
        dest_folder = generate_folder_structure(file_path, root_dir)
        if dest_folder is None:
            continue  # skip non-DICOM files
        current_folder = os.path.abspath(os.path.dirname(file_path))
        dest_folder_abs = os.path.abspath(dest_folder)
        # If the file is already in the proper destination, skip it.
        if current_folder == dest_folder_abs:
            continue

        # Create destination directory if it doesn't exist.
        os.makedirs(dest_folder_abs, exist_ok=True)
        new_path = os.path.join(dest_folder_abs, os.path.basename(file_path))

        try:
            shutil.move(file_path, new_path)
            print(f"Moved: {file_path} --> {new_path}")
        except Exception as e:
            print(f"Error moving {file_path} to {new_path}: {e}")

def delete_empty_dirs(root_dir):
    """
    Recursively delete empty directories under root_dir.
    This function repeatedly scans for empty directories until no more can be removed.
    The root_dir itself is not deleted.
    """
    removed_any = True
    while removed_any:
        removed_any = False
        # Walk from the deepest directories upward.
        for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
            # Skip the root directory itself
            if os.path.abspath(dirpath) == os.path.abspath(root_dir):
                continue
            # Re-check the directory's contents because os.walk's list might be stale.
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    removed_any = True
                    print(f"Deleted empty directory: {dirpath}")
            except Exception as e:
                print(f"Error deleting directory {dirpath}: {e}")

def main():
    # Compute the default root directory relative to the script location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_root_dir = os.path.abspath(os.path.join(script_dir, "../DICOM"))

    parser = argparse.ArgumentParser(
        description="Reorganize DICOM files under the root directory into a folder structure based on DICOM tags."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default=default_root_dir,
        help=f"Path to the root DICOM input folder (default: {default_root_dir})"
    )
    parser.add_argument(
        "--delete_empty",
        action="store_true",
        default=True,
        help="Delete empty directories after moving files."
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist or is not a directory.")
        exit(1)

    print(f"Reorganizing DICOM files under: {input_dir}")
    list_subdirs = {"00-inputs", "01-outputs-fr",  "02-outputs-en"}
    for subdir in list_subdirs:
        reorganize_dicom_files(os.path.join(input_dir, subdir))
    print("Reorganization complete.")

    if args.delete_empty:
        print("Deleting empty directories...")
        delete_empty_dirs(input_dir)
        print("Empty directories deletion complete.")

if __name__ == "__main__":
    main()