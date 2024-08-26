import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMenuBar, QMenu,
                             QPushButton, QSpinBox, QHBoxLayout, QComboBox, QToolTip, QStackedWidget)
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import Qt, QUrl, QByteArray
from Algorithms import *
import graphviz
import tempfile
import os
from manim import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64


class GraphVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualization Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.home_page = self.create_home_page()
        self.built_in_examples_page = BuiltInExamplesWidget(self)
        self.create_example_page = CreateExampleWidget(self)
        self.algorithm_selection_page = AlgorithmSelectionWidget(self)
        self.visualization_page = VisualizationPage(self)

        self.central_widget.addWidget(self.home_page)
        self.central_widget.addWidget(self.built_in_examples_page)
        self.central_widget.addWidget(self.create_example_page)
        self.central_widget.addWidget(self.algorithm_selection_page)
        self.central_widget.addWidget(self.visualization_page)

        self.create_menu()

    def run_algorithm_visualization(self, num_nodes, start_node, algorithm):
        graph, path = self.generate_networkx_graph(num_nodes, start_node, algorithm)
        self.visualization_page.visualize_path(graph, None, path, algorithm)

    # def run_algorithm_visualization(self, num_nodes, start_node, algorithm):
    #     graph, pos, path = self.generate_networkx_graph(num_nodes, start_node, algorithm)
    #     self.visualization_page.visualize_path(graph, pos, path, algorithm)

    def generate_networkx_graph(self, num_nodes, start_node, algorithm):
        G = nx.Graph()
        G.add_nodes_from(range(1, num_nodes + 1))

        # Generate random edges
        for i in range(1, num_nodes + 1):
            for j in range(i + 1, num_nodes + 1):
                if random.random() < 0.3:  # 30% chance of edge creation
                    weight = random.randint(1, 10)
                    G.add_edge(i, j, weight=weight)

        start_node = int(start_node)
        end_node = num_nodes  # Set the last node as the goal

        if algorithm == "Breadth-First Search (BFS)":
            path = nx.shortest_path(G, source=start_node, target=end_node)
        elif algorithm == "Depth-First Search (DFS)":
            path = list(nx.dfs_preorder_nodes(G, source=start_node))
            if end_node not in path:
                path.append(end_node)
        elif algorithm == "Dijkstra's Algorithm":
            path = nx.dijkstra_path(G, source=start_node, target=end_node)
        else:
            path = []

        return G, path

    # def generate_networkx_graph(self, num_nodes, start_node, algorithm):
    #     G = nx.Graph()
    #     G.add_nodes_from(range(1, num_nodes + 1))
    #
    #     # Generate random edges
    #     for i in range(1, num_nodes + 1):
    #         for j in range(i + 1, num_nodes + 1):
    #             if random.random() < 0.3:  # 30% chance of edge creation
    #                 weight = random.randint(1, 10)
    #                 G.add_edge(i, j, weight=weight)
    #
    #     pos = nx.spring_layout(G)
    #
    #     start_node = int(start_node)
    #     end_node = num_nodes  # Set the last node as the goal
    #
    #     if algorithm == "Breadth-First Search (BFS)":
    #         path = nx.shortest_path(G, source=start_node, target=end_node)
    #     elif algorithm == "Depth-First Search (DFS)":
    #         path = nx.dfs_preorder_nodes(G, source=start_node)
    #         path = list(path)
    #         if end_node not in path:
    #             path.append(end_node)
    #     elif algorithm == "Dijkstra's Algorithm":
    #         path = nx.dijkstra_path(G, source=start_node, target=end_node)
    #     else:
    #         path = []
    #
    #     return G, pos, path
    def create_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #444444; color: white;")

        examples_menu = QMenu("Examples", self)
        examples_menu.setStyleSheet("background-color: #444444; color: white;")
        menubar.addMenu(examples_menu)

        built_in_action = QAction("Built in examples", self)
        built_in_action.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        built_in_action.triggered.connect(self.show_built_in_examples)
        examples_menu.addAction(built_in_action)

        create_action = QAction("Create example", self)
        create_action.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        create_action.triggered.connect(self.show_create_example)
        examples_menu.addAction(create_action)

        help_action = QAction("Help", self)
        help_action.setFont(QFont("Arial", 10))
        help_action.setShortcut('Ctrl+H')
        help_action.triggered.connect(self.show_help)
        menubar.addAction(help_action)

    def create_home_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        built_in_button = self.create_main_button("Built in examples", "#007ACC")
        built_in_button.clicked.connect(self.show_built_in_examples)

        create_button = self.create_main_button("Create example", "#FF6600")
        create_button.clicked.connect(self.show_create_example)

        layout.addWidget(built_in_button)
        layout.addWidget(create_button)

        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #2D2D2D;")
        return widget

    def create_main_button(self, text, color):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: {color};
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        return button

    def darken_color(self, color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        factor = 0.8
        return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"

    def show_built_in_examples(self):
        self.central_widget.setCurrentWidget(self.built_in_examples_page)

    def show_create_example(self):
        self.central_widget.setCurrentWidget(self.create_example_page)

    def show_algorithm_selection(self):
        self.central_widget.setCurrentWidget(self.algorithm_selection_page)

    def show_help(self):
        print("Help clicked")

    def go_back(self):
        current_index = self.central_widget.currentIndex()
        if current_index > 0:
            self.central_widget.setCurrentIndex(current_index - 1)


class BuiltInExamplesWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Built-in Examples")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFD700; margin-bottom: 20px;")
        layout.addWidget(title)

        options_layout = QHBoxLayout()

        basic_button = self.create_option_button("Basic Example", "🔢",
                                                 "Learn graph algorithms using basic relatable examples")
        basic_button.clicked.connect(self.parent.show_algorithm_selection)
        options_layout.addWidget(basic_button)

        real_world_button = self.create_option_button("Real World Scenario", "🌍",
                                                      "Learn graph algorithms using real world applications and scenarios")
        options_layout.addWidget(real_world_button)

        layout.addLayout(options_layout)

        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems(
            ["The Traveling Salesman Problem", "Finding the Least Congested Path in London Tube"])
        self.scenario_combo.setStyleSheet("""
            QComboBox {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #5CBF60;
                color: white;
                selection-background-color: #45a049;
            }
        """)
        self.scenario_combo.currentIndexChanged.connect(self.parent.show_algorithm_selection)
        self.scenario_combo.hide()
        layout.addWidget(self.scenario_combo)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2D2D2D;")

    def create_option_button(self, text, icon, tooltip):
        button = QPushButton(f"{icon} {text}")
        button.setFont(QFont("Arial", 16))
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button.setToolTip(tooltip)
        QToolTip.setFont(QFont('SansSerif', 12))

        if text == "Real World Scenario":
            button.clicked.connect(self.toggle_scenario_dropdown)

        return button

    def toggle_scenario_dropdown(self):
        self.scenario_combo.setVisible(not self.scenario_combo.isVisible())


class AlgorithmSelectionWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Select Algorithm")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFD700; margin-bottom: 20px;")
        layout.addWidget(title)

        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        combo_style = """
            QComboBox {
                background-color: #5C85BF;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                margin-top: 5px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #6C95CF;
                color: white;
                selection-background-color: #4C75AF;
            }
        """

        # Traversal Algorithm section
        traversal_layout = QVBoxLayout()
        traversal_button = QPushButton("Traversal Algorithm")
        traversal_button.setStyleSheet(button_style)
        traversal_layout.addWidget(traversal_button)

        self.traversal_combo = QComboBox()
        self.traversal_combo.addItems(
            ["Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Dijkstra's Algorithm"])
        self.traversal_combo.setStyleSheet(combo_style)
        self.traversal_combo.hide()
        traversal_layout.addWidget(self.traversal_combo)

        traversal_button.clicked.connect(self.toggle_traversal_options)
        layout.addLayout(traversal_layout)

        # Visualization button
        visualize_button = QPushButton("Visualize")
        visualize_button.setStyleSheet(button_style)
        visualize_button.clicked.connect(self.show_visualization)
        layout.addWidget(visualize_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.go_back)
        back_button.setStyleSheet(button_style.replace("#4CAF50", "#FF5733"))
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2D2D2D;")

    def toggle_traversal_options(self):
        self.traversal_combo.setVisible(not self.traversal_combo.isVisible())

    def show_visualization(self):
        selected_algorithm = self.traversal_combo.currentText()
        self.parent.visualization_page.set_algorithm(selected_algorithm)
        self.parent.central_widget.setCurrentWidget(self.parent.visualization_page)


class CreateExampleWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Create Example")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFD700; margin-bottom: 20px;")
        layout.addWidget(title)

        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """

        select_algorithm_button = QPushButton("Select Algorithm")
        select_algorithm_button.clicked.connect(self.parent.show_algorithm_selection)
        select_algorithm_button.setStyleSheet(button_style)
        layout.addWidget(select_algorithm_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.go_back)
        back_button.setStyleSheet(button_style.replace("#3498db", "#FF5733"))  # Different color for back button
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2D2D2D;")


class GraphVisualizationScene(Scene):
    def __init__(self, graph, path, algorithm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.path = path
        self.algorithm = algorithm

    def construct(self):
        # Create Manim graph from NetworkX graph
        vertices = list(self.graph.nodes())
        edges = list(self.graph.edges())

        g = Graph(vertices, edges, layout="spring", layout_scale=3)

        # Add edge weights
        for edge in self.graph.edges(data=True):
            weight = Text(str(edge[2]['weight']), font_size=20)
            g.add(weight.move_to(g.edges[edge[:2]].get_center()))

        self.add(g)

        # Highlight the path
        if self.path:
            path_edges = list(zip(self.path, self.path[1:]))
            for edge in path_edges:
                g.edges[edge].set_color(RED)

        # Add title
        title = Text(f"{self.algorithm} - Path: {' -> '.join(map(str, self.path))}", font_size=36)
        title.to_edge(UP)
        self.add(title)


class VisualizationPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.algorithm = ""
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Sidebar for options (1/6 of the screen)
        options_widget = QWidget()
        options_layout = QVBoxLayout()
        options_widget.setLayout(options_layout)
        options_widget.setFixedWidth(200)  # Adjust this value as needed

        title = QLabel("Graph Visualization")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        options_layout.addWidget(title)

        self.node_count_spin = QSpinBox()
        self.node_count_spin.setRange(2, 10)
        self.node_count_spin.setValue(5)
        options_layout.addWidget(QLabel("Number of Nodes:"))
        options_layout.addWidget(self.node_count_spin)

        self.start_node_combo = QComboBox()
        options_layout.addWidget(QLabel("Start Node:"))
        options_layout.addWidget(self.start_node_combo)

        # Connect the node count change to update start node options
        self.node_count_spin.valueChanged.connect(self.update_start_node_options)

        visualize_button = QPushButton("Visualize")
        visualize_button.clicked.connect(self.visualize_graph)
        options_layout.addWidget(visualize_button)

        options_layout.addStretch()

        layout.addWidget(options_widget)

        # Graph visualization space (5/6 of the screen)
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, stretch=5)

        self.setLayout(layout)

        # Initialize start node options
        self.update_start_node_options(self.node_count_spin.value())

    def update_start_node_options(self, num_nodes):
        self.start_node_combo.clear()
        self.start_node_combo.addItems([str(i) for i in range(1, num_nodes + 1)])

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def visualize_graph(self):
        num_nodes = self.node_count_spin.value()
        start_node = self.start_node_combo.currentText()
        self.parent.run_algorithm_visualization(num_nodes, start_node, self.algorithm)

    def visualize_path(self, graph, pos, path, algorithm):
        # Create the Manim scene and render it
        scene = GraphVisualizationScene(graph, path, algorithm)
        scene.render(preview=False)

        # The rendered image path
        image_path = 'media/images/GraphVisualizationScene_ManimCE_v0.18.1.png'

        # Check if the file exists
        if os.path.exists(image_path):
            # Load the image into QWebEngineView
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()

            img_base64 = base64.b64encode(img_data).decode('utf-8')
            html = f'<img src="data:image/png;base64,{img_base64}">'
            self.web_view.setHtml(html)
        else:
            print(f"Error: Image file not found at {image_path}")

    # def visualize_path(self, graph, pos, path, algorithm):
    #     plt.figure(figsize=(10, 8))
    #     nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=16, font_weight='bold')
    #
    #     edge_labels = nx.get_edge_attributes(graph, 'weight')
    #     nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    #
    #     if path:
    #         path_edges = list(zip(path, path[1:]))
    #         nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='r', width=2)
    #
    #     plt.title(f"{algorithm} - Path: {' -> '.join(map(str, path))}")
    #
    #     buf = BytesIO()
    #     plt.savefig(buf, format='png')
    #     plt.close()
    #
    #     data = base64.b64encode(buf.getbuffer()).decode('ascii')
    #     html = f'<img src="data:image/png;base64,{data}">'
    #     self.web_view.setHtml(html)

    def remove_temp_file(self, filename):
        # Remove the temporary file
        try:
            os.remove(filename)
        except:
            pass


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QToolTip {
            background-color: #F0F0F0;
            color: #333333;
            border: 1px solid #CCCCCC;
            padding: 5px;
        }
    """)

    main_window = GraphVisualizationApp()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# class VisualizationPage(QWidget):
