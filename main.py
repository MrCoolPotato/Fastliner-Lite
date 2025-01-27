# main.py

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from UI.main_window import MainWindow

from UTILS.signals import SignalManager
from UTILS.config_manager import ConfigManager

from CORE.command_handler import CommandHandler

def main():

    config = ConfigManager.load_config()

    app = QApplication(sys.argv)

    font_name = ConfigManager.get("font", "Helvetica")
    ui_scale = ConfigManager.get("ui_scale", 1.0)
    font_scale = ConfigManager.get("font_scale", 14)

    base_font_size = int(font_scale * ui_scale)

    app.setFont(QFont(font_name, base_font_size))

    # Create and show our main window
    window = MainWindow()
    window.show()

    signals = SignalManager()
    
    cmd_handler = CommandHandler(main_window=window)
    
    signals.commandSignal.connect(cmd_handler.handle_command)
    signals.messageSignal.emit("Fastliner", "system")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()