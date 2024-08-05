import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMenuBar, QMenu
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt

class GraphVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graph Visualization Tool")
        self.setGeometry(100, 100, 800, 600)

        # Create main menu
        menubar = self.menuBar()

        # Create 'Examples' menu
        examples_menu = QMenu("Examples", self)
        menubar.addMenu(examples_menu)

        # Add 'Built in examples' action
        built_in_action = QAction("Built in examples", self)
        built_in_action.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        built_in_action.triggered.connect(self.show_built_in_examples)
        examples_menu.addAction(built_in_action)

        # Add 'Create example' action
        create_action = QAction("Create example", self)
        create_action.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        create_action.triggered.connect(self.show_create_example)
        examples_menu.addAction(create_action)

        # Add 'Help' action
        help_action = QAction("Help", self)
        help_action.setFont(QFont("Arial", 10))
        help_action.setShortcut('Ctrl+H')
        help_action.triggered.connect(self.show_help)
        menubar.addAction(help_action)

        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout for central widget
        layout = QVBoxLayout()

        # Create labels for 'Built in examples' and 'Create example'
        built_in_label = QLabel("Built in examples")
        built_in_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        built_in_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        create_label = QLabel("Create example")
        create_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        create_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add labels to layout
        layout.addWidget(built_in_label)
        layout.addWidget(create_label)

        central_widget.setLayout(layout)

    def show_built_in_examples(self):
        # Placeholder function for 'Built in examples' action
        print("Built in examples clicked")

    def show_create_example(self):
        # Placeholder function for 'Create example' action
        print("Create example clicked")

    def show_help(self):
        # Placeholder function for 'Help' action
        print("Help clicked")

def main():
    app = QApplication(sys.argv)
    main_window = GraphVisualizationApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
