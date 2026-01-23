from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
import dearpygui.dearpygui as dpg
import os
import tkinter as tk
from tkinter import filedialog
import pygame


#====================================================================================
@dataclass
class ViewHandles:
    preset_name_input: int
    choose_folder_btn: int
    presets_combo: int
    current_folder_text: int
    action_btn: int
    verify_btn: int
    log_box: int
    folder_dialog: int


class View:
    """DearPyGUI view. Pure UI; no business logic."""

    # ====================================================================================
    def __init__(self) -> None:
        self.handles: Optional[ViewHandles] = None

    # ====================================================================================
    def _select_verification_folder_windows(self) -> str | None:
        self.play_sound("assets/audio/ui_sound_02.wav", wait=False)
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        selected = filedialog.askdirectory(
            title="Select folder to VERIFY",
            initialdir=os.getcwd()
        )

        root.destroy()

        if not selected:
            return None

        return os.path.abspath(selected)

    # ====================================================================================
    def build(
        self,
        on_action_clicked: Callable[[], None],
        on_verify_clicked: Callable[[], None],
        on_folder_picked: Callable[[str | None], None],
    ) -> None:
        dpg.create_context()
        dpg.create_viewport(title="(H.I.T.) - Hash Integrity Tool", width=980, height=520)
        dpg.set_viewport_small_icon("assets/images/CompanyLogo.ico")
        dpg.set_viewport_large_icon("assets/images/CompanyLogo.ico")

        pygame.mixer.init()

        # resolve presets directory robustly
        script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
        presets_dir_script = os.path.join(script_dir, "presets")
        presets_dir_cwd = os.path.abspath("./presets")

        def _get_presets_dir() -> str:
            if os.path.isdir(presets_dir_script):
                return presets_dir_script
            return presets_dir_cwd

        def _list_preset_files() -> list[str]:
            preset_dir = _get_presets_dir()
            if not os.path.isdir(preset_dir):
                return []
            return sorted([n for n in os.listdir(preset_dir) if n.lower().endswith(".json")])

        with dpg.window(tag="primary", label="HIT", width=960, height=620):
            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_text("Preset name:")
                preset_name_input = dpg.add_input_text(width=260, hint="Example")

                dpg.add_spacer(width=20)

                # --- presets dropdown (combo) ---
                presets_combo = dpg.add_combo(
                    items=_list_preset_files() or ["(no presets found)"],
                    width=260,
                    label="",
                    callback=lambda s, a: _on_preset_chosen(self, a, preset_name_input)  # FIX
                )

                dpg.add_spacer(width=10)

                choose_folder_btn = dpg.add_button(
                    label="Choose verification folder…",
                    width=260,
                    callback=lambda: on_folder_picked(self._select_verification_folder_windows())
                )

                # Refresh preset list when the user hovers the dropdown (covers arrow-click too)
                with dpg.item_handler_registry(tag="presets_combo_handlers"):
                    dpg.add_item_hover_handler(
                        callback=lambda: dpg.configure_item(
                            presets_combo,
                            items=_list_preset_files() or ["(no presets found)"]
                        )
                    )
                dpg.bind_item_handler_registry(presets_combo, "presets_combo_handlers")

            current_folder_text = dpg.add_text("Verification folder: (not set)")

            # Buttons row: Create preset + Verify (side-by-side)
            with dpg.group(horizontal=True):
                action_btn = dpg.add_button(label="Create preset", width=180, callback=lambda: on_action_clicked())
                dpg.add_spacer(width=10)
                verify_btn = dpg.add_button(label="Verify", width=180, callback=lambda: on_verify_clicked())

            dpg.add_separator()
            dpg.add_text("Output:")

            with dpg.child_window(height=360, horizontal_scrollbar=True):
                log_box = dpg.add_input_text(
                    multiline=True,
                    readonly=True,
                    width=-1,
                    height=-1,
                    no_horizontal_scroll=False,
                )

        self.handles = ViewHandles(
            preset_name_input=preset_name_input,
            choose_folder_btn=choose_folder_btn,
            presets_combo=presets_combo,
            current_folder_text=current_folder_text,
            action_btn=action_btn,
            verify_btn=verify_btn,
            log_box=log_box,
            folder_dialog=0,
        )

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("primary", True)

    # ===============================(UI HELPERS)=========================================
    def start(self) -> None:
        dpg.start_dearpygui()
        dpg.destroy_context()

    def get_mode(self) -> str:
        return "Create preset"

    def get_preset_name_input(self) -> str:
        assert self.handles is not None
        return dpg.get_value(self.handles.preset_name_input)

    def set_verification_folder_label(self, folder: str) -> None:
        assert self.handles is not None
        dpg.set_value(self.handles.current_folder_text, f"Verification folder: {folder}")

    def enable_folder_button(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.choose_folder_btn, enabled=enabled)

    def enable_create_preset_button(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.action_btn, enabled=enabled)

    def enable_verify_button(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.verify_btn, enabled=enabled)

    def log(self, msg: str, *, newline: bool = True) -> None:
        assert self.handles is not None
        current = dpg.get_value(self.handles.log_box) or ""
        if newline and current:
            current += "\n"
        current += msg
        dpg.set_value(self.handles.log_box, current)

    def clear_log(self) -> None:
        assert self.handles is not None
        dpg.set_value(self.handles.log_box, "")

    def play_sound(self, filename: str, wait: bool = True) -> None:
        path = os.path.abspath(filename)
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            print(f"[Sound Error] File missing or empty: {path}")
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            if wait:
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(30)
        except Exception as e:
            print("Audio playback failed:", e)


# --- helper for combo selection ---
def _on_preset_chosen(view: View, selected_value: str, preset_name_input_id: int) -> None:
    view.play_sound("assets/audio/ui_sound_01.wav", wait=False)
    if not selected_value or str(selected_value).startswith("("):
        return

    name = os.path.splitext(str(selected_value))[0]
    if name.startswith("hashes_preset_"):
        name = name[len("hashes_preset_"):]
    dpg.set_value(preset_name_input_id, name)
