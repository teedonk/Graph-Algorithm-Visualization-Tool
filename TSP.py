# import csv
# import os
#
# # File name
# file_name = 'tiny.csv'
#
# # Check if the file exists in the current directory
# if not os.path.exists(file_name):
#     raise FileNotFoundError(f"The file {file_name} does not exist in the current directory.")
#
# # List to store coordinates
# coordinates = []
#
# # Read the CSV file
# with open(file_name, 'r') as file:
#     csv_reader = csv.reader(file)
#     for row in csv_reader:
#         # Convert string coordinates to float
#         x = float(row[0])
#         y = float(row[1])
#         coordinates.append((x, y))
#
# # List of city names (in the same order as the coordinates)
# city_names = [
#     "Bluewater Bay",
#     "Sunhaven",
#     "Highpoint",
#     "Frostholm",
#     "Midvale",
#     "Eastharbor",
#     "Northpeak",
#     "Skyridge",
#     "Greenmeadow",
#     "Westbrook"
# ]
#
# # Create the dictionary mapping coordinates to city names
# city_coordinates = {tuple(coord): name for coord, name in zip(coordinates, city_names)}
#
# # Print the resulting dictionary
# for coord, name in city_coordinates.items():
#     print(f"{name}: {coord}")
#
import networkx as nx
import matplotlib.pyplot as plt
import math

# Assuming we have the city_coordinates dictionary from the previous script
city_coordinates = {
    "Bluewater Bay": (-1.08563060, -0.67888615),
    "Sunhaven": (0.99734545, -0.09470897),
    "Highpoint": (0.28297850, 1.49138963),
    "Frostholm": (-1.50629471, -0.63890200),
    "Midvale": (-0.57860025, -0.44398196),
    "Eastharbor": (1.65143654, -0.43435128),
    "Northpeak": (-2.42667924, 2.20593008),
    "Skyridge": (-0.42891263, 2.18678609),
    "Greenmeadow": (1.26593626, 1.00405390),
    "Westbrook": (-0.86674040, 0.38618640)
}

# Create a graph
G = nx.Graph()

# Add nodes with their positions
for city, coords in city_coordinates.items():
    G.add_node(city, pos=coords)

# Add edges (connecting all cities for this example)
for city1 in city_coordinates:
    for city2 in city_coordinates:
        if city1 != city2:
            dist = math.sqrt(sum((city_coordinates[city1][i] - city_coordinates[city2][i]) ** 2 for i in range(2)))
            G.add_edge(city1, city2, weight=dist)


# Function to visualize the graph
def visualize_graph(G, path=None, title="City Graph"):
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8)

    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# 1. Breadth-First Search (BFS)
def bfs_path(G, start, end):
    return nx.bfs_edges(G, source=start)


bfs_result = list(bfs_path(G, "Bluewater Bay", "Eastharbor"))
bfs_path = ["Bluewater Bay"] + [v for u, v in bfs_result]
visualize_graph(G, bfs_path, "BFS from Bluewater Bay")


# 2. Depth-First Search (DFS)
def dfs_path(G, start, end):
    return nx.dfs_edges(G, source=start)


dfs_result = list(dfs_path(G, "Bluewater Bay", "Eastharbor"))
dfs_path = ["Bluewater Bay"] + [v for u, v in dfs_result]
visualize_graph(G, dfs_path, "DFS from Bluewater Bay")

# 3. Dijkstra's Algorithm
dijkstra_path = nx.dijkstra_path(G, "Bluewater Bay", "Eastharbor", weight='weight')
visualize_graph(G, dijkstra_path, "Dijkstra's Shortest Path from Bluewater Bay to Eastharbor")


# 4. Nearest Neighbor Algorithm
def nearest_neighbor(G, start):
    path = [start]
    unvisited = set(G.nodes()) - {start}

    while unvisited:
        current = path[-1]
        next_city = min(unvisited, key=lambda city: G[current][city]['weight'])
        path.append(next_city)
        unvisited.remove(next_city)

    return path


nn_path = nearest_neighbor(G, "Bluewater Bay")
visualize_graph(G, nn_path, "Nearest Neighbor Path from Bluewater Bay")