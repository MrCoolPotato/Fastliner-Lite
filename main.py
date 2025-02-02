# main.py

import sys
import asyncio
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from PySide6.QtGui import QFont

from UI.main_window import MainWindow
from UTILS.signals import SignalManager
from UTILS.config_manager import ConfigManager
from CORE.command_handler import CommandHandler
from CORE.matrix_client import MatrixClient

if __name__ == "__main__":

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    try:
        config = ConfigManager.load_config()
        font_name = ConfigManager.get("font", "Helvetica")
        ui_scale = ConfigManager.get("ui_scale", 1.0)
        font_scale = ConfigManager.get("font_scale", 14)
        base_font_size = int(font_scale * ui_scale)
        app.setFont(QFont(font_name, base_font_size))
        signals = SignalManager()
        matrix_client = MatrixClient(signals)
        window = MainWindow(matrix_client=matrix_client)
        window.show()
        cmd_handler = CommandHandler(main_window=window, matrix_client=matrix_client)
        signals.commandSignal.connect(cmd_handler.handle_command)
        signals.messageSignal.emit("Fastliner is ready.", "system")

        with loop:
            try:
                loop.run_forever()
            except (KeyboardInterrupt, SystemExit):
                print("Exiting Fastliner...")
                loop.run_until_complete(matrix_client.stop())
            finally:
                print("Shutting down...")
                loop.close()

    except Exception as e:
        print(f"Critical error during app startup: {e}")
        sys.exit(1)