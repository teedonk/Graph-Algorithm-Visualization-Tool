import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMenuBar, QMenu,
                             QPushButton, QStyle, QSlider, QMessageBox, QSpinBox, QHBoxLayout, QComboBox, QToolTip, QStackedWidget)
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QUrl, QByteArray
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
import tempfile
import os
from manim import *
import networkx as nx
import shutil
import matplotlib.pyplot as plt
import traceback
import logging

class GraphVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualization Tool")
        self.setGeometry(100, 100, 1440, 900)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.home_page = self.create_home_page()
        self.built_in_examples_page = BuiltInExamplesWidget(self)
        self.create_example_page = CreateExampleWidget(self)
        self.algorithm_selection_page = AlgorithmSelectionWidget(self)
        self.visualization_page = VisualizationPage(self)
        self.real_world_scenario_page = RealWorldScenarioWidget(self)

        self.central_widget.addWidget(self.home_page)
        self.central_widget.addWidget(self.built_in_examples_page)
        self.central_widget.addWidget(self.create_example_page)
        self.central_widget.addWidget(self.algorithm_selection_page)
        self.central_widget.addWidget(self.visualization_page)
        self.central_widget.addWidget(self.real_world_scenario_page)

        self.create_menu()
    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

    def run_algorithm_visualization(self, num_nodes, start_node, end_node, algorithm, graph_type):
        try:
            logger.info(
                f"Running algorithm visualization: Nodes={num_nodes}, Start={start_node}, End={end_node}, Algorithm={algorithm}, Graph Type={graph_type}")
            graph, path = self.generate_networkx_graph(num_nodes, start_node, end_node, algorithm, graph_type)
            logger.info(f"Generated graph with {len(graph.nodes())} nodes and {len(graph.edges())} edges")
            logger.info(f"Generated path: {path}")
            self.visualization_page.visualize_path(graph, None, path, algorithm)
        except Exception as e:
            logger.error(f"Error in run_algorithm_visualization: {str(e)}")
            logger.error(traceback.format_exc())
            error_message = f"An error occurred during visualization: {str(e)}\n\nPlease try different parameters or contact support."
            self.show_error_message("Visualization Error", error_message)

    def generate_networkx_graph(self, num_nodes, start_node, end_node, algorithm, graph_type):
        logger.info(
            f"Generating NetworkX graph: Nodes={num_nodes}, Start={start_node}, End={end_node}, Algorithm={algorithm}, Graph Type={graph_type}")
        if graph_type == "Directed Acyclic Graph":
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        G.add_nodes_from(range(num_nodes))

        def add_edge(i, j):
            weight = random.randint(1, 10)
            G.add_edge(i, j, weight=weight)

        if graph_type == "Complete Graph":
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    add_edge(i, j)
        elif graph_type == "Linear Graph":
            for i in range(num_nodes - 1):
                add_edge(i, i + 1)
        elif graph_type == "Star Graph":
            for i in range(1, num_nodes):
                add_edge(0, i)
        elif graph_type == "Tree Graph":
            for i in range(1, num_nodes):
                parent = random.randint(0, i - 1)
                add_edge(parent, i)
        elif graph_type == "Directed Acyclic Graph":
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    if random.random() < 0.3:  # 30% chance of adding an edge
                        add_edge(i, j)

        logger.info(f"Generated graph with {len(G.nodes())} nodes and {len(G.edges())} edges")

        start_node = int(start_node)
        end_node = int(end_node) if end_node is not None else None

        # Ensure the graph is connected
        if isinstance(G, nx.DiGraph):
            if not nx.is_weakly_connected(G):
                # For directed graphs, add edges to ensure weak connectivity
                nodes = list(G.nodes())
                for i in range(len(nodes) - 1):
                    G.add_edge(nodes[i], nodes[i + 1], weight=random.randint(1, 10))
        else:
            if not nx.is_connected(G):
                # For undirected graphs, add edges to ensure connectivity
                nodes = list(G.nodes())
                for i in range(len(nodes) - 1):
                    G.add_edge(nodes[i], nodes[i + 1], weight=random.randint(1, 10))

        def find_shortest_path_visiting_all_nodes(G, start_node, algorithm):
            unvisited = set(G.nodes())
            current_node = start_node
            path = [current_node]
            unvisited.remove(current_node)

            while unvisited:
                reachable_nodes = [n for n in unvisited if nx.has_path(G, current_node, n)]
                if not reachable_nodes:
                    # If no unvisited nodes are reachable, find the shortest path to any unvisited node
                    next_node = min(unvisited,
                                    key=lambda n: nx.shortest_path_length(G, current_node, n, weight='weight'))
                else:
                    if algorithm == "Dijkstra's Algorithm":
                        next_node = min(reachable_nodes,
                                        key=lambda n: nx.dijkstra_path_length(G, current_node, n, weight='weight'))
                        segment = nx.dijkstra_path(G, current_node, next_node, weight='weight')
                    else:  # A* Algorithm
                        next_node = min(reachable_nodes,
                                        key=lambda n: nx.astar_path_length(G, current_node, n, weight='weight'))
                        segment = nx.astar_path(G, current_node, next_node, weight='weight')

                path.extend(segment[1:])
                unvisited.remove(next_node)
                current_node = next_node

            return path

        if algorithm == "Breadth-First Search (BFS)":
            path = list(nx.bfs_edges(G, source=start_node))
        elif algorithm == "Depth-First Search (DFS)":
            path = list(nx.dfs_edges(G, source=start_node))
        elif algorithm == "Dijkstra's Algorithm" or algorithm == "A* Algorithm":
            full_path = find_shortest_path_visiting_all_nodes(G, start_node, algorithm)
            path = list(zip(full_path[:-1], full_path[1:]))
        else:
            path = []

        logger.info(f"Generated path: {path}")
        return G, path
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


    def show_real_world_scenarios(self):
        self.central_widget.setCurrentWidget(self.real_world_scenario_page)

    def show_visualization_page(self):
        self.central_widget.setCurrentWidget(self.visualization_page)

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
        basic_button.clicked.connect(self.show_algorithm_selection)
        options_layout.addWidget(basic_button)

        real_world_button = self.create_option_button("Real World Scenario", "🌍",
                                                      "Learn graph algorithms using real world applications and scenarios")
        real_world_button.clicked.connect(self.show_real_world_scenarios)
        options_layout.addWidget(real_world_button)

        layout.addLayout(options_layout)

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
        return button

    def show_algorithm_selection(self):
        self.parent.show_algorithm_selection()

    def show_real_world_scenarios(self):
        self.parent.show_real_world_scenarios()


class RealWorldScenarioWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Real World Scenarios")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFD700; margin-bottom: 20px;")
        layout.addWidget(title)

        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems(["The Traveling Salesman Problem", "Finding the Least Congested Path in London Tube"])
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
        layout.addWidget(self.scenario_combo)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Dijkstra's Algorithm", "A* Algorithm"])
        self.algorithm_combo.setStyleSheet(self.scenario_combo.styleSheet())
        layout.addWidget(self.algorithm_combo)

        visualize_button = QPushButton("Visualize")
        visualize_button.clicked.connect(self.visualize)
        visualize_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(visualize_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        back_button.setStyleSheet(visualize_button.styleSheet().replace("#3498db", "#FF5733"))
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2D2D2D;")

    def visualize(self):
        scenario = self.scenario_combo.currentText()
        algorithm = self.algorithm_combo.currentText()
        # Here you would implement the visualization for the selected real-world scenario
        # For now, we'll just print the selected options
        print(f"Visualizing {scenario} using {algorithm}")
        # In the future, you can replace this with actual visualization logic
        self.parent.show_visualization_page()

    def go_back(self):
        self.parent.show_built_in_examples()
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
        self.traversal_combo.addItems(["Breadth-First Search (BFS)", "Depth-First Search (DFS)"])
        self.traversal_combo.setStyleSheet(combo_style)
        self.traversal_combo.hide()
        traversal_layout.addWidget(self.traversal_combo)

        traversal_button.clicked.connect(self.toggle_traversal_options)
        layout.addLayout(traversal_layout)

        # Pathfinding Algorithm section
        pathfinding_layout = QVBoxLayout()
        pathfinding_button = QPushButton("Pathfinding Algorithm")
        pathfinding_button.setStyleSheet(button_style)
        pathfinding_layout.addWidget(pathfinding_button)

        self.pathfinding_combo = QComboBox()
        self.pathfinding_combo.addItems(["Dijkstra's Algorithm", "A* Algorithm"])
        self.pathfinding_combo.setStyleSheet(combo_style)
        self.pathfinding_combo.hide()
        pathfinding_layout.addWidget(self.pathfinding_combo)

        pathfinding_button.clicked.connect(self.toggle_pathfinding_options)
        layout.addLayout(pathfinding_layout)

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
        self.pathfinding_combo.hide()

    def toggle_pathfinding_options(self):
        self.pathfinding_combo.setVisible(not self.pathfinding_combo.isVisible())
        self.traversal_combo.hide()

    def show_visualization(self):
        if self.traversal_combo.isVisible():
            selected_algorithm = self.traversal_combo.currentText()
        elif self.pathfinding_combo.isVisible():
            selected_algorithm = self.pathfinding_combo.currentText()
        else:
            selected_algorithm = "No algorithm selected"

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
        logger.info(f"Initializing GraphVisualizationScene: Algorithm={algorithm}, Path={path}")

    def construct(self):
        vertices = list(self.graph.nodes())
        edges = list(self.graph.edges(data=True))

        logger.info(f"Constructing graph with {len(vertices)} vertices and {len(edges)} edges")

        g = Graph(
            vertices,
            [(e[0], e[1]) for e in edges],
            layout="spring",
            layout_scale=3,
            vertex_config={"fill_color": BLUE, "radius": 0.3},
            edge_config={
                "stroke_color": GRAY,
                "buff": 0.3,
            }
        )

        # Add arrows for directed graphs and edge weights for pathfinding algorithms
        edge_weights = {}
        weight_labels = {}
        for edge in edges:
            start, end, data = edge
            line = g.edges[(start, end)]

            # Add arrow for directed graphs
            if isinstance(self.graph, nx.DiGraph):
                arrow = Arrow(
                    line.get_start(),
                    line.get_end(),
                    buff=0.3,
                    color=GRAY,
                    max_tip_length_to_length_ratio=0.1,
                    max_stroke_width_to_length_ratio=2,
                )
                g.add(arrow)

            # Add edge weight label only for pathfinding algorithms
            if 'weight' in data and ("Dijkstra" in self.algorithm or "A*" in self.algorithm):
                weight = data['weight']
                weight_label = Text(str(weight), font_size=16, color=WHITE)
                weight_label.move_to(line.get_center() + UP * 0.1)
                weight_labels[(start, end)] = weight_label
                edge_weights[(start, end)] = weight

        # Label all nodes
        for node in g.vertices:
            label = Text(str(node), font_size=24, color=WHITE)
            label.move_to(g[node].get_center())
            g.add(label)

        self.add(g)

        # Add title
        title = Text(f"{self.algorithm}", font_size=36)
        title.to_edge(UP)
        self.add(title)

        # Initialize path text
        path_text = Text("Path: ", font_size=24)
        path_text.to_edge(DOWN)
        self.add(path_text)

        # Initialize distance text for Dijkstra's and A*
        if "Dijkstra" in self.algorithm or "A*" in self.algorithm:
            distance_text = Text("Distance: 0", font_size=24)
            distance_text.next_to(path_text, UP)
            self.add(distance_text)

        visited_nodes = set()
        total_distance = 0
        invalid_edges = []

        # Add all weight labels at once for pathfinding algorithms
        if "Dijkstra" in self.algorithm or "A*" in self.algorithm:
            self.add(*weight_labels.values())

        logger.info(f"Starting path animation: {self.path}")
        if not self.path:
            self.add(Text("No path found or start/end nodes are the same", font_size=24, color=RED).next_to(title, DOWN))
        else:
            for i, edge in enumerate(self.path):
                start, end = edge
                logger.info(f"Animating edge {i}: {start} -> {end}")

                # Check if the edge exists in the graph
                if (start, end) in g.edges or (end, start) in g.edges:
                    # Highlight the current edge
                    edge_to_highlight = (start, end) if (start, end) in g.edges else (end, start)
                    self.play(g.edges[edge_to_highlight].animate.set_color(RED), run_time=0.5)
                else:
                    invalid_edges.append((start, end))
                    logger.warning(f"Edge {start} -> {end} does not exist in the graph")

                # Highlight nodes
                for node in [start, end]:
                    if node not in visited_nodes:
                        self.play(g[node].animate.set_color(RED), run_time=0.5)
                        visited_nodes.add(node)

                # Update the path text
                new_path_text = Text(f"Path: {' -> '.join(map(str, visited_nodes))}", font_size=24)
                new_path_text.to_edge(DOWN)
                self.play(Transform(path_text, new_path_text), run_time=0.5)

                # Update distance for Dijkstra's and A*
                if "Dijkstra" in self.algorithm or "A*" in self.algorithm:
                    if (start, end) in edge_weights or (end, start) in edge_weights:
                        total_distance += edge_weights.get((start, end), edge_weights.get((end, start), 0))
                        new_distance_text = Text(f"Distance: {total_distance}", font_size=24)
                        new_distance_text.next_to(new_path_text, UP)
                        self.play(Transform(distance_text, new_distance_text), run_time=0.5)

                # Add stage label
                stage_label = Text(f"Stage {i + 1}", font_size=20, color=YELLOW)
                stage_label.next_to(g[end], UP)
                self.play(FadeIn(stage_label))

                # Pause to allow viewers to see the current state
                self.wait(1)

        # Highlight any remaining unvisited nodes
        unvisited_nodes = set(vertices) - visited_nodes
        if unvisited_nodes:
            for node in unvisited_nodes:
                self.play(g[node].animate.set_color(YELLOW), run_time=0.5)

            unvisited_text = Text(f"Unvisited nodes: {', '.join(map(str, unvisited_nodes))}", font_size=20, color=YELLOW)
            unvisited_text.next_to(path_text, UP)
            self.play(FadeIn(unvisited_text))

        # Display invalid edges if any
        if invalid_edges:
            invalid_edges_text = Text(f"Invalid edges: {', '.join([f'{s}->{e}' for s, e in invalid_edges])}",
                                      font_size=20, color=RED)
            invalid_edges_text.next_to(unvisited_text, UP) if unvisited_nodes else invalid_edges_text.next_to(path_text, UP)
            self.play(FadeIn(invalid_edges_text))

        # Final state
        self.wait(2)
        logger.info("Finished constructing and animating the scene")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VisualizationPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.algorithm = ""
        self.temp_dir = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left panel for controls (1/6 of the screen width)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(self.width() // 6)

        title = QLabel("Graph Visualization")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(title)

        self.node_count_spin = QSpinBox()
        self.node_count_spin.setRange(2, 10)
        self.node_count_spin.setValue(5)
        left_layout.addWidget(QLabel("Number of Nodes:"))
        left_layout.addWidget(self.node_count_spin)

        self.start_node_combo = QComboBox()
        left_layout.addWidget(QLabel("Start Node:"))
        left_layout.addWidget(self.start_node_combo)

        self.end_node_combo = QComboBox()
        left_layout.addWidget(QLabel("End Node:"))
        left_layout.addWidget(self.end_node_combo)
        self.end_node_combo.hide()

        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Complete Graph", "Linear Graph", "Star Graph", "Tree Graph", "Directed Acyclic Graph"])
        left_layout.addWidget(QLabel("Graph Type:"))
        left_layout.addWidget(self.graph_type_combo)

        self.node_count_spin.valueChanged.connect(self.update_node_options)

        visualize_button = QPushButton("Visualize")
        visualize_button.clicked.connect(self.visualize_graph)
        left_layout.addWidget(visualize_button)

        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # Right panel for visualization and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Video player
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        right_layout.addWidget(self.video_widget, 7)  # 7/10 of the right panel

        # Static image display (fallback)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.hide()
        right_layout.addWidget(self.image_label, 7)  # 7/10 of the right panel

        # Bottom controls panel
        bottom_controls = QWidget()
        bottom_layout = QVBoxLayout(bottom_controls)

        # Progress Slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        bottom_layout.addWidget(self.progress_slider)

        # Playback controls
        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)

        self.backward_button = QPushButton()
        self.backward_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.backward_button.clicked.connect(self.backward)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.forward_button.clicked.connect(self.forward)

        self.replay_button = QPushButton()
        self.replay_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.replay_button.clicked.connect(self.replay)

        controls_layout.addWidget(self.backward_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.forward_button)
        controls_layout.addWidget(self.replay_button)

        bottom_layout.addLayout(controls_layout)
        right_layout.addWidget(bottom_controls, 3)  # 3/10 of the right panel

        main_layout.addWidget(right_panel, 5)  # 5/6 of the total width

        self.setLayout(main_layout)
        self.update_node_options(self.node_count_spin.value())

        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

    def update_node_options(self, num_nodes):
        self.start_node_combo.clear()
        self.end_node_combo.clear()
        for i in range(num_nodes):
            self.start_node_combo.addItem(str(i))
            self.end_node_combo.addItem(str(i))

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        if "Dijkstra" in algorithm or "A*" in algorithm:
            self.end_node_combo.show()
        else:
            self.end_node_combo.hide()

    def visualize_graph(self):
        try:
            logger.info("Visualize button clicked")
            num_nodes = self.node_count_spin.value()
            start_node = int(self.start_node_combo.currentText())
            end_node = int(self.end_node_combo.currentText()) if self.end_node_combo.isVisible() else None
            graph_type = self.graph_type_combo.currentText()
            logger.info(f"Visualizing: Nodes={num_nodes}, Start={start_node}, End={end_node}, Type={graph_type}, Algorithm={self.algorithm}")
            self.parent.run_algorithm_visualization(num_nodes, start_node, end_node, self.algorithm, graph_type)
        except Exception as e:
            logger.error(f"Error in visualize_graph: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_error_message("Visualization Error", str(e))

    def visualize_path(self, graph, pos, path, algorithm):
        try:
            logger.info("Entering visualize_path method")
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)

            self.temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temporary directory: {self.temp_dir}")

            config.pixel_height = 480
            config.pixel_width = 854
            config.frame_rate = 15

            scene = GraphVisualizationScene(graph, path, algorithm)
            logger.info("Rendering scene...")
            scene.render()

            rendered_video = 'media/videos/480p15/GraphVisualizationScene.mp4'
            video_path = os.path.join(self.temp_dir, 'GraphVisualizationScene.mp4')

            if not os.path.exists(rendered_video):
                raise FileNotFoundError(f"Rendered video not found at {rendered_video}")

            shutil.move(rendered_video, video_path)

            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video not found at {video_path}")

            logger.info(f"Setting media source: {video_path}")
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.play_pause()
            self.video_widget.show()
            self.image_label.hide()

            logger.info(f"Video successfully loaded from {video_path}")
        except Exception as e:
            logger.error(f"Error in visualize_path: {str(e)}")
            logger.error(traceback.format_exc())

            # Fallback to static image
            logger.info("Falling back to static image")
            self.create_static_image(graph, algorithm)

    def create_static_image(self, graph, algorithm):
        try:
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(graph)
            nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10,
                    font_weight='bold')
            edge_labels = nx.get_edge_attributes(graph, 'weight')
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

            plt.title(f"{algorithm} - Static Visualization")
            img_path = os.path.join(self.temp_dir, 'graph.png')
            plt.savefig(img_path)
            plt.close()

            pixmap = QPixmap(img_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))
            self.video_widget.hide()
            self.image_label.show()

            logger.info(f"Static image saved to {img_path}")
        except Exception as e:
            logger.error(f"Error creating static image: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_error_message("Visualization Error", "Failed to create static image")
    def show_error_message(self, title, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        error_box.exec()

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def stop(self):
        self.media_player.stop()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def backward(self):
        new_position = max(0, self.media_player.position() - 5000)  # Go back 5 seconds
        self.media_player.setPosition(new_position)

    def forward(self):
        new_position = min(self.media_player.duration(), self.media_player.position() + 5000)  # Go forward 5 seconds
        self.media_player.setPosition(new_position)

    def replay(self):
        self.media_player.setPosition(0)
        self.media_player.play()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)

    def update_position(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def closeEvent(self, event):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().closeEvent(event)

    #
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