import hashlib
import os
import json
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timezone
import time
import inspect


#====================================================================================
verification_folder = './verify'
PRESET_FOLDER = './presets'
METADATA_FOLDER = './metadata'
PRESET_PREFIX = 'hashes_preset_'
METADATA_PREFIX = 'metadata_for_hashes_preset_'
HIT_VERSION = '1.0.0'


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

    #Return if preset already exists
    if os.path.isfile(PRESET_FOLDER + '/' + PRESET_PREFIX + preset_name + '.json'):
        print(f"\n[Error] Preset {preset_name} already exists")
        _create_hashes_preset_metadata(preset_name, inspect.currentframe().f_code.co_name, 0, 0, hashes)
        return

    if not os.path.isdir(PRESET_FOLDER):
        os.mkdir(PRESET_FOLDER)

    start_time = time.perf_counter()

    for f in os.listdir(verification_folder):
        full_path = os.path.join(verification_folder, f)
        if os.path.isfile(full_path):
            print(f"\nappending hash of {f} to preset {PRESET_PREFIX}{preset_name}")
            hashes.append(_calculate_sha256(full_path))
            print("complete")

    # save (once) after collecting hashes
    with open(f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json", 'w') as f:
        json.dump(hashes, f, indent=4)

    duration_seconds = time.perf_counter() - start_time
    _create_hashes_preset_metadata(preset_name, inspect.currentframe().f_code.co_name, 1, duration_seconds, hashes)

#Creates a preset using all files from the 'verify' folder
def _create_hashes_preset_metadata(preset_name: str, action: str, result: int, duration_seconds: float, hashes_written: list):
    filename = f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json"
    mtime = os.path.getmtime(filename)

    if not os.path.isdir(METADATA_FOLDER):
        os.mkdir(METADATA_FOLDER)

    # save (once) after collecting hashes
    with open(f"{METADATA_FOLDER}/{METADATA_PREFIX}{preset_name}.json", 'w') as f:
        json.dump({
            "message": f"The following hashes were added to {PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json",
            "hashes": hashes_written,
            "timestamp of event": datetime.now().astimezone().isoformat(),
            "preset_modified_at": datetime.fromtimestamp(mtime).astimezone().isoformat(),
            "app": "HIT",
            "version": HIT_VERSION,
            "action": action,
            "target_folder": PRESET_FOLDER,
            "preset": f"{PRESET_PREFIX}{preset_name}",
            "result": result,
            "hashes_written": len(hashes_written),
            "duration_ms": f"{duration_seconds:.4f}"
        }, f, indent=2)


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

    #TODO upon preset creation, add the presets rich meta-data to a separate file in a
    #todo metada folder for I in CIA. so creation time,date,location,size,
    #todo file names that were hashed, original folder location
