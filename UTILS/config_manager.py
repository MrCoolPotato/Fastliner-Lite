# UTILS/config_manager.py
import json
import os

DEFAULT_CONFIG = {
    "shell_mode": False,
    "font": "Helvetica",
    "ui_scale": 1.0,
    "font_scale": 14,
    "input_placeholder": "~",
    "colors": {
        "text_general": "#282828", 
        "text_system": "#458588",
        "text_error": "#cc241d",   
        "text_success": "#98971a",
        "text_warning": "#d79921",
        "cli_widget_border_color": "white",
        "input_field_border_color": "white",
        "central_widget_border_color": "none",
        "cli_widget_color": "255, 255, 255, 1",
        "input_field_color": "255, 255, 255, 1",
        "central_widget_color": "255, 255, 255, 0.5"
    }
}

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  
    "..",                                      
    "STORE",                                    
    "config.json"
)

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