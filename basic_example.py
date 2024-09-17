import numpy as np
import networkx as nx
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSlider, QStyle
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from manim import *
import tempfile
import os
import shutil

class TSPVisualizationScene(Scene):
    def __init__(self, graph, path, algorithm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.path = path
        self.algorithm = algorithm

    def construct(self):
        vertices = list(self.graph.nodes())
        edges = list(self.graph.edges(data=True))

        g = Graph(
            vertices,
            [(e[0], e[1]) for e in edges],
            layout="spring",
            layout_scale=3,
            vertex_config={"fill_color": BLUE, "radius": 0.3},
            edge_config={"stroke_color": GRAY, "buff": 0.3}
        )

        # Add edge weights
        weight_labels = {}
        for edge in edges:
            start, end, data = edge
            weight = data['weight']
            weight_label = Text(f"{weight:.2f}", font_size=16, color=WHITE)
            weight_label.move_to(g.edges[(start, end)].get_center() + UP * 0.1)
            weight_labels[(start, end)] = weight_label

        # Label all nodes
        for node in g.vertices:
            label = Text(str(node), font_size=24, color=WHITE)
            label.move_to(g[node].get_center())
            g.add(label)

        self.add(g)
        self.add(*weight_labels.values())

        # Add title
        title = Text(f"TSP: {self.algorithm}", font_size=36)
        title.to_edge(UP)
        self.add(title)

        # Initialize path text
        path_text = Text("Path: ", font_size=24)
        path_text.to_edge(DOWN)
        self.add(path_text)

        # Initialize distance text
        distance_text = Text("Distance: 0", font_size=24)
        distance_text.next_to(path_text, UP)
        self.add(distance_text)

        visited_nodes = []
        total_distance = 0

        for i, (start, end) in enumerate(self.path):
            # Highlight the current edge
            self.play(g.edges[(start, end)].animate.set_color(RED), run_time=0.5)

            # Highlight nodes
            for node in [start, end]:
                if node not in visited_nodes:
                    self.play(g[node].animate.set_color(RED), run_time=0.5)
                    visited_nodes.append(node)

            # Update the path text
            new_path_text = Text(f"Path: {' -> '.join(map(str, visited_nodes))}", font_size=24)
            new_path_text.to_edge(DOWN)
            self.play(Transform(path_text, new_path_text), run_time=0.5)

            # Update distance
            total_distance += self.graph[start][end]['weight']
            new_distance_text = Text(f"Distance: {total_distance:.2f}", font_size=24)
            new_distance_text.next_to(new_path_text, UP)
            self.play(Transform(distance_text, new_distance_text), run_time=0.5)

            # Add stage label
            stage_label = Text(f"Step {i + 1}", font_size=20, color=YELLOW)
            stage_label.next_to(g[end], UP)
            self.play(FadeIn(stage_label))

            self.wait(1)

        # Final state
        self.wait(2)

class TSPVisualizationWidget(QWidget):
    visualize_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.temp_dir = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Algorithm type selection
        algo_type_layout = QHBoxLayout()
        algo_type_label = QLabel("Algorithm Type:")
        self.algo_type_combo = QComboBox()
        self.algo_type_combo.addItems(["Traversal", "Pathfinding"])
        self.algo_type_combo.currentTextChanged.connect(self.on_algo_type_changed)
        algo_type_layout.addWidget(algo_type_label)
        algo_type_layout.addWidget(self.algo_type_combo)
        layout.addLayout(algo_type_layout)

        # Algorithm selection
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Select Algorithm:")
        self.algo_combo = QComboBox()
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        layout.addLayout(algo_layout)

        # Visualization button
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.clicked.connect(self.on_visualize)
        layout.addWidget(self.visualize_button)

        # Video player
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        layout.addWidget(self.video_widget)

        # Playback controls
        controls_layout = QHBoxLayout()
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_button)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.progress_slider)

        layout.addLayout(controls_layout)

        self.setLayout(layout)
        self.on_algo_type_changed("Traversal")  # Set initial algorithms

    def on_algo_type_changed(self, algo_type):
        self.algo_combo.clear()
        if algo_type == "Traversal":
            self.algo_combo.addItems(["Breadth-First Search (BFS)", "Depth-First Search (DFS)"])
        else:  # Pathfinding
            self.algo_combo.addItems(["Dijkstra's Algorithm", "A* Algorithm"])

    def load_data(self):
        self.data = np.loadtxt('tiny.csv', delimiter=',')
        self.graph = self.create_graph_from_data(self.data)

    def create_graph_from_data(self, data):
        G = nx.Graph()
        for i, (x, y) in enumerate(data):
            G.add_node(i, pos=(x, y))
        for i in G.nodes:
            for j in G.nodes:
                if i != j:
                    dist = np.linalg.norm(np.array(G.nodes[i]['pos']) - np.array(G.nodes[j]['pos']))
                    G.add_edge(i, j, weight=dist)
        return G

    def on_visualize(self):
        algorithm = self.algo_combo.currentText()
        self.visualize_signal.emit(algorithm)
        self.visualize_tsp(algorithm)

    def visualize_tsp(self, algorithm):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = tempfile.mkdtemp()

        if algorithm == "Breadth-First Search (BFS)":
            path = list(nx.bfs_edges(self.graph, source=0))
        elif algorithm == "Depth-First Search (DFS)":
            path = list(nx.dfs_edges(self.graph, source=0))
        elif algorithm == "Dijkstra's Algorithm":
            path = nx.single_source_dijkstra_path(self.graph, source=0, weight='weight')
            path = [(path[node][-2], node) for node in path if len(path[node]) > 1]
        elif algorithm == "A* Algorithm":
            path = nx.astar_path(self.graph, source=0, target=len(self.graph)-1, weight='weight')
            path = list(zip(path[:-1], path[1:]))

        config.pixel_height = 720
        config.pixel_width = 1280
        config.frame_rate = 30

        scene = TSPVisualizationScene(self.graph, path, algorithm)
        scene.render()

        video_path = os.path.join(self.temp_dir, 'TSPVisualizationScene.mp4')
        shutil.move('media/videos/1080p60/TSPVisualizationScene.mp4', video_path)

        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.play_pause()

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop(self):
        self.media_player.stop()

    def set_position(self, position):
        self.media_player.setPosition(position)

    def closeEvent(self, event):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().closeEvent(event)