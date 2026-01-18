import hashlib
import os
import json

#====================================================================================
#test data
folder_with_files ='./verify'

#====================================================================================
def calculate_sha256(filename):
    hash_object = hashlib.sha256()

    with open(filename, "rb") as f:
        #so file is read in chunks to handle large files we chose 8192 bytes for effeciency
        while chunk := f.read(8192):
            hash_object.update(chunk)

    return hash_object.hexdigest()

#====================================================================================
def _compare_hashes_with_preset(folder_files_and_hashes: dict, hashes_preset: list):
    files_that_failed_verification = []

    #look through each files hash and if a hash is not in the preset, then add it to list of hashes not found
    for key, value in folder_files_and_hashes.items():
        file_hash = value[0]
        if file_hash in hashes_preset:
            print(f"Verified hash for file: {key}")
            pass
        else:
            files_that_failed_verification.append(key)

    #test outcome
    print(f"files that failed verification: {files_that_failed_verification}")

#====================================================================================
def _get_folder_files_and_there_hashes():
    folder_files_and_hashes = {}

    for f in os.listdir(folder_with_files):
        full_path = os.path.join(folder_with_files, f)
        if os.path.isfile(full_path):
            folder_files_and_hashes[f"{f}"] = []
            folder_files_and_hashes[f"{f}"].append(calculate_sha256(full_path))

    return folder_files_and_hashes


#====================================================================================
def load_preset(preset_to_load_number: str):

    #If user data folder does not exist, create it.
    if not os.path.isdir("presets"):
        os.mkdir("presets")
    path =os.path.abspath("presets/"+f"hashes_preset_{preset_to_load_number}.json")

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

_compare_hashes_with_preset(_get_folder_files_and_there_hashes(), load_preset("01"))


