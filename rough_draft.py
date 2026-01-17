import hashlib
import os
import numpy as np

#====================================================================================
#test data
folder_with_files ='./test'

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
#todo so presets can be stored in json files and read as lists like OPS
hashes_preset_01 = ["b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
                 "XX4d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcdXX"]

_compare_hashes_with_preset(_get_folder_files_and_there_hashes(), hashes_preset_01)


