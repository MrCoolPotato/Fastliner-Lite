# main_window.py

from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt, QPoint
from UTILS.signals import SignalManager
from UTILS.color_manager import ColorManager

class MainWindow(QMainWindow):
    def __init__(self, ui_scale=1.0):
        super().__init__()
        self.setWindowTitle("Fastliner")

        # 1. Remove the default window frame and allow background transparency
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(750, 500)

        # 2. Set up the central container with a scaled, rounded-corner background
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")

        scaled_radius = int(5 * ui_scale)

        central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: rgba(245, 245, 245, 0.8);
                border-radius: {scaled_radius}px;
            }}
        """)

        # CLI text area
        self.cli_widget = QTextEdit()
        self.cli_widget.setReadOnly(True)
        self.cli_widget.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 1);
            color: #333;
            border: 1px solid #ccc;
            border-radius: {scaled_radius}px;
        """)
        # Turn off scrollbars
        self.cli_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cli_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # User input field
        self.input_field = QLineEdit()
        self.input_field.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 1);
            color: #333;
            border: 1px solid #ccc;
            border-radius: {scaled_radius}px;
            padding: {int(5 * ui_scale)}px;
        """)
        self.input_field.returnPressed.connect(self.handle_user_input)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.cli_widget)
        layout.addWidget(self.input_field)
        self.setCentralWidget(central_widget)

        # Connect to our signal manager
        self.signals = SignalManager()
        self.setup_connections()

        # Track the last known cursor position for dragging
        self._drag_pos = QPoint()

    def setup_connections(self):
        """
        Connect signals from the singleton signal manager to local methods.
        """
        self.signals.messageSignal.connect(self.append_text)

    def append_text(self, text: str, role: str = None):
        colorized_html = ColorManager.colorize(text, role=role)
        self.cli_widget.insertHtml(colorized_html + "<br>")

    def handle_user_input(self):
        user_text = self.input_field.text().strip()
        if user_text:
            if user_text.startswith("/"):
                # Command mode: keep the slash in the first token
                parts = user_text.split()
                command = parts[0] if len(parts) > 0 else ""
                args = parts[1:] if len(parts) > 1 else []
                self.signals.commandSignal.emit(command, args)
            else:
                # Message mode: just emit as a plain text message
                self.signals.messageSignal.emit(user_text, "user")
        self.input_field.clear()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            diff = event.globalPosition().toPoint() - self._drag_pos
            new_pos = self.pos() + diff
            self.move(new_pos)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()