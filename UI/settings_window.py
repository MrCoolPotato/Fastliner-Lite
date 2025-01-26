from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

class SettingsWindow(QDialog):
    """
    Popup dialog for configuring application settings.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("App Settings")

        layout = QVBoxLayout()
        
        # Main heading
        layout.addWidget(QLabel("Settings:"))
        
        # New settings options
        layout.addWidget(QLabel("Account"))
        layout.addWidget(QLabel("Preferences"))
        layout.addWidget(QLabel("Appearance"))
        layout.addWidget(QLabel("Security"))
        layout.addWidget(QLabel("Notifications"))

        self.setLayout(layout)