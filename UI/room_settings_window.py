from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QSizePolicy,
    QHeaderView,
)
from PySide6.QtCore import Qt
import asyncio

class RoomSettingsWindow(QDialog):
    def __init__(self, room_id: str, matrix_client, parent=None):
        super().__init__(parent)
        self.room_id = room_id
        self.matrix_client = matrix_client
        self.original_power_levels = {}  # Will store the originally fetched flattened power levels.
        self.setWindowTitle("Room Settings")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setStyleSheet(f"""
            color: #282828;
            background-color: rgba(255, 255, 255, 1.0);
            border-radius: 1px;
            border: 1px solid white;
            padding: 0px;
        """)
        self.resize(700, 500)

        layout = QVBoxLayout(self)
        # Optionally, add layout margins if needed:
        layout.setContentsMargins(5, 5, 5, 5)

        # Table for displaying power levels as a list
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Power", "Level"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, stretch=1)

        self.save_button = QPushButton("Save")
        self.save_button.setVisible(False)
        
        self.restore_button = QPushButton("Restore")
        self.restore_button.setVisible(False)
        
        from PySide6.QtWidgets import QHBoxLayout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.restore_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons signals.
        self.save_button.clicked.connect(self.on_save_clicked)
        self.restore_button.clicked.connect(self.on_restore_clicked)

        # Load current power levels asynchronously.
        asyncio.create_task(self.load_power_levels())

    async def load_power_levels(self):
        # Get the full power levels state for the room.
        result = await self.matrix_client.get_room_power_levels(self.room_id)
        if result.get("status") == "success":
            content = result.get("content", {})
            # Flatten nested power level properties for display.
            power_levels = self.flatten_power_levels(content)
            # Store original fetched data.
            self.original_power_levels = power_levels.copy()
            self.populate_table(power_levels)
        else:
            self.populate_table({"error": "Error loading power levels"})

    def flatten_power_levels(self, content: dict) -> dict:
        flattened = {}
        for key, value in content.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    flattened[f"{key}.{subkey}"] = subvalue
            else:
                flattened[key] = value
        return flattened

    def populate_table(self, power_levels: dict):
        self.table.setRowCount(len(power_levels))
        for row, (prop, val) in enumerate(power_levels.items()):
            prop_item = QTableWidgetItem(str(prop))
            # Make property name read-only and left-aligned.
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemIsEditable)
            prop_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 0, prop_item)

            val_item = QTableWidgetItem(str(val))
            val_item.setFlags(val_item.flags() | Qt.ItemIsEditable)
            # Center the value.
            val_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, val_item)

        # Resize columns: left column resizes to contents, right column stretches.
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Show Save and Restore buttons if there is at least one row.
        if self.table.rowCount() > 0:
            self.save_button.setVisible(True)
            self.restore_button.setVisible(True)

    def on_save_clicked(self):
        # Collect updated power levels from the table.
        new_power_levels = {}
        for row in range(self.table.rowCount()):
            prop = self.table.item(row, 0).text()
            val_text = self.table.item(row, 1).text()
            try:
                # Try to convert to an integer.
                val = int(val_text)
            except ValueError:
                self.signals.messageSignal.emit(
                    f"Illegal value in row {row+1}: '{val_text}' is not a number.", "error"
                )
                return

            # Check if the value is within the legal range.
            if val < 0 or val > 100:
                self.signals.messageSignal.emit(
                    f"Illegal power level in row {row+1}: {val} is not between 0 and 100.", "error"
                )
                return

            # For nested properties like "users.default", split into parent and child.
            if '.' in prop:
                parent, child = prop.split('.', 1)
                if parent not in new_power_levels:
                    new_power_levels[parent] = {}
                new_power_levels[parent][child] = val
            else:
                new_power_levels[prop] = val
        
        # Send the new power levels via the matrix client.
        asyncio.create_task(self.matrix_client.update_room_power_levels(self.room_id, new_power_levels))
        self.save_button.setVisible(False)
        self.restore_button.setVisible(False)
        self.close()

    def on_restore_clicked(self):
        # Restore the table with the original power levels.
        self.populate_table(self.original_power_levels)