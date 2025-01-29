# main_window.py

from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)
from PySide6.QtCore import Qt, QPoint, QEvent

from UTILS.signals import SignalManager
from UTILS.color_manager import ColorManager
from UTILS.config_manager import ConfigManager

import asyncio

class MainWindow(QMainWindow):
    def __init__(self, ui_scale=1.0):
        super().__init__()
        self.setWindowTitle("Fastliner")

        self.ui_scale = ui_scale

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(750, 500)

        placeholder_text = ConfigManager.get("input_placeholder", "~")
        colors_config = ConfigManager.get("colors", {})
        default_color = colors_config.get("text_general", "#282828") 
        display_border_color = colors_config.get("cli_widget_border_color", "white")
        input_border_color = colors_config.get("input_field_border_color", "white")
        app_border_color = colors_config.get("central_widget_border_color", "none")
        display_color = colors_config.get("cli_widget_color", "255, 255, 255, 1")
        input_color = colors_config.get("input_field_color", "255, 255, 255, 1")
        app_color = colors_config.get("central_widget_color", "255, 255, 255, 0.5")

        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")

        scaled_radius = int(5 * ui_scale)
        scaled_radius_sharp = int(0 * ui_scale)

        central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: rgba({app_color});
                border-radius: {scaled_radius}px;
                border: 1px solid {app_border_color};
            }}
        """)

        # CLI text area
        self.cli_widget = QTextEdit()
        self.cli_widget.setReadOnly(True)
        self.cli_widget.setStyleSheet(f"""
            color: {default_color};
            background-color: rgba({display_color});
            border: 1px solid {display_border_color};
            border-radius: {scaled_radius}px;
            border-bottom-left-radius: {scaled_radius_sharp}px;
            border-bottom-right-radius: {scaled_radius_sharp}px;
            padding: {int(5 * ui_scale)}px;
        """)
        
        self.cli_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cli_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        
        self.input_field = QTextEdit()
        self.input_field.setStyleSheet(f"""
            background-color: rgba({input_color});
            color: {default_color};
            border: 1px solid {input_border_color};
            border-radius: {scaled_radius}px;
            padding: {int(5 * ui_scale)}px;
            border-top-left-radius: {scaled_radius_sharp}px;
            border-top-right-radius: {scaled_radius_sharp}px;

        """)
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        initial_height = int(30 * self.ui_scale)
        self.input_field.setFixedHeight(initial_height)
        self.input_field.textChanged.connect(self.adjust_input_height)
        self.input_field.setPlaceholderText(placeholder_text)
        self.input_field.installEventFilter(self)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.addWidget(self.cli_widget)
        layout.addWidget(self.input_field)
        self.setCentralWidget(central_widget)

        
        self.signals = SignalManager()
        self.setup_connections()

        self._drag_pos = QPoint()

    def setup_connections(self):
        self.signals.messageSignal.connect(self.append_text)

    def append_text(self, text: str, role: str = None):
        colorized_html = ColorManager.colorize(text, role=role)
        self.cli_widget.insertHtml(colorized_html + "<br>")

    def handle_user_input(self):
        user_text = self.input_field.toPlainText().strip()

        if user_text:
            if user_text.startswith("/"):
                parts = user_text.split()
                command = parts[0] if len(parts) > 0 else ""
                args = parts[1:] if len(parts) > 1 else []
                self.signals.commandSignal.emit(command, args)
            else:
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

    def eventFilter(self, obj, event):
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.handle_user_input()
                return True
        return super().eventFilter(obj, event)    

    def adjust_input_height(self):
        document_height = self.input_field.document().size().height()
        max_height = int(100 * self.ui_scale)
        self.input_field.setMaximumHeight(min(max_height, document_height + 10))  

    def closeEvent(self, event):
        self.signals.messageSignal.emit("Cleaning up resources...", "system")
        event.accept()
        asyncio.create_task(self.cleanup())

    async def cleanup(self):
        global matrix_client
        if matrix_client:
            await matrix_client.stop()      