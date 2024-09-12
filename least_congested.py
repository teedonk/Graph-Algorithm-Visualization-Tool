from PyQt6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QProgressDialog, QMainWindow, QLabel, QVBoxLayout, QWidget, QMenuBar, QMenu,
                             QPushButton, QStyle, QSlider, QMessageBox, QSpinBox, QHBoxLayout, QComboBox, QToolTip, QStackedWidget)
from PyQt6.QtGui import QAction, QPainter,QImage, QFont, QIcon, QPixmap, QDesktopServices
from PyQt6.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
import tempfile
import os
import networkx as nx
import shutil
import matplotlib.pyplot as plt
import traceback
import matplotlib.animation as animation
import json
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend which doesn't require a GUI
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from queue import PriorityQueue

class LondonTubeVisualizationPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.graph = None
        self.paths = []
        self.temp_dir = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left panel for controls (2/6 of the screen width)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(self.width() * 2 // 6)

        title = QLabel("London Tube Least Congested Path")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(title)

        # Day selection
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        left_layout.addWidget(QLabel("Select Day:"))
        left_layout.addWidget(self.day_combo)
        self.day_combo.currentTextChanged.connect(self.load_data)

        # Starting station selection
        self.start_station_combo = QComboBox()
        left_layout.addWidget(QLabel("Starting Station:"))
        left_layout.addWidget(self.start_station_combo)

        # Ending station selection
        self.end_station_combo = QComboBox()
        left_layout.addWidget(QLabel("Ending Station:"))
        left_layout.addWidget(self.end_station_combo)

        # Search for path button
        self.search_button = QPushButton("Search for Path")
        self.search_button.clicked.connect(self.search_path)
        left_layout.addWidget(self.search_button)

        # Path count display
        self.path_count_label = QLabel("Paths found: 0")
        left_layout.addWidget(self.path_count_label)

        # Graph algorithm selection
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(
            ["Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Dijkstra's Algorithm", "A* Algorithm"])
        left_layout.addWidget(QLabel("Graph Algorithm:"))
        left_layout.addWidget(self.algorithm_combo)

        # Visualize button
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.clicked.connect(self.visualize)
        left_layout.addWidget(self.visualize_button)

        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # Right panel for visualization (4/6 of the screen width)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Stacked widget to switch between image and video
        self.stacked_widget = QStackedWidget()
        right_layout.addWidget(self.stacked_widget, 7)

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

        main_layout.addWidget(right_panel, 4)  # 4/6 of the total width

        self.setLayout(main_layout)

        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.errorOccurred.connect(self.handle_media_error)

    def load_data(self):
        day = self.day_combo.currentText().lower()[:3]  # Get first 3 letters of the day
        file_path = f'london_tube_crowding_data/london_tube_crowding_{day}.json'

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            self.graph = nx.Graph()  # Use undirected graph
            for station, connections in data.items():
                # Remove " Underground Station" from station names
                station_name = station.replace(" Underground Station", "")
                for connected_station, details in connections.items():
                    connected_station_name = connected_station.replace(" Underground Station", "")
                    self.graph.add_edge(station_name, connected_station_name,
                                        weight=details['crowding'],
                                        line=details['line'])

            print(
                f"Loaded data for {day.capitalize()}. Graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

            # Update station lists
            stations = list(self.graph.nodes())
            self.start_station_combo.clear()
            self.end_station_combo.clear()
            self.start_station_combo.addItems(stations)
            self.end_station_combo.addItems(stations)
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            QMessageBox.critical(self, "Error", f"Data file for {day.capitalize()} not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file - {file_path}")
            QMessageBox.critical(self, "Error", f"Invalid data in file for {day.capitalize()}.")
    def search_path(self):
        if self.graph is None:
            QMessageBox.warning(self, "Warning", "Please select a day to load data first.")
            return

        start = self.start_station_combo.currentText()
        end = self.end_station_combo.currentText()

        if start == end:
            QMessageBox.warning(self, "Warning", "Start and end stations are the same.")
            return

        try:
            # Use networkx to find all simple paths
            self.paths = list(nx.all_simple_paths(self.graph, start, end))
            path_count = len(self.paths)
            self.path_count_label.setText(f"Paths found: {path_count}")
            print(f"Found {path_count} paths from {start} to {end}")
        except nx.NetworkXNoPath:
            self.paths = []
            self.path_count_label.setText("Paths found: 0")
            QMessageBox.warning(self, "No Path", "No path found between the selected stations.")


    def find_least_congested_path(self, start, end, algorithm):
        if algorithm in ["Dijkstra's Algorithm", "A* Algorithm"]:
            return self.least_congested_path(start, end)
        elif algorithm == "Breadth-First Search (BFS)":
            return self.bfs_path(start, end)
        elif algorithm == "Depth-First Search (DFS)":
            return self.dfs_path(start, end)

    def bfs_path(self, start, end):
        queue = [(start, [start])]
        visited = set()
        while queue:
            (vertex, path) = queue.pop(0)
            if vertex not in visited:
                if vertex == end:
                    return path
                visited.add(vertex)
                for neighbor in self.graph.neighbors(vertex):
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
        return None

    def dfs_path(self, start, end):
        stack = [(start, [start])]
        visited = set()
        while stack:
            (vertex, path) = stack.pop()
            if vertex not in visited:
                if vertex == end:
                    return path
                visited.add(vertex)
                for neighbor in self.graph.neighbors(vertex):
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))
        return None

    def least_congested_path(self, start, end):
        pq = PriorityQueue()
        pq.put((0, [start]))
        visited = set()

        while not pq.empty():
            (max_congestion, path) = pq.get()
            node = path[-1]

            if node == end:
                return path

            if node not in visited:
                visited.add(node)

                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        new_path = path + [neighbor]
                        edge_congestion = self.graph[node][neighbor]['weight']
                        new_max_congestion = max(max_congestion, edge_congestion)
                        pq.put((new_max_congestion, new_path))

        return None  # No path found
    def create_animation(self, G, path, algorithm):
        pos = nx.spring_layout(G)
        fig, ax = plt.subplots(figsize=(12, 8))

        def update(frame):
            ax.clear()
            nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, ax=ax)

            # Draw the path up to the current frame
            path_edges = list(zip(path[:frame + 1], path[1:frame + 2]))
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)

            # Highlight current node
            if frame < len(path):
                nx.draw_networkx_nodes(G, pos, nodelist=[path[frame]], node_color='r', node_size=700)

            ax.set_title(f"{algorithm} - Step {frame + 1}/{len(path)}")

        # Use PillowWriter instead of FFMpegWriter
        writer = PillowWriter(fps=1)
        anim = FuncAnimation(fig, update, frames=len(path), repeat=False, interval=1000)

        # Save as GIF instead of MP4
        video_path = os.path.join(self.temp_dir, 'tube_animation.gif')
        anim.save(video_path, writer=writer)

        plt.close(fig)  # Prevent showing the plot immediately
        return video_path


    def generate_video_visualization(self, algorithm, path):
        try:
            # Create a subgraph containing only the nodes and edges in the path
            subgraph = nx.Graph()
            for i in range(len(path) - 1):
                if self.graph.has_edge(path[i], path[i+1]):
                    subgraph.add_edge(path[i], path[i+1], **self.graph[path[i]][path[i+1]])
                else:
                    print(f"Warning: No direct connection between {path[i]} and {path[i+1]}")

            fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
            pos = nx.spring_layout(subgraph, k=1.5, iterations=50)

            def update(frame):
                ax.clear()
                nx.draw(subgraph, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, ax=ax)

                path_edges = list(zip(path[:frame + 1], path[1:frame + 1]))
                nx.draw_networkx_edges(subgraph, pos, edgelist=path_edges, edge_color='r', width=2, ax=ax)

                if frame < len(path):
                    nx.draw_networkx_nodes(subgraph, pos, nodelist=[path[frame]], node_color='g', node_size=3500, ax=ax)

                nx.draw_networkx_nodes(subgraph, pos, nodelist=[path[0], path[-1]], node_color='y', node_size=3500, ax=ax)

                edge_labels = {}
                for (u, v, data) in subgraph.edges(data=True):
                    if algorithm in ["Dijkstra's Algorithm", "A* Algorithm"]:
                        edge_labels[(u, v)] = f"{data.get('line', 'N/A')}\n(Congestion: {data.get('weight', 'N/A')})"
                    else:
                        edge_labels[(u, v)] = data.get('line', 'N/A')
                nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_size=8)

                ax.set_title(f"{algorithm} - Step {frame + 1}/{len(path)}")

            anim = animation.FuncAnimation(fig, update, frames=len(path), repeat=False, interval=1000)

            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = tempfile.mkdtemp()
            video_path = os.path.join(self.temp_dir, 'tube_animation.mp4')

            writer = animation.FFMpegWriter(fps=1, metadata=dict(artist='Me'), bitrate=1800)
            anim.save(video_path, writer=writer)

            plt.close(fig)

            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.stacked_widget.setCurrentWidget(self.video_widget)
            self.play_pause()

            print(f"Video visualization generated and displayed")
            print(f"Video saved at: {video_path}")

        except Exception as e:
            error_msg = f"An error occurred during video visualization:\n\n{str(e)}\n\nStack Trace:\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def visualize(self):
        if not self.paths:
            QMessageBox.warning(self, "Warning", "Please search for paths first.")
            return

        algorithm = self.algorithm_combo.currentText()
        start = self.start_station_combo.currentText()
        end = self.end_station_combo.currentText()

        print(f"Visualizing path from {start} to {end} using {algorithm}")

        try:
            path = self.find_least_congested_path(start, end, algorithm)
            if path:
                print(f"Selected path: {path}")
                if algorithm in ["Dijkstra's Algorithm", "A* Algorithm"]:
                    max_congestion = max(self.graph[path[i]][path[i+1]]['weight'] for i in range(len(path)-1) if self.graph.has_edge(path[i], path[i+1]))
                    print(f"Maximum congestion along the path: {max_congestion:.2f}")
                self.generate_video_visualization(algorithm, path)
            else:
                QMessageBox.warning(self, "No Path", "No path found between the selected stations.")
        except Exception as e:
            print(f"Error in visualize method: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred during visualization: {str(e)}")

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
        self.media_player.setPosition(max(0, self.media_player.position() - 1000))  # Move back 1 second

    def forward(self):
        self.media_player.setPosition(
            min(self.media_player.duration(), self.media_player.position() + 1000))  # Move forward 1 second

    def replay(self):
        self.media_player.setPosition(0)
        self.media_player.play()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_media_error(self, error):
        error_msg = f"Media player error: {error}"
        print(error_msg)
        QMessageBox.critical(self, "Media Error", error_msg)

    def update_duration(self, duration):
        try:
            self.progress_slider.setRange(0, duration)
        except Exception as e:
            print(f"Error in update_duration: {str(e)}")

    def update_position(self, position):
        try:
            if not self.progress_slider.isSliderDown():
                self.progress_slider.setValue(position)
        except Exception as e:
            print(f"Error in update_position: {str(e)}")

    def closeEvent(self, event):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        super().closeEvent(event)
    def correct_path(self, path):
        corrected_path = [path[0]]
        for i in range(1, len(path)):
            current = corrected_path[-1]
            next_station = path[i]
            if self.graph.has_edge(current, next_station):
                corrected_path.append(next_station)
            else:
                # Find a path between current and next_station
                try:
                    intermediate_path = nx.shortest_path(self.graph, current, next_station)
                    corrected_path.extend(intermediate_path[1:])
                except nx.NetworkXNoPath:
                    print(f"No path found between {current} and {next_station}")
                    # Instead of continuing, we'll add the next_station and handle the disconnection visually
                    corrected_path.append(next_station)
        return corrected_path

    def show_loading_indicator(self):
        self.loading_dialog = QProgressDialog("Generating visualization...", None, 0, 0, self)
        self.loading_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.loading_dialog.setWindowTitle("Please Wait")
        self.loading_dialog.setCancelButton(None)
        self.loading_dialog.setAutoClose(True)
        self.loading_dialog.setMinimumDuration(0)
        self.loading_dialog.show()
        QTimer.singleShot(200, lambda: self.loading_dialog.setValue(0))

    def hide_loading_indicator(self):
        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None


