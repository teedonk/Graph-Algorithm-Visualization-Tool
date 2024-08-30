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

class GraphVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualization Tool")
        self.setGeometry(100, 100, 1440, 900)  # Adjust the width and height as needed
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

    def run_algorithm_visualization(self, num_nodes, start_node, algorithm, graph_type):
        try:
            graph, path = self.generate_networkx_graph(num_nodes, start_node, algorithm, graph_type)
            self.visualization_page.visualize_path(graph, None, path, algorithm)
        except Exception as e:
            print(f"Error in run_algorithm_visualization: {str(e)}")
            traceback.print_exc()
            self.show_error_message("Visualization Error", str(e))

    def generate_networkx_graph(self, num_nodes, start_node, algorithm, graph_type):
        G = nx.Graph()
        G.add_nodes_from(range(num_nodes))

        def add_edge(i, j):
            G.add_edge(i, j)

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

        start_node = int(start_node)

        if algorithm == "Breadth-First Search (BFS)":
            path = list(nx.bfs_edges(G, source=start_node))
        elif algorithm == "Depth-First Search (DFS)":
            path = list(nx.dfs_edges(G, source=start_node))
        elif algorithm == "Dijkstra's Algorithm":
            path = nx.dijkstra_path(G, source=start_node, target=num_nodes - 1)
            path = list(zip(path[:-1], path[1:]))
        else:
            path = []

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

        g = Graph(vertices, edges, layout="spring", layout_scale=3,
                  vertex_config={"fill_color": BLUE, "radius": 0.3},
                  edge_config={"stroke_color": GRAY})

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

        # Animate the path
        path_text = Text("Path: ", font_size=24)
        path_text.to_edge(DOWN)
        self.add(path_text)

        visited_nodes = []
        for i, edge in enumerate(self.path):
            start, end = edge

            # Highlight the current edge
            self.play(g.edges[edge].animate.set_color(RED), run_time=0.5)

            # Highlight nodes
            for node in [start, end]:
                if node not in visited_nodes:
                    self.play(g[node].animate.set_color(RED), run_time=0.5)
                    visited_nodes.append(node)

            # Update the path text
            new_path_text = Text(f"Path: {' -> '.join(map(str, visited_nodes))}", font_size=24)
            new_path_text.to_edge(DOWN)
            self.play(Transform(path_text, new_path_text), run_time=0.5)

            # Add stage label
            stage_label = Text(f"Stage {i + 1}", font_size=20, color=YELLOW)
            stage_label.next_to(g[end], UP)
            self.play(FadeIn(stage_label))

        # Final state
        self.wait(1)

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

        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Complete Graph", "Linear Graph", "Star Graph", "Tree Graph"])
        left_layout.addWidget(QLabel("Graph Type:"))
        left_layout.addWidget(self.graph_type_combo)

        self.node_count_spin.valueChanged.connect(self.update_start_node_options)

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
        self.update_start_node_options(self.node_count_spin.value())

        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

    def update_start_node_options(self, num_nodes):
        self.start_node_combo.clear()
        self.start_node_combo.addItems([str(i) for i in range(num_nodes)])

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def visualize_graph(self):
        try:
            print("Visualize button clicked")
            num_nodes = self.node_count_spin.value()
            start_node = self.start_node_combo.currentText()
            graph_type = self.graph_type_combo.currentText()
            print(f"Visualizing: Nodes={num_nodes}, Start={start_node}, Type={graph_type}, Algorithm={self.algorithm}")
            self.parent.run_algorithm_visualization(num_nodes, start_node, self.algorithm, graph_type)
        except Exception as e:
            print(f"Error in visualize_graph: {str(e)}")
            traceback.print_exc()
            self.show_error_message("Visualization Error", str(e))

    def visualize_path(self, graph, pos, path, algorithm):
        try:
            print("Entering visualize_path method")
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)

            self.temp_dir = tempfile.mkdtemp()
            print(f"Created temporary directory: {self.temp_dir}")

            config.pixel_height = 480
            config.pixel_width = 854
            config.frame_rate = 15

            scene = GraphVisualizationScene(graph, path, algorithm)
            scene.render()

            rendered_video = 'media/videos/480p15/GraphVisualizationScene.mp4'
            video_path = os.path.join(self.temp_dir, 'GraphVisualizationScene.mp4')

            if not os.path.exists(rendered_video):
                raise FileNotFoundError(f"Rendered video not found at {rendered_video}")

            shutil.move(rendered_video, video_path)

            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video not found at {video_path}")

            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.play_pause()
            self.video_widget.show()
            self.image_label.hide()

            print(f"Video successfully loaded from {video_path}")
        except Exception as e:
            print(f"Error in visualize_path: {str(e)}")
            traceback.print_exc()

            # Fallback to static image
            print("Falling back to static image")
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

            print(f"Static image saved to {img_path}")
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