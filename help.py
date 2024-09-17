from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtCore import Qt, QUrl


class HelpWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        # Load the HTML file
        html_path = QUrl.fromLocalFile("help.html")
        self.text_browser.setSource(html_path)

        layout.addWidget(self.text_browser)

        self.setLayout(layout)
        self.setWindowTitle("Graph Visualization Tool Help")
        self.resize(800, 600)