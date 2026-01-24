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
    clear_log_btn: int


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
        on_clear_log_clicked: Callable[[], None],
    ) -> None:
        dpg.create_context()
        dpg.create_viewport(title="(H.I.T.) - Hash Integrity Tool", width=976, height=535)

        with dpg.texture_registry(show=False):
            width, height, channels, data = dpg.load_image("assets/images/bg.png")
            dpg.add_static_texture(width, height, data, tag="background_texture")

        with dpg.window(tag="background_window", no_title_bar=True, no_move=True, no_resize=True, no_scrollbar=True,
                        no_collapse=True, no_close=True, pos=(-8, -8), width=980, height=520):
            dpg.add_image("background_texture", tag="background_image")

        dpg.set_viewport_small_icon("assets/images/CompanyLogo.ico")
        dpg.set_viewport_large_icon("assets/images/CompanyLogo.ico")



        # === Red Button Highlight Theme ===
        with dpg.theme() as red_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (150, 0, 0, 255))  # Dark red hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (200, 0, 0, 255))  # Bright red active
        # === Red Combo Highlight Theme ===
        with dpg.theme() as red_combo_theme:
            with dpg.theme() as red_combo_theme:
                with dpg.theme_component(dpg.mvAll):
                    # popup background + border (dropdown)
                    dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (15, 15, 15, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_Border, (120, 0, 0, 255))

                    # hovered item background in lists/combos
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (150, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (200, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_Header, (90, 0, 0, 255))

                    # this is the BLUE you’re seeing (keyboard/gamepad nav highlight)
                    dpg.add_theme_color(dpg.mvThemeCol_NavHighlight, (150, 0, 0, 255))

                    # sometimes selection uses this too
                    dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (150, 0, 0, 140))

                # combo frame + arrow
                with dpg.theme_component(dpg.mvCombo):
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (40, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (60, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (150, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (200, 0, 0, 255))

            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (150, 0, 0, 255))  # hover on the combo box
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (200, 0, 0, 255))  # when clicked/open
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (150, 0, 0, 255))  # arrow hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (200, 0, 0, 255))  # arrow active
        # === Transparent Theme ===
        with dpg.theme() as transparent_theme:
            with dpg.theme_component(0):  # mvAll
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (0, 0, 0))
        # === Transparent Log Theme ===
        with dpg.theme() as transparent_log_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0))
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0))

        pygame.mixer.init()
        dpg.bind_item_theme("background_window", transparent_theme)

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

        with dpg.window(tag="primary", label="B.A.D. - H.I.T.", width=957, height=620, pos=[1.9,0], no_close=True):
            dpg.add_separator()
            dpg.bind_item_theme("primary", transparent_theme)

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
                dpg.bind_item_theme(presets_combo, red_combo_theme)

                dpg.add_spacer(width=10)

                choose_folder_btn = dpg.add_button(
                    label="Choose verification folder…",
                    width=260,
                    callback=lambda: on_folder_picked(self._select_verification_folder_windows())
                )
                dpg.bind_item_theme(choose_folder_btn, red_button_theme)

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
                dpg.bind_item_theme(action_btn, red_button_theme)
                dpg.add_spacer(width=10)
                verify_btn = dpg.add_button(label="Verify", width=180, callback=lambda: on_verify_clicked())
                dpg.bind_item_theme(verify_btn, red_button_theme)
                clear_log_btn = dpg.add_button(label='Clear Log', width=180, callback=lambda: on_clear_log_clicked())
                dpg.bind_item_theme(clear_log_btn, red_button_theme)

            dpg.add_separator()
            dpg.add_text("Output:")

            with dpg.child_window(tag="log_child",height=360, horizontal_scrollbar=True):
                log_box = dpg.add_input_text(
                    multiline=True,
                    readonly=True,
                    width=-1,
                    height=-1,
                    no_horizontal_scroll=False,
                )
            dpg.bind_item_theme("log_child", transparent_log_theme)
            dpg.bind_item_theme(log_box, transparent_log_theme)

        self.handles = ViewHandles(
            preset_name_input=preset_name_input,
            choose_folder_btn=choose_folder_btn,
            presets_combo=presets_combo,
            current_folder_text=current_folder_text,
            action_btn=action_btn,
            verify_btn=verify_btn,
            clear_log_btn=clear_log_btn,
            log_box=log_box,
            folder_dialog=0,
        )

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("background_window", True)


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

    def enable_clear_log_button(self, enabled: bool) -> None:
        assert self.handles is not None
        dpg.configure_item(self.handles.clear_log_btn, enabled=enabled)

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
