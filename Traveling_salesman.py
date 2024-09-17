import sys
import random
from PyQt6.QtWidgets import (QApplication, QWidget,QStyle,QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSlider, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QFont
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile
import os
import shutil
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CITY_NAMES = ["New York", "London", "Tokyo", "Paris", "Sydney", "Moscow", "Dubai",
              "Singapore", "Rome", "Cairo", "Rio de Janeiro", "Bangkok", "Toronto",
              "Berlin", "Mumbai", "Seoul", "Istanbul", "Amsterdam", "Madrid", "Vienna"]


class TSPVisualizationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.graph = None
        self.city_positions = None
        self.city_names = None
        self.temp_dir = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left panel for controls (1/5 of the screen width)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        title = QLabel("Traveling Salesman Problem")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(title)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Breadth-First Search (BFS)", "Depth-First Search (DFS)",
                                       "Dijkstra's Algorithm", "A* Algorithm"])
        left_layout.addWidget(QLabel("Graph Algorithm:"))
        left_layout.addWidget(self.algorithm_combo)

        visualize_button = QPushButton("Visualize")
        visualize_button.clicked.connect(self.visualize)
        left_layout.addWidget(visualize_button)

        left_layout.addStretch()

        # Right panel for visualization (4/5 of the screen width)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Stacked widget to switch between image and video
        self.stacked_widget = QStackedWidget()
        right_layout.addWidget(self.stacked_widget)

        # Video display
        self.video_widget = QVideoWidget()
        self.stacked_widget.addWidget(self.video_widget)

        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # Progress Slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.sliderMoved.connect(self.set_position)
        right_layout.addWidget(self.progress_slider)

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

        right_layout.addLayout(controls_layout)

        # Add panels to main layout with correct proportions
        main_layout.addWidget(left_panel, 1)  # 1/5 of the total width
        main_layout.addWidget(right_panel, 4)  # 4/5 of the total width

        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.errorOccurred.connect(self.handle_media_error)

    def visualize(self):
        algorithm = self.algorithm_combo.currentText()
        logger.info(f"Visualizing with algorithm: {algorithm}")
        start_node = 0  # Assuming the salesman starts from the first city

        try:
            if algorithm == "Breadth-First Search (BFS)":
                path = list(nx.bfs_edges(self.graph, source=start_node))
            elif algorithm == "Depth-First Search (DFS)":
                path = list(nx.dfs_edges(self.graph, source=start_node))
            elif algorithm in ["Dijkstra's Algorithm", "A* Algorithm"]:
                if algorithm == "Dijkstra's Algorithm":
                    path_func = nx.dijkstra_path
                else:  # A* Algorithm
                    path_func = nx.astar_path

                full_path = [start_node]
                current_node = start_node
                unvisited = set(self.graph.nodes()) - {start_node}

                while unvisited:
                    next_node = min(unvisited, key=lambda n: nx.path_weight(self.graph,
                                                                            path_func(self.graph, current_node, n,
                                                                                      weight='weight'), 'weight'))
                    full_path.extend(path_func(self.graph, current_node, next_node, weight='weight')[1:])
                    unvisited.remove(next_node)
                    current_node = next_node

                full_path.append(start_node)  # Return to start
                path = list(zip(full_path[:-1], full_path[1:]))
            else:
                raise ValueError("Invalid algorithm selected.")

            self.generate_video_visualization(algorithm, path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during visualization: {str(e)}")

    def load_data(self):
        try:
            data = np.loadtxt('tiny.csv', delimiter=',')
            logger.info(f"Loaded data from tiny.csv: {data.shape} points")
            self.city_positions = {i: (x, y) for i, (x, y) in enumerate(data)}
            self.city_names = {i: name for i, name in zip(range(len(data)), random.sample(CITY_NAMES, len(data)))}

            self.graph = nx.Graph()
            for i, (x, y) in self.city_positions.items():
                self.graph.add_node(i, pos=(x, y), name=self.city_names[i])

            for i in range(len(self.city_positions)):
                for j in range(i + 1, len(self.city_positions)):
                    dist = np.linalg.norm(np.array(self.city_positions[i]) - np.array(self.city_positions[j]))
                    self.graph.add_edge(i, j, weight=dist)
            # ... rest of the method ...
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def generate_video_visualization(self, algorithm, path):
        try:
            logger.info(f"Generating video visualization for {algorithm}")
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = tempfile.mkdtemp()

            fig, ax = plt.subplots(figsize=(12, 8))
            pos = nx.get_node_attributes(self.graph, 'pos')

            def update(frame):
                ax.clear()
                nx.draw(self.graph, pos, with_labels=True, labels=nx.get_node_attributes(self.graph, 'name'),
                        node_color='lightblue', node_size=2000, font_size=8, ax=ax)  # Increased node_size to 1000

                path_edges = path[:frame + 1]
                nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='r', width=2)

                if frame < len(path):
                    current_node = path[frame][1]
                    nx.draw_networkx_nodes(self.graph, pos, nodelist=[current_node],
                                           node_color='g', node_size=2100)  # Increased node_size to 1400

                ax.set_title(f"{algorithm} - Step {frame + 1}/{len(path)}")

            anim = animation.FuncAnimation(fig, update, frames=len(path), repeat=False, interval=1000)

            video_path = os.path.join(self.temp_dir, 'tsp_animation.mp4')
            writer = animation.FFMpegWriter(fps=1, metadata=dict(artist='Me'), bitrate=1800)
            anim.save(video_path, writer=writer)

            plt.close(fig)

            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.play_pause()

            print(f"Video visualization generated and displayed")
            print(f"Video saved at: {video_path}")
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate video: {str(e)}")

    # def generate_video_visualization(self, algorithm, path):
    #     try:
    #         logger.info(f"Generating video visualization for {algorithm}")
    #         if self.temp_dir:
    #             shutil.rmtree(self.temp_dir, ignore_errors=True)
    #         self.temp_dir = tempfile.mkdtemp()
    #
    #         fig, ax = plt.subplots(figsize=(12, 8))
    #         pos = nx.get_node_attributes(self.graph, 'pos')
    #
    #         def update(frame):
    #             ax.clear()
    #             nx.draw(self.graph, pos, with_labels=True, labels=nx.get_node_attributes(self.graph, 'name'),
    #                     node_color='lightblue', node_size=500, font_size=8, ax=ax)
    #
    #             path_edges = path[:frame + 1]
    #             nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='r', width=2)
    #
    #             if frame < len(path):
    #                 current_node = path[frame][1]
    #                 nx.draw_networkx_nodes(self.graph, pos, nodelist=[current_node], node_color='g', node_size=700)
    #
    #             ax.set_title(f"{algorithm} - Step {frame + 1}/{len(path)}")
    #
    #         anim = animation.FuncAnimation(fig, update, frames=len(path), repeat=False, interval=1000)
    #
    #         video_path = os.path.join(self.temp_dir, 'tsp_animation.mp4')
    #         writer = animation.FFMpegWriter(fps=1, metadata=dict(artist='Me'), bitrate=1800)
    #         anim.save(video_path, writer=writer)
    #
    #         plt.close(fig)
    #
    #         self.media_player.setSource(QUrl.fromLocalFile(video_path))
    #         self.play_pause()
    #
    #         print(f"Video visualization generated and displayed")
    #         print(f"Video saved at: {video_path}")
    #         # ... rest of the method ...
    #     except Exception as e:
    #         logger.error(f"Error generating video: {str(e)}")
    #         QMessageBox.critical(self, "Error", f"Failed to generate video: {str(e)}")

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

    def handle_media_error(self, error):
        error_msg = f"Media player error: {error}"
        logger.error(error_msg)
        QMessageBox.critical(self, "Media Error", error_msg)
    def set_position(self, position):
        self.media_player.setPosition(position)

    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)

    def update_position(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)

    def closeEvent(self, event):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().closeEvent(event)
