# CORE/command_handler.py

from PySide6.QtCore import QObject
from UTILS.signals import SignalManager
from UI.settings_window import SettingsWindow
import platform, os

class CommandHandler(QObject):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.signals = SignalManager()
        
        self.settings_window = None
        
        self.main_window = main_window
        
        self.logged_in = not False

    def handle_command(self, command: str, args: list):
        """
        Dispatch commands to appropriate actions.
        """
        cmd_lower = command.lower()

        if cmd_lower == "/help":
            self.signals.messageSignal.emit((
                "Available commands:\n"
                "  /help\n"
                "  /settings\n"
                "  /exit\n"
                "  /minimize\n"
                "  /fullscreen\n"
                "  /clear\n"
                "  ..."
            ), "system")

        elif cmd_lower == "/settings":
            if not self.logged_in:
                self.signals.messageSignal.emit("You are not logged in.", "warning")
            else:
                self._handle_settings()

        elif cmd_lower == "/exit":
            self._handle_exit()

        elif cmd_lower == "/minimize":
            self._handle_minimize()

        elif cmd_lower == "/fullscreen":
            self._handle_fullscreen()

        elif cmd_lower == "/clear":
            self._handle_clear()   

        else:
            self.signals.messageSignal.emit(f"Unknown command: {command}", "error")

    def _handle_settings(self):
        """
        Show the settings window as a popup dialog.
        """
        if self.settings_window is None or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow()
            self.settings_window.show()
        else:
            # Bring it to the foreground if already open
            self.settings_window.activateWindow()

    def _handle_exit(self):
        """
        Closes the main application window, effectively exiting the app.
        """
        if self.main_window:
            self.signals.messageSignal.emit("Exiting application...", "success")
            self.main_window.close()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot exit.", "error")

    def _handle_minimize(self):
        """
        Minimizes the main window.
        """
        if self.main_window:
            self.signals.messageSignal.emit("Minimizing window...", "success")
            self.main_window.showMinimized()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot minimize.", "error")

    def _handle_fullscreen(self):
        """
        Toggles or sets the main window to fullscreen.
        """
        if self.main_window:
            # If already fullscreen, return to normal; otherwise go fullscreen.
            if self.main_window.isFullScreen():
                self.signals.messageSignal.emit("Restoring window from fullscreen...", "success")
                self.main_window.showNormal()
            else:
                self.signals.messageSignal.emit("Entering fullscreen mode...", "success")
                self.main_window.showFullScreen()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot fullscreen.", "error")

    def _handle_clear(self):
        """
        Clears the console (OS-level) and the in-app text area.
        """

        # 1) OS-level clear (helpful if the app is run in a real console)
        if platform.system().lower().startswith("win"):
            # Windows
            os.system("cls")
        else:
            # macOS, Linux, etc.
            os.system("clear")

        # 2) Clear the Qt "CLI" text area, if we have a reference to the main window
        if self.main_window and hasattr(self.main_window, "cli_widget"):
            self.main_window.cli_widget.clear()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot clear local screen.", "error")        