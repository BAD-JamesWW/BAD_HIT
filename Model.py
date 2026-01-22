import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import time
import inspect


#====================================================================================
verification_folder = './verify'
PRESET_FOLDER = './presets'
METADATA_FOLDER = './metadata'
PRESET_PREFIX = 'hashes_preset_'
METADATA_FOR_HASHES_PREFIX = 'metadata_for_hashes_preset_'
HIT_VERSION = '1.0.0'


@dataclass
class CompareResult:
    verified_files: List[str]
    failed_files: List[Tuple[str, str]]  # (filename, sha256)


class Model:
    """Core HIT logic (no UI)."""


    # ====================================================================================
    def __init__(self, verification_folder: str = "./verify", preset_folder: str = "./presets", log_fn=print):
        self.verification_folder = os.path.abspath(verification_folder)
        self.preset_folder = os.path.abspath(preset_folder)
        self.preset_prefix = "hashes_preset_"
        self.log = log_fn

        os.makedirs(self.preset_folder, exist_ok=True)


    # ====================================================================================
    # Caluclates the hash of a file
    def _calculate_sha256(self, filename):
        hash_object = hashlib.sha256()

        with open(filename, "rb") as f:
            # so file is read in chunks to handle large files we chose 8192 bytes for effeciency
            while chunk := f.read(8192):
                hash_object.update(chunk)

        return hash_object.hexdigest()

    # ====================================================================================
    # Used to set the verification folder
    def set_verification_folder(self, folder: str) -> None:
        folder = os.path.abspath(folder)
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Verification folder does not exist: {folder}")
        self.verification_folder = folder


    # ====================================================================================
    # Used to create a preset using all files from the verification folder
    def _create_preset(self, preset_name: str):
        hashes = []

        # Return if preset already exists
        if os.path.isfile(PRESET_FOLDER + '/' + PRESET_PREFIX + preset_name + '.json'):
            self.log(f"\n[Error] Preset {preset_name} already exists")
            self._create_hashes_preset_metadata(
                preset_name,
                inspect.currentframe().f_code.co_name,
                0,
                0,
                hashes
            )
            return

        if not os.path.isdir(PRESET_FOLDER):
            os.mkdir(PRESET_FOLDER)

        start_time = time.perf_counter()

        # IMPORTANT: recurse into subfolders too
        for root, _, files in os.walk(self.verification_folder):
            for name in files:
                full_path = os.path.join(root, name)
                if os.path.isfile(full_path):
                    rel_path = os.path.relpath(full_path,
                                               self.verification_folder)  # keeps folder structure in the name
                    self.log(f"\nGenerating hash of {rel_path} to preset {PRESET_PREFIX}{preset_name}...")
                    hashes.append(self._calculate_sha256(full_path))
                    self.log("complete")

        # save (once) after collecting hashes
        with open(f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json", 'w') as f:
            json.dump(hashes, f, indent=4)

        duration_seconds = time.perf_counter() - start_time
        self._create_hashes_preset_metadata(
            preset_name,
            inspect.currentframe().f_code.co_name,
            1,
            duration_seconds,
            hashes
        )

        self.log(f"\n[OK] Preset {PRESET_PREFIX}{preset_name} created.")


    # ====================================================================================
    # Used to write metadata for the creation of presets
    def _create_hashes_preset_metadata(
        self,
        preset_name: str,
        action: str,
        result: int,
        duration_seconds: float,
        hashes_written: list
    ):
        filename = f"{PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json"
        mtime = os.path.getmtime(filename)

        if not os.path.isdir(METADATA_FOLDER):
            os.mkdir(METADATA_FOLDER)

        # Append metadata to corresponding .json
        metadata_path = f"{METADATA_FOLDER}/{METADATA_FOR_HASHES_PREFIX}{preset_name}.json"

        event = {
            "message": f"The following hashes were added to {PRESET_FOLDER}/{PRESET_PREFIX}{preset_name}.json",
            "hashes": hashes_written,
            "timestamp_of_event": datetime.now().astimezone().isoformat(),
            "preset_modified_at": datetime.fromtimestamp(mtime).astimezone().isoformat(),
            "app": "HIT",
            "version": HIT_VERSION,
            "action": action,
            "target_folder": PRESET_FOLDER,
            "preset": f"{PRESET_PREFIX}{preset_name}",
            "result": result,
            "hashes_written": len(hashes_written),
            "duration_ms": f"{duration_seconds:.4f}"
        }

        # read existing list (or create new one)
        if os.path.isfile(metadata_path):
            with open(metadata_path, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]  # convert old single object to list
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        # append event
        data.append(event)

        # write back
        with open(metadata_path, "w") as f:
            json.dump(data, f, indent=2)
