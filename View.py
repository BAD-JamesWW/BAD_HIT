from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import dearpygui.dearpygui as dpg
import os
import tkinter as tk
from tkinter import filedialog


@dataclass
class ViewHandles:
    preset_name_input: int
    choose_folder_btn: int
    current_folder_text: int
    action_btn: int
    log_box: int
    folder_dialog: int


class View:
    """DearPyGUI view. Pure UI; no business logic."""

    def __init__(self) -> None:
        self.handles: Optional[ViewHandles] = None

    # --- Windows native folder picker (tkinter) ---
    def _select_verification_folder_windows(self) -> str | None:
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

    def build(
        self,
        on_action_clicked: Callable[[], None],
        on_folder_picked: Callable[[str | None], None],
    ) -> None:
        dpg.create_context()
        dpg.create_viewport(title="HIT — Hash Integrity Tool (B.A.D.)", width=980, height=640)

        with dpg.window(tag="primary", label="HIT", width=960, height=620):
            dpg.add_text("HIT — Hash Integrity Tool")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_text("Mode: Create preset")

            with dpg.group(horizontal=True):
                dpg.add_text("Preset name:")
                preset_name_input = dpg.add_input_text(width=260, hint="Example")

                dpg.add_spacer(width=20)

                choose_folder_btn = dpg.add_button(
                    label="Choose verification folder…",
                    width=260,
                    callback=lambda: on_folder_picked(self._select_verification_folder_windows())
                )

            current_folder_text = dpg.add_text("Verification folder: (not set)")

            with dpg.group(horizontal=True):
                action_btn = dpg.add_button(label="Create preset", width=180, callback=lambda: on_action_clicked())

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
            current_folder_text=current_folder_text,
            action_btn=action_btn,
            log_box=log_box,
            folder_dialog=0,  # no longer using dpg file dialog
        )

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("primary", True)

    # ----------------------------
    # UI helpers
    # ----------------------------
    def start(self) -> None:
        dpg.start_dearpygui()
        dpg.destroy_context()

    def get_mode(self) -> str:
        return "Create preset"

    def get_preset_name_input(self) -> str:
        assert self.handles is not None
        return dpg.get_value(self.handles.preset_name_input)

    def get_selected_preset(self) -> str:
        return ""

    def set_presets(self, presets: list[str]) -> None:
        return

    def set_verification_folder_label(self, folder: str) -> None:
        assert self.handles is not None
        dpg.set_value(self.handles.current_folder_text, f"Verification folder: {folder}")

    def set_action_button_label(self, label: str) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.action_btn, label=label)

    def enable_preset_name(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.preset_name_input, enabled=enabled)

    def enable_preset_select(self, enabled: bool) -> None:
        return

    def enable_folder_button(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.choose_folder_btn, enabled=enabled)

    def enable_create_preset_button(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.action_btn, enabled=enabled)

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
