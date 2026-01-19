import hashlib
import os
import json
import sys
import tkinter as tk
from tkinter import filedialog


#====================================================================================
verification_folder = './verify'
PRESET_FOLDER = './presets'
PRESET_PREFIX = 'hashes_preset_'


#====================================================================================
def _select_verification_folder_on_launch() -> str:
    """
    Opens a Windows folder picker and returns the selected folder.
    If the user cancels, the program exits.
    """
    root = tk.Tk()
    root.withdraw()          # hide the main tkinter window
    root.attributes('-topmost', True)  # bring dialog to front

    selected = filedialog.askdirectory(
        title="Select folder to VERIFY",
        initialdir=os.path.abspath(verification_folder) if os.path.isdir(verification_folder) else os.getcwd()
    )

    root.destroy()

    if not selected:
        print("\nNo folder selected. Exiting.")
        sys.exit(0)

    return os.path.abspath(selected)


#====================================================================================
#Caluclates the hash of a file
def _calculate_sha256(filename):
    hash_object = hashlib.sha256()

    with open(filename, "rb") as f:
        # so file is read in chunks to handle large files we chose 8192 bytes for effeciency
        while chunk := f.read(8192):
            hash_object.update(chunk)

    return hash_object.hexdigest()


#====================================================================================
#Compares each file's corresponding hash from the verify folder with the list of hashes from the chosen preset.
def _compare_hashes_with_preset(folder_files_and_hashes: dict, hashes_preset: list):
    if hashes_preset is None:
        print('\nNo preset found')
        return

    files_that_failed_verification = []

    #look through each files hash and if a hash is not in the preset, then add it to list of hashes not found
    for key, value in folder_files_and_hashes.items():
        file_hash = value[0]
        print(f"\nverifying in progress for: {key}")
        if file_hash in hashes_preset:
            pass
        else:
            files_that_failed_verification.append(key)
        print("complete")

    #test outcome
    if not files_that_failed_verification:
        print("\nAll files passed verification")
        return
    else:
        print(f"\nfiles that failed verification: {files_that_failed_verification}")


#====================================================================================
#Returns a dict of, each file's name and it's corresponding hash from the 'verify' folder.
def _get_hashes():
    folder_files_and_hashes = {}

    if not os.path.isdir(verification_folder):
        print(f"\n[Error] Verification folder not found: {verification_folder}")
        return folder_files_and_hashes

    for f in os.listdir(verification_folder):
        full_path = os.path.join(verification_folder, f)
        if os.path.isfile(full_path):
            folder_files_and_hashes[f"{f}"] = []
            print(f"\ncalculating hash for file: {f}")
            folder_files_and_hashes[f"{f}"].append(_calculate_sha256(full_path))
            print("complete")

    return folder_files_and_hashes


#====================================================================================
#Creates a preset using all files from the 'verify' folder
def _create_preset(preset_name: str):
    hashes = []

    #todo if preset file already exists do error already exists

    if not os.path.isdir(PRESET_FOLDER):
        os.mkdir(PRESET_FOLDER)

    for f in os.listdir(verification_folder):
        full_path = os.path.join(verification_folder, f)
        if os.path.isfile(full_path):
            print(f"\nappending hash of {f} to preset {PRESET_PREFIX}{preset_name}")
            hashes.append(_calculate_sha256(full_path))
            print("complete")

    # save (once) after collecting hashes
    with open(f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json", 'w') as f:
        json.dump(hashes, f, indent=4)


#====================================================================================
#Returns a list of hashes for the desired preset.
def _load_preset(preset_name: str):

    #If user data folder does not exist, create it.
    if not os.path.isdir(PRESET_FOLDER):
        os.mkdir(PRESET_FOLDER)

    path = os.path.abspath(f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json")

    if not os.path.isfile(path):
        return None

    try:
        with open(path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return data
            else:
                return None
    except json.JSONDecodeError:
        print(f"\n[Error] Failed to decode JSON in: {path}")
        return None


#====================================================================================
#Deletes the desired preset
def _delete_preset(preset_name: str):
    path = os.path.abspath(f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json")

    if not os.path.isfile(path):
        print(f"\n[Error] File not found: {path}")
        return
    else:
        os.remove(path)


#====================================================================================
if __name__ == "__main__":
    # On launch: force user to pick the verify folder
    verification_folder = _select_verification_folder_on_launch()
    print(f"\nUsing verification folder: {verification_folder}")

    _create_preset("Example")

    _compare_hashes_with_preset(_get_hashes(), _load_preset("Example"))

    # _delete_preset("Example")
