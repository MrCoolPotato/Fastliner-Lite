
"""
def show_register(self):
       
        target_shape = random.choice(["square", "circle", "triangle"])
        target_color = random.choice(["orange", "yellow", "green"])
        bot_game = BotGame(target_shape, target_color)
        if bot_game.exec() == QDialog.Accepted:
            # Proceed to registration dialog only if the bot game is successful
            self.register_dialog = RegisterDialog()
            self.register_dialog.setWindowModality(Qt.ApplicationModal)
            self.register_dialog.show()
        else:
            QMessageBox.warning(self, "Access Denied", "Please pass the bot check to continue.")


from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QMessageBox
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt, QSize, QPoint
import random


class ShapeWidget(QLabel):

    def __init__(self, shape, color, size=100, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.color = color 
        self.size = size
        self.setFixedSize(QSize(size, size))
        self.setStyleSheet("background: none; border: none;")  # Remove borders

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set the brush and pen for the shape
        brush = QBrush(QColor(self.color))
        pen = QPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.setPen(pen)

        # Draw the shape
        if self.shape == "square":
            painter.drawRect(10, 10, self.size - 20, self.size - 20)
        elif self.shape == "circle":
            painter.drawEllipse(10, 10, self.size - 20, self.size - 20)
        elif self.shape == "triangle":
            points = [
                QPoint(self.size // 2, 10),
                QPoint(10, self.size - 10),
                QPoint(self.size - 10, self.size - 10),
            ]
            painter.drawPolygon(points)


class BotGame(QDialog):

    def __init__(self, target_shape, target_color, parent=None):
        super().__init__(parent)
        self.target_shape = target_shape
        self.target_color = target_color
        self.setWindowTitle("Prove You're Human")
        self.setFixedSize(500, 500)

        # Instructions
        layout = QVBoxLayout()
        instruction = QLabel(f"Click on all the {target_color} {target_shape}s.")
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)

        # Shape grid
        self.grid_layout = QGridLayout()
        self.shapes = []
        self.remaining_targets = 0
        self.create_shapes()
        layout.addLayout(self.grid_layout)

        self.setLayout(layout)

    def create_shapes(self):
        rows, cols = 5, 5  # Define grid size
        total_cells = rows * cols

        # Determine the number of target shapes (at least 3 and at most half of the grid)
        target_count = random.randint(3, total_cells // 2)
        self.remaining_targets = target_count

        # Generate positions for target shapes
        target_positions = random.sample(range(total_cells), target_count)

        for index in range(total_cells):
            if index in target_positions:
                # Create a target shape
                shape = self.target_shape
                color = self.target_color
            else:
                # Create a random shape and color
                shape = random.choice(["square", "circle", "triangle"])
                color = random.choice(["orange", "yellow", "green"])

            shape_widget = ShapeWidget(shape, color, parent=self)

            # Connect the shape widget to handle clicks
            shape_widget.mousePressEvent = lambda _, s=shape_widget: self.handle_click(s)

            self.shapes.append((shape_widget, shape, color))
            row, col = divmod(index, cols)
            self.grid_layout.addWidget(shape_widget, row, col)

    def handle_click(self, shape_widget):
        shape, color = shape_widget.shape, shape_widget.color
        is_target = shape == self.target_shape and color == self.target_color

        if is_target:
            # Remove the target shape by hiding it
            shape_widget.hide()
            self.remaining_targets -= 1

            # Check if the game is complete
            if self.remaining_targets == 0:
                QMessageBox.information(self, "Success", "You passed the bot check!")
                self.accept()  # Close the game with success
        else:
            # Incorrect click ends the game
            QMessageBox.critical(self, "Failure", "You clicked the wrong shape. Try again.")
            self.reject()  # Close the game with failure
            """