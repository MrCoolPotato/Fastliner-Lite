# CORE/command_handler.py

from PySide6.QtCore import QObject

from UTILS.signals import SignalManager

from UI.settings_window import SettingsWindow

from CORE.matrix_client import MatrixClient

import platform, os

import asyncio

class CommandHandler(QObject):
    def __init__(self, main_window=None, parent=None, matrix_client=None):
        super().__init__(parent)
        self.signals = SignalManager()
        
        self.settings_window = None
        
        self.main_window = main_window

        self.matrix_client = matrix_client
        
        self.logged_in = False

    def handle_command(self, command: str, args: list):
        
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
                "  -\n"
                "  /login <username> <password>\n"
                "  /logout\n"
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

        elif cmd_lower == "/login":
            if len(args) != 2:
                self.signals.messageSignal.emit("Usage: /login <username> <password>", "warning")
            else:
                username, password = args
                self.signals.messageSignal.emit(f"Logging in as {username}...", "system")
                asyncio.create_task(self._handle_login(username, password))  

        elif cmd_lower == "/logout":
            asyncio.create_task(self._handle_logout())        

        else:
            self.signals.messageSignal.emit(f"Unknown command: {command}", "error")

    async def _handle_login(self, username: str, password: str):

        success = await self.matrix_client.login(username, password)
        if success:
            self.logged_in = True
            self.signals.messageSignal.emit("Login successful.", "success")
        else:
            self.logged_in = False
            self.signals.messageSignal.emit("Login failed. Check your credentials.", "error")

    async def _handle_logout(self):

        success = await self.matrix_client.logout()
        if success:
            self.logged_in = False
            self.signals.messageSignal.emit("Logout successful.", "success")
        else:
            self.signals.messageSignal.emit("Logout failed.", "error")                

    def _handle_settings(self):\
    
        if self.settings_window is None or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow()
            self.settings_window.show()
        else:
            self.settings_window.activateWindow()

    def _handle_exit(self):

        if self.main_window:
            self.signals.messageSignal.emit("Exiting application...", "success")
            self.main_window.close()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot exit.", "error")

    def _handle_minimize(self):
        
        if self.main_window:
            self.signals.messageSignal.emit("Minimizing window...", "success")
            self.main_window.showMinimized()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot minimize.", "error")

    def _handle_fullscreen(self):

        if self.main_window:
            if self.main_window.isFullScreen():
                self.signals.messageSignal.emit("Restoring window from fullscreen...", "success")
                self.main_window.showNormal()
            else:
                self.signals.messageSignal.emit("Entering fullscreen mode...", "success")
                self.main_window.showFullScreen()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot fullscreen.", "error")

    def _handle_clear(self):

        if platform.system().lower().startswith("win"):
            os.system("cls")
        else:
            os.system("clear")

        if self.main_window and hasattr(self.main_window, "cli_widget"):
            self.main_window.cli_widget.clear()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot clear local screen.", "error")        