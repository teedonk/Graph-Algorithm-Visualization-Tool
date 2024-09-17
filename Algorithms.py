from manim import *
import networkx as nx
import json

# Load dataset
with open("london_tube_crowding_data/london_tube_crowding_sat.json") as file:
    data = json.load(file)

# Create graph
graph = nx.Graph()
for station, connections in data.items():
    for connected_station, details in connections.items():
        graph.add_edge(station, connected_station, weight=details["crowding"], line=details["line"])

# Define BFS function
def bfs_path(graph, start, end):
    try:
        return nx.shortest_path(graph, source=start, target=end)
    except nx.NetworkXNoPath:
        return None

# Find path using BFS between Kensington (Olympia) and Woodford
start_station = "Kensington (Olympia) Underground Station"
end_station = "Woodford Underground Station"
path = bfs_path(graph, start_station, end_station)

# Manim Scene
class LondonTubeGraphScene(Scene):
    def __init__(self, graph, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.path = path

    def construct(self):
        # Create Graph for visualization
        vertices = list(self.graph.nodes())
        edges = list(self.graph.edges())

        # Create a Manim Graph
        g = Graph(
            vertices,
            [(e[0], e[1]) for e in edges],
            layout="spring",  # Automatically layout nodes
            layout_scale=3,   # Scale the layout to fit
            vertex_config={"fill_color": BLUE},
            edge_config={"stroke_color": GRAY}
        )

        # Highlight the BFS path
        if self.path:
            for i, node in enumerate(self.path):
                self.play(g[node].animate.set_fill(RED), run_time=0.5)

                # Highlight edges in the path
                if i > 0:
                    prev_node = self.path[i - 1]
                    if self.graph.has_edge(prev_node, node):
                        edge = g.edges[(prev_node, node)]
                        self.play(edge.animate.set_color(RED), run_time=0.5)

        # Add the graph to the scene
        self.add(g)
        self.wait(2)

# Run the Scene
if path:
    print(f"BFS Path from {start_station} to {end_station}: {path}")
    scene = LondonTubeGraphScene(graph, path)
    scene.render()
else:
    print(f"No path found between {start_station} and {end_station}")