#     def __init__(self, parent):
#         super().__init__()
#         self.parent = parent
#         self.algorithm = ""
#         self.init_ui()
#
#     def init_ui(self):
#         layout = QHBoxLayout()
#
#         # Sidebar for options (1/6 of the screen)
#         options_widget = QWidget()
#         options_layout = QVBoxLayout()
#         options_widget.setLayout(options_layout)
#         options_widget.setFixedWidth(200)  # Adjust this value as needed
#
#         title = QLabel("Graph Visualization")
#         title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
#         options_layout.addWidget(title)
#
#         self.node_count_spin = QSpinBox()
#         self.node_count_spin.setRange(2, 10)
#         self.node_count_spin.setValue(5)
#         options_layout.addWidget(QLabel("Number of Nodes:"))
#         options_layout.addWidget(self.node_count_spin)
#
#         self.start_node_combo = QComboBox()
#         self.start_node_combo.addItems(['A', 'B', 'C', 'D', 'E', 'F'])
#         options_layout.addWidget(QLabel("Start Node:"))
#         options_layout.addWidget(self.start_node_combo)
#
#         visualize_button = QPushButton("Visualize")
#         visualize_button.clicked.connect(self.visualize_graph)
#         options_layout.addWidget(visualize_button)
#
#         options_layout.addStretch()
#
#         layout.addWidget(options_widget)
#
#         # Graph visualization space (5/6 of the screen)
#         self.figure = plt.figure(figsize=(10, 8))
#         self.canvas = FigureCanvas(self.figure)
#         layout.addWidget(self.canvas, stretch=5)
#
#         self.setLayout(layout)
#
#     def set_algorithm(self, algorithm):
#         self.algorithm = algorithm
#
#     def visualize_graph(self):
#         num_nodes = self.node_count_spin.value()
#         start_node = self.start_node_combo.currentText()
#         self.parent.run_algorithm_visualization(num_nodes, start_node, self.algorithm)
#
#     def visualize_path(self, graph, pos, path, algorithm):
#         self.figure.clear()
#         ax = self.figure.add_subplot(111)
#         nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=16, font_weight='bold', ax=ax)
#         nx.draw_networkx_edges(graph, pos, edgelist=list(zip(path, path[1:])), edge_color='r', width=2, ax=ax)
#         ax.set_title(f"{algorithm} - Path from {path[0]} to {path[-1]}")
#         self.canvas.draw()
