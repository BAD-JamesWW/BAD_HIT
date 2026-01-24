from __future__ import annotations

import os
import traceback

from Model import Model
from View import View


class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        model.log = view.log


    # ===================================(CALLBACKS)======================================
    def on_action_clicked(self) -> None:
        try:
            preset_name = self.view.get_preset_name_input().strip()
            if not preset_name:
                self.view.play_sound("assets/audio/ui_sound_05.wav", False)
                self.view.log("\n[Error] Preset name is required.")
                return

            if not os.path.isdir(self.model.verification_folder):
                self.view.play_sound("assets/audio/ui_sound_05.wav", False)
                self.view.log("\n[Error] Verification folder is not set. Click 'Choose verification folder…' first.")
                return

            self.view.play_sound("assets/audio/ui_sound_01.wav", False)
            self.view.enable_create_preset_button(False)
            self.view.log(f"\nCreating preset '{preset_name}' from: {self.model.verification_folder}")
            path = self.model._create_preset(preset_name)
            self.view.enable_create_preset_button(True)

        except Exception as e:
            self.view.log(f"[Error] {e}")

    def on_verify_clicked(self) -> None:
        try:
            preset_name = self.view.get_preset_name_input().strip()
            if not preset_name:
                self.view.play_sound("assets/audio/ui_sound_05.wav", False)
                self.view.log("[Error] Preset name is required.")
                return

            if not os.path.isdir(self.model.verification_folder):
                self.view.play_sound("assets/audio/ui_sound_05.wav", False)
                self.view.log("[Error] Verification folder is not set. Click 'Choose verification folder…' first.")
                return

            self.view.play_sound("assets/audio/ui_sound_01.wav", False)
            self.view.enable_create_preset_button(False)
            self.view.enable_verify_preset_button(False)
            self.view.log(f"Verifying hashes of {self.model.verification_folder} with preset '{preset_name}'")
            path = self.model._compare_hashes_with_preset(
                folder_files_and_hashes=self.model._get_hashes(),
                hashes_preset=self.model._load_preset("Example"),
                preset_name=preset_name)
            self.view.enable_create_preset_button(True)
            self.view.enable_verify_preset_button(True)

        except Exception as e:
            self.view.log(f"[Error] {e}")

    def on_folder_picked(self, folder_path: str | None) -> None:
        try:
            if not folder_path:
                self.view.play_sound("assets/audio/ui_sound_05.wav", False)
                self.view.log("[Info] Folder selection cancelled.")
                return

            self.model.set_verification_folder(folder_path)
            self.view.set_verification_folder_label(self.model.verification_folder)
            self.view.log(f"[OK] Verification folder set to: {self.model.verification_folder}\n")

        except Exception as e:
            self.view.log(f"[Error] {e}")

    def on_clear_log_clicked(self) -> None:
        self.view.play_sound("assets/audio/ui_sound_01.wav", False)
        self.view.clear_log()
# ===================================(END CALLBACKS)==================================



#====================================================================================
def main() -> None:
    model = Model(verification_folder="./verify", preset_folder="./presets")
    view = View()
    controller = Controller(model, view)

    view.build(
        on_action_clicked=controller.on_action_clicked,
        on_folder_picked=controller.on_folder_picked,
        on_verify_clicked=controller.on_verify_clicked,
        on_clear_log_clicked=controller.on_clear_log_clicked
    )

    # initial state
    view.set_verification_folder_label(model.verification_folder)

    view.start()


#====================================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
