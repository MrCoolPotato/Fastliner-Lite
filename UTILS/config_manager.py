# UTILS/config_manager.py
import json
import os

DEFAULT_CONFIG = {
    "font": "Helvetica",
    "ui_scale": 1.0,
    "colors": {
        "text_general": "#000000",
        "text_system": "#0000FF",
        "text_error": "#FF0000"
    },
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