# UTILS/config_manager.py
import json
import os
import sys

DEFAULT_CONFIG = {
    "homeserver": "http://matrix.fastliner.club:8008",
    "font": "SF Mono",
    "ui_scale": 1.0,
    "font_scale": 14,
    "input_placeholder": "~",
    "settings_width": 600,
    "settings_height": 500,
    "room_settings_width": 700,
    "room_settings_height": 500,
    "colors": {
        "text_general": "#282828", 
        "text_system": "#458588",
        "text_error": "#cc241d",   
        "text_success": "#98971a",
        "text_warning": "#d79921",
        "text_server": "#d65d0e",
        "text_debug": "#b16286",
        "cli_widget_border_color": "white",
        "input_field_border_color": "white",
        "central_widget_border_color": "none",
        "cli_widget_color": "255, 255, 255, 1",
        "input_field_color": "255, 255, 255, 1",
        "central_widget_color": "255, 255, 255, 0.5",
        "sidebar_splitter_color": "#282828",
        "sidebar_color": "255, 255, 255, 1",
        "sidebar_border_color": "white",
        "tree_background_color": "255, 255, 255, 1",
        "tree_color": "#282828",
        "tree_item_color": "#282828",
        "tree_item_selected_color": "255, 255, 255, 0.5",
        "tree_category_icon_color_closed": "255, 255, 255, 0.5",
        "tree_category_icon_color_open": "255, 255, 255, 0.5",
        "tree_item_hover_color": "255, 255, 255, 0.5",
        "tree_item_indentation_color": "255, 255, 255, 1.0",
        "tree_category_indentation_color": "255, 255, 255, 1.0",
        "settings_color": "255, 255, 255, 1.0",
        "settings_border_color": "white",
        "settings_text_color": "#282828",
        "room_settings_background_color": "255, 255, 255, 1.0",
        "room_settings_border_color": "white",
        "room_settings_text_color": "#282828"
    }
}

def _resources_dir():
    if getattr(sys, "frozen", False):
        macos_dir = os.path.dirname(sys.executable)
        return os.path.normpath(os.path.join(macos_dir, os.pardir, "Resources"))
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CONFIG_PATH = os.path.join(_resources_dir(), "STORE", "config.json")

class ConfigManager:
    _config_data = None

    @classmethod
    def load_config(cls):
        """
        Loads config from JSON or creates a new one if not found.
        """
        if cls._config_data is None:
            if not os.path.exists(CONFIG_PATH):
                # Create default config JSON if missing
                cls._config_data = DEFAULT_CONFIG.copy()
                cls.save_config()
            else:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    try:
                        cls._config_data = json.load(f)
                    except json.JSONDecodeError:
                        # If the file is invalid, start fresh
                        cls._config_data = DEFAULT_CONFIG.copy()
                        cls.save_config()
        return cls._config_data

    @classmethod
    def save_config(cls):
        """
        Writes the current config to JSON.
        """
        if cls._config_data is not None:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cls._config_data, f, indent=4)

    @classmethod
    def get(cls, key, default=None):
        """
        Get a config value by key.
        """
        data = cls.load_config()
        return data.get(key, default)

    @classmethod
    def set(cls, key, value):
        """
        Set a config value and persist.
        """
        data = cls.load_config()
        data[key] = value
        cls.save_config()

    @classmethod
    def restore_defaults(cls):
        """Resets the config data to DEFAULT_CONFIG and saves."""
        cls._config_data = DEFAULT_CONFIG.copy()
        cls.save_config()    