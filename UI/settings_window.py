from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

#from UTILS.config_manager import ConfigManager TODO connect cconfigs

class SettingsWindow(QDialog):
   
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("App Settings")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)

        #TODO settings color.
        #TODO settings scaling.

        self.setStyleSheet(f"""
            color: #282828;
            background-color: rgba(255, 255, 255, 1.0);
            border-radius: 5px;
            border: 1px solid white;
            padding: 5px;
        """)

        self.resize(400, 250)

        layout = QVBoxLayout()
        
        # Main heading
        layout.addWidget(QLabel("Settings:"))
        
        # New settings options
        layout.addWidget(QLabel("Account"))
        layout.addWidget(QLabel("Preferences"))
        layout.addWidget(QLabel("Appearance"))
        layout.addWidget(QLabel("Security"))
        layout.addWidget(QLabel("Notifications"))
        layout.addWidget(QLabel("Advanced"))

        self.setLayout(layout)