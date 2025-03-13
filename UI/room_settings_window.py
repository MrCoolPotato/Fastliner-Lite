from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QHBoxLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt
from UTILS.signals import SignalManager
import asyncio
import json

class RoomSettingsWindow(QDialog):
    def __init__(self, room_id: str, matrix_client, parent=None):
        super().__init__(parent)
        self.room_id = room_id
        self.matrix_client = matrix_client
        self.signals = SignalManager()
        self.original_power_levels = {}

        self.setWindowTitle("Room Settings")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setStyleSheet("""
            color: #282828;
            background-color: rgba(255, 255, 255, 1.0);
            border-radius: 1px;
            border: 1px solid white;
            padding: 5px;
        """)
        self.resize(700, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(QLabel("Room Power Levels (raw JSON):"))

        self.text_edit = QPlainTextEdit()
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.text_edit, stretch=1)

        self.save_button = QPushButton("Save")
        self.restore_button = QPushButton("Restore")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.restore_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.save_button.clicked.connect(self.on_save_clicked)
        self.restore_button.clicked.connect(self.on_restore_clicked)

        asyncio.create_task(self.load_power_levels())

    async def load_power_levels(self):
        result = await self.matrix_client.get_room_power_levels(self.room_id)
        if result.get("status") == "success":
            self.original_power_levels = result.get("content", {})
            pretty = json.dumps(self.original_power_levels, indent=4)
            self.text_edit.setPlainText(pretty)
            self.save_button.setVisible(True)
            self.restore_button.setVisible(True)
        else:
            self.text_edit.setPlainText("Error loading power levels")

    def on_save_clicked(self):
        try:
            new_json = json.loads(self.text_edit.toPlainText())
        except Exception as e:
            self.signals.messageSignal.emit(f"Invalid JSON: {e}", "error")
            return
        self.signals.messageSignal.emit(f"New raw power levels at save: {json.dumps(new_json)}", "debug")
        asyncio.create_task(self.matrix_client.update_room_power_levels(self.room_id, new_json))
        self.save_button.setVisible(False)
        self.restore_button.setVisible(False)
        self.close()

    def on_restore_clicked(self):
        pretty = json.dumps(self.original_power_levels, indent=4)
        self.text_edit.setPlainText(pretty)