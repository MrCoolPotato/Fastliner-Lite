# main_window.py

from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
)
from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtWebEngineWidgets import QWebEngineView

from UTILS.signals import SignalManager
from UTILS.color_manager import ColorManager
from UTILS.config_manager import ConfigManager

import asyncio

class MainWindow(QMainWindow):
    def __init__(self, matrix_client, ui_scale=1.0):
        super().__init__()
        self.setWindowTitle("Fastliner") 

        self.current_room_id = None

        self.matrix_client = matrix_client

        self.ui_scale = ui_scale

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(750, 500)

        placeholder_text = ConfigManager.get("input_placeholder", "~")
        colors_config = ConfigManager.get("colors", {})
        sidebar_splitter_color = colors_config.get("sidebar_splitter_color", "#282828")
        sidebar_color = colors_config.get("sidebar_color", "255, 255, 255, 1")
        sidebar_border_color = colors_config.get("sidebar_border_color", "white")

        tree_background_color = colors_config.get("tree_background_color", "255, 255, 255, 1")
        tree_color = colors_config.get("tree_color", "#282828")
        tree_item_color = colors_config.get("tree_item_color", "#282828")
        tree_item_selected_color = colors_config.get("tree_item_selected_color", "255, 255, 255, 0.5")
        tree_category_icon_color_closed = colors_config.get("tree_category_icon_color_closed", "255, 255, 255, 0.5")
        tree_category_icon_color_open = colors_config.get("tree_category_icon_color_open", "255, 255, 255, 0.5")
        tree_item_hover_color = colors_config.get("tree_item_hover_color", "255, 255, 255, 0.5")
        tree_item_indentation_color = colors_config.get("tree_item_indentation_color", "255, 255, 255, 1.0")
        tree_category_indentation_color = colors_config.get("tree_category_indentation_color", "255, 255, 255, 1.0")

        default_color = colors_config.get("text_general", "#282828") 
        display_border_color = colors_config.get("cli_widget_border_color", "white")
        input_border_color = colors_config.get("input_field_border_color", "white")
        app_border_color = colors_config.get("central_widget_border_color", "none")
        display_color = colors_config.get("cli_widget_color", "255, 255, 255, 1")
        input_color = colors_config.get("input_field_color", "255, 255, 255, 1")
        app_color = colors_config.get("central_widget_color", "255, 255, 255, 0.5")

        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")

        scaled_radius = int(5 * ui_scale)
        scaled_radius_sharp = int(0 * ui_scale)

        self.central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: rgba({app_color});
                border-radius: {scaled_radius}px;
                border: 1px solid {app_border_color};
            }}
        """)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setVisible(False)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setStyleSheet(f"""
            QWidget#Sidebar {{
                background-color: rgba({sidebar_color});
                border-right: 1px solid {sidebar_border_color};
                border-top-left-radius: {scaled_radius}px;
                border-bottom-left-radius: {scaled_radius}px;
            }}
        """)

        self.tree = QTreeWidget(self.sidebar)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: rgba({tree_background_color});
                color: {tree_color};
                border: none;
                padding: 5px;
            }}
            QTreeWidget::item {{
                color: {tree_item_color};
                padding: 5px;
            }}
            QTreeWidget::item:selected {{
                background-color: rgba({tree_item_selected_color});
                border-radius: 5px;
            }}
            QTreeView::branch:closed:has-children {{
                background-color: rgba({tree_category_icon_color_closed});
                image: url("assets/fl_small_logo.png");
            }}
            QTreeView::branch:open:has-children {{
                background-color: rgba({tree_category_icon_color_open});
                image: url(assets/fl_small_logo.png);
            }}
            QTreeWidget::item:hover {{
                background-color: rgba({tree_item_hover_color});
            }}
            QTreeView::branch:selected {{
                background-color: rgba({tree_item_indentation_color});
            }}
            QTreeView::branch:has-children:selected {{
                background-color: rgba({tree_category_indentation_color});
            }}
        """)
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.addWidget(self.tree)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar.setLayout(sidebar_layout)

        # CallWidget
        self.callwidget = QWebEngineView()
        self.callwidget.setVisible(False)
        self.callwidget.setObjectName("CallWidget")
        self.callwidget.setStyleSheet(f"""
            QWidget#CallWidget {{
                background-color: rgba({sidebar_color});
                border-right: 1px solid {sidebar_border_color};
                border-top-left-radius: {scaled_radius}px;
                border-bottom-left-radius: {scaled_radius}px;
            }}
        """)

        # I/O Container: Wraps CLI Widget + Input Field
        self.io_container = QWidget()
        self.io_container.setObjectName("IOContainer")

        io_layout = QVBoxLayout(self.io_container)
        io_layout.setSpacing(0)
        io_layout.setContentsMargins(0, 0, 0, 0)

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

        # Input field
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

        io_layout.addWidget(self.cli_widget)
        io_layout.addWidget(self.input_field)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.io_container)
        self.splitter.addWidget(self.callwidget)
        self.splitter.setSizes([0, 1])
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: transparent;
                border: 1px solid {sidebar_splitter_color};
            }}
        """)
        self.splitter.setHandleWidth(0)

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.splitter)
        
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.signals = SignalManager()
        self.setup_connections()

        self._drag_pos = QPoint()

    def setup_connections(self):
        self.signals.messageSignal.connect(self.append_text)
        self.signals.roomSignal.connect(self.populate_sidebar)
        self.tree.itemClicked.connect(self.on_item_clicked)

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

    def toggle_sidebar(self):
    
        scaled_radius_sharp = int(0 * self.ui_scale)

        sizes = self.splitter.sizes()

        if sizes[0] == 0:
            self.splitter.setSizes([200, sizes[1]])
            self.cli_widget.setStyleSheet(self.cli_widget.styleSheet() + f"""
                border-top-left-radius: {scaled_radius_sharp}px;
            """)
            self.input_field.setStyleSheet(self.input_field.styleSheet() + f"""
                border-bottom-left-radius: {scaled_radius_sharp}px;
            """)
            self.sidebar.setVisible(True)
        else:
            self.splitter.setSizes([0, sizes[1]])
            self.cli_widget.setStyleSheet(self.cli_widget.styleSheet().replace(
                f"border-top-left-radius: {scaled_radius_sharp}px;", ""
            ))
            self.input_field.setStyleSheet(self.input_field.styleSheet().replace(
                f"border-bottom-left-radius: {scaled_radius_sharp}px;", ""
            ))
            self.sidebar.setVisible(False)      

    def toggle_callwidget(self):
    
        scaled_radius_sharp = int(0 * self.ui_scale)

        sizes = self.splitter.sizes()

        if sizes[2] == 0:
            self.splitter.setSizes([sizes[0], sizes[1], 500])
            self.cli_widget.setStyleSheet(self.cli_widget.styleSheet() + f"""
                border-top-right-radius: {scaled_radius_sharp}px;
            """)
            self.input_field.setStyleSheet(self.input_field.styleSheet() + f"""
                border-bottom-right-radius: {scaled_radius_sharp}px;
            """)
            self.callwidget.setUrl("https://www.google.com")
            self.callwidget.setVisible(True)
        else:
            self.splitter.setSizes([sizes[0], sizes[1], 0])
            self.cli_widget.setStyleSheet(self.cli_widget.styleSheet().replace(
                f"border-top-right-radius: {scaled_radius_sharp}px;", ""
            ))
            self.input_field.setStyleSheet(self.input_field.styleSheet().replace(
                f"border-bottom-right-radius: {scaled_radius_sharp}px;", ""
            ))
            self.callwidget.setVisible(False)  
            self.callwidget.setUrl("about:blank")
            self.callwidget.page().profile().clearHttpCache()     

    def populate_sidebar(self, room_details):
        # Clear any existing items
        self.tree.clear()

        # Separate spaces and standalone rooms
        spaces = {}
        standalone_rooms = []

        for room in room_details:
            if room.get("is_space"):
                spaces[room["room_id"]] = room
            else:
                standalone_rooms.append(room)

        # Process spaces and add their children if present
        for space_id, space in spaces.items():
            # Use the room's name if available, else fallback to its id.
            display_name = space.get("name", space_id)
            space_item = QTreeWidgetItem(self.tree, [f"─ {display_name}"])
            # Save the room id in the item data.
            space_item.setData(0, Qt.UserRole, space_id)

            # Get children if any; each child is expected to be a dictionary with keys 'room_id' and 'name'
            children = space.get("children", [])
            for child in children:
                child_display_name = child.get("name", child.get("room_id", "Unknown"))
                child_item = QTreeWidgetItem(space_item, [f"└ {child_display_name}"])
                # Save the child room id in the item data.
                child_item.setData(0, Qt.UserRole, child.get("room_id"))
            space_item.setExpanded(True)

        # Process standalone rooms
        for room in standalone_rooms:
            display_name = room.get("name", room.get("room_id"))
            room_item = QTreeWidgetItem(self.tree, [display_name])
            room_item.setData(0, Qt.UserRole, room.get("room_id"))

        # Refresh the UI
        self.tree.repaint()

    def on_item_clicked(self, item, column):
        # Retrieve the stored room ID from the clicked item
        room_id = item.data(0, Qt.UserRole)
        if room_id:
            # If this room is already open, do not fetch the context again.
            if self.current_room_id == room_id:
                self.signals.messageSignal.emit(f"Room {room_id} is already open.", "system")
                return
            # Update the current room and fetch its context
            self.current_room_id = room_id
            self.signals.messageSignal.emit(f"Fetching context for room: {room_id}", "system")
            asyncio.create_task(self.matrix_client.fetch_room_messages(room_id))
        else:
            self.signals.messageSignal.emit("No room id found for the selected item.", "error")       

    def closeEvent(self, event):
        self.signals.messageSignal.emit("Cleaning up resources...", "system")
        event.accept()
        asyncio.create_task(self.cleanup())

    async def cleanup(self):
        global matrix_client
        if matrix_client:
            await matrix_client.stop()