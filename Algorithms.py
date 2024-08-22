import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import heapq
import random

# Create a sample graph
G = nx.Graph()
edges = [
    ('A', 'B', 4), ('A', 'C', 2), ('B', 'D', 3), ('B', 'E', 1),
    ('C', 'D', 5), ('C', 'F', 6), ('D', 'E', 2), ('E', 'F', 4)
]
G.add_weighted_edges_from(edges)

# Position nodes for consistent layout
pos = nx.spring_layout(G)

# Visualize the graph
plt.figure(figsize=(12, 8))
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=16, font_weight='bold')
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title("Sample Graph", fontsize=20)
plt.axis('off')
plt.show()


# Breadth-First Search
def bfs(graph, start, goal):
    queue = deque([[start]])
    visited = set([start])

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal:
            return path

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None

# Depth-First Search
def dfs(graph, start, goal, path=None):
    if path is None:
        path = [start]

    if start == goal:
        return path

    for neighbor in graph[start]:
        if neighbor not in path:
            new_path = dfs(graph, neighbor, goal, path + [neighbor])
            if new_path:
                return new_path

    return None


# Dijkstra's Algorithm
def dijkstra(graph, start, goal):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    previous = {node: None for node in graph}

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_node == goal:
            path = []
            while current_node:
                path.append(current_node)
                current_node = previous[current_node]
            return path[::-1]

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight['weight']
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    return None


# A* Algorithm
def heuristic(a, b):
    # Using Euclidean distance as a simple heuristic
    return ((pos[a][0] - pos[b][0]) ** 2 + (pos[a][1] - pos[b][1]) ** 2) ** 0.5


def a_star(graph, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, goal)

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor, weight in graph[current].items():
            tentative_g_score = g_score[current] + weight['weight']
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None


# Function to visualize path
def visualize_path(G, pos, path, algorithm_name):
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=16, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)

    start_node = path[0] if path else ''
    goal_node = path[-1] if path else ''
    plt.title(f"{algorithm_name} - Path from {start_node} to {goal_node}", fontsize=20)
    plt.axis('off')
    plt.show()

def generate_graph(num_nodes):
    nodes = [chr(i) for i in range(65, 65 + num_nodes)]
    G = nx.Graph()

    # Add all nodes to the graph
    G.add_nodes_from(nodes)

    # Ensure the graph is connected
    for i in range(1, len(nodes)):
        G.add_edge(nodes[i - 1], nodes[i], weight=random.randint(1, 10))

    # Add random additional edges
    for _ in range(num_nodes):
        node1, node2 = random.sample(nodes, 2)
        if node1 != node2 and not G.has_edge(node1, node2):
            G.add_edge(node1, node2, weight=random.randint(1, 10))

    # Position nodes for visualization
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    return G, pos