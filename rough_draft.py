import hashlib
import os
import json


#====================================================================================
verification_folder ='./verify'
PRESET_FOLDER='./presets'
PRESET_PREFIX='hashes_preset_'


#====================================================================================
#Caluclates the hash of a file
def _calculate_sha256(filename):
    hash_object = hashlib.sha256()

    with open(filename, "rb") as f:
        #so file is read in chunks to handle large files we chose 8192 bytes for effeciency
        while chunk := f.read(8192):
            hash_object.update(chunk)

    return hash_object.hexdigest()


#====================================================================================
#Compares each file's corresponding hash from the verify folder with the list of hashes from the chosen preset.
def _compare_hashes_with_preset(folder_files_and_hashes: dict, hashes_preset: list):
    files_that_failed_verification = []

    #look through each files hash and if a hash is not in the preset, then add it to list of hashes not found
    for key, value in folder_files_and_hashes.items():
        file_hash = value[0]
        print(f"verifying in progress for: {file_hash}")
        if file_hash in hashes_preset:
            print(f"Verified hash for file: {key}")
            pass
        else:
            files_that_failed_verification.append(key)

    #test outcome
    print(f"files that failed verification: {files_that_failed_verification}")


#====================================================================================
#Returns a dict of, each file's name and it's corresponding hash from the 'verify' folder.
def _get_hashes():
    folder_files_and_hashes = {}

    for f in os.listdir(verification_folder):
        full_path = os.path.join(verification_folder, f)
        if os.path.isfile(full_path):
            folder_files_and_hashes[f"{f}"] = []
            print(f"calculating hash for file: {f}")
            folder_files_and_hashes[f"{f}"].append(_calculate_sha256(full_path))

    return folder_files_and_hashes


#====================================================================================
#Creates a preset using all files from the 'verify' folder
def _create_preset(preset_name: str):
    hashes = []

    for f in os.listdir(verification_folder):
        full_path = os.path.join(verification_folder, f)
        if os.path.isfile(full_path):
            print(f"appending hashh of {f} to preset {PRESET_PREFIX}{preset_name}")
            hashes.append(_calculate_sha256(full_path))

        #todo make sure preset with same name doesnt already exist

        with open(f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}", 'w') as f:
            json.dump(hashes, f, indent=4)


#====================================================================================
#Returns a list of hashes for the desired preset.
def _load_preset(preset_name: str):

    #If user data folder does not exist, create it.
    if not os.path.isdir("presets"):
        os.mkdir("presets")
    path =os.path.abspath("presets/"+f"{PRESET_PREFIX}{preset_name}.json")

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
        print(f"[Error] Failed to decode JSON in: {path}")
        return None


#====================================================================================
#Deletes the desired preset
def _delete_preset(preset_name: str):
    path = os.path.abspath("presets/"+f"{PRESET_PREFIX}{preset_name}.json")

    if not os.path.isfile(path):
        print(f"[Error] File not found: {path}")
        return
    else:
        os.remove(path)


#====================================================================================
_compare_hashes_with_preset(_get_hashes(), _load_preset("Example"))
#_create_preset("test")
#_delete_preset("Example")
#TODO Make verify folder change-able so user can user file explorer to select the
#todo desired folder to create preset from and verify


