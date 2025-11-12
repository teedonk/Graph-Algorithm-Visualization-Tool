# Graph-Algorithm-Visualization-Tool

A desktop application for visualizing graph algorithms on real-world network problems. Built with PyQt6 and NetworkX, this tool demonstrates how different pathfinding algorithms work through animated visualizations.

## Features

The application includes two main visualization modules:

**London Tube Least Congested Path**
- Finds optimal routes through the London Underground network considering crowding levels
- Supports multiple days of the week with different crowding patterns
- Visualizes paths using BFS, DFS, Dijkstra's Algorithm, and A* Algorithm
- Shows step-by-step animated traversal with congestion weights

**Traveling Salesman Problem**
- Solves TSP for a set of cities with geographic coordinates
- Compares different graph traversal and pathfinding algorithms
- Generates animated visualizations showing the route progression
- Displays city names and calculates path distances

## Supported Algorithms

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Dijkstra's Algorithm
- A* Algorithm

## Requirements

- Python 3.x
- PyQt6
- NetworkX
- Matplotlib
- NumPy
- FFmpeg (for video generation)

## Installation

Install required packages:

```bash
pip install PyQt6 networkx matplotlib numpy
```

Install FFmpeg for video generation. On Windows, download from ffmpeg.org and add to system PATH.

## Usage

Run the main application:

```bash
python main.py
```

For standalone examples:

- London Tube visualization: `python least_congested.py`
- TSP visualization: `python Traveling_salesman.py`
- Basic algorithm examples: `python TSP.py`

## Data Files

The application requires:
- `london_tube_crowding_data/` directory with JSON files for each day of the week
- `tiny.csv` file containing city coordinates for TSP problem

## How It Works

1. Select an algorithm from the dropdown menu
2. For London Tube: choose a day, starting station, and ending station
3. Click "Search for Path" to find available routes
4. Click "Visualize" to generate an animated video showing the algorithm in action
5. Use playback controls to play, pause, stop, or replay the visualization
