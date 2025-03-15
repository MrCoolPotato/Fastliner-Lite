from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QHBoxLayout
)
from PySide6.QtCore import Qt
import json

from UTILS.config_manager import ConfigManager
from UTILS.signals import SignalManager

class SettingsWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("App Settings")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)

        self.signals = SignalManager()

       
        ui_scale = ConfigManager.get("ui_scale", 1.0)
    
        settings_width = ConfigManager.get("settings_width", 600)
        settings_height = ConfigManager.get("settings_height", 500)

        base_radius = 5
        scaled_radius = int(base_radius * ui_scale)

        colors_config = ConfigManager.get("colors", {})
        settings_background_rgba = colors_config.get("settings_color", "255, 255, 255, 1.0")
        settings_border_color = colors_config.get("settings_border_color", "white")
        settings_text_color = colors_config.get("settings_text_color", "#282828")

        self.resize(settings_width, settings_height)

        self.setStyleSheet(f"""
            color: {settings_text_color};
            background-color: rgba({settings_background_rgba});
            border-radius: {scaled_radius}px;
            border: 1px solid {settings_border_color};
            padding: 5px;
        """)

        config_dict = ConfigManager.load_config()
        self.original_content = json.dumps(config_dict, indent=4)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        description_label = QLabel("Config contents (JSON):")
        main_layout.addWidget(description_label)

        self.json_editor = QPlainTextEdit()
        self.json_editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.json_editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.json_editor.setPlainText(self.original_content)
        main_layout.addWidget(self.json_editor)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.restore_button = QPushButton("Restore")
        self.reset_defaults_button = QPushButton("Reset Defaults")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.reset_defaults_button)
        main_layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_config)
        self.restore_button.clicked.connect(self.restore_config)
        self.reset_defaults_button.clicked.connect(self._reset_to_defaults)

    def save_config(self):
        new_content = self.json_editor.toPlainText()

        try:
            new_dict = json.loads(new_content)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return

        ConfigManager._config_data = new_dict
        ConfigManager.save_config()          
        self.signals.messageSignal.emit("Config saved.", "system")
        self.original_content = new_content
        self.close()

    def restore_config(self):
        self.json_editor.setPlainText(self.original_content)
        self.signals.messageSignal.emit("Restored to original.", "system")

    def _reset_to_defaults(self):
        ConfigManager.restore_defaults()
        default_data = ConfigManager.load_config()
        self.original_content = json.dumps(default_data, indent=4)
        self.json_editor.setPlainText(self.original_content)
        self.signals.messageSignal.emit("Reset to default config.", "system")