# YouTube Pathfinder

A Python tool to search YouTube, collect recommended videos recursively at multiple depth levels, and visualize the video relationship graph.

![YouTube Pathfinder](./youtube_graph.png)

## Features

- **Recursive Video Collection**: Scrape YouTube search results and their recommendations at multiple depth levels
- **Bidirectional Graph**: Each video knows what recommended it and what it recommends
- **Multiple Parents Support**: A video can be recommended by multiple different videos
- **Static Visualization**: PDF output with hierarchical layout colored by depth
- **Interactive Visualization**: HTML output with draggable, zoomable network graph

## Quick Start

```bash
# Install dependencies
pip install selenium networkx matplotlib pyvis

# Run search
python3 youtube_search.py

# Create graph
python3 youtube_create_graph.py

# Visualize (PDF)
python3 youtube_visualize_map.py

# Visualize (Interactive HTML)
python3 youtube_visualize_pyvis.py
```

## Installation

### Requirements
- Python 3.7+
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)

### Dependencies
```bash
pip install selenium networkx matplotlib pyvis
```

## Configuration

Edit `settings.py` to customize:

```python
MAX_INITIAL = 3              # Number of videos from initial search
MAX_RECOMMENDATIONS = 3      # Recommendations per video
DEPTH = 2                    # Recursion depth (1 = initial only, 2 = +depth1 recs, etc.)
SEARCH_QUERY = "python tutorials"
OUTPUT_FILE = "youtube_results.csv"
```

## Usage

### 1. Search and Scrape
```bash
python3 youtube_search.py
```
Creates `youtube_results.csv` with columns: title, channel, views, url, depth, recommended_from

### 2. Create Graph
```bash
python3 youtube_create_graph.py                    # uses youtube_results.csv
python3 youtube_create_graph.py custom.csv       # custom input
```
Outputs a text representation of the graph hierarchy

### 3. Static Visualization (PDF)
```bash
python3 youtube_visualize_map.py                 # creates youtube_graph.pdf
python3 youtube_visualize_map.py input.csv output.pdf
```
Creates a hierarchical PDF visualization with:
- Nodes colored by depth level
- Arrows showing parent → child relationships
- Legend for depth levels

### 4. Interactive Visualization (HTML)
```bash
python3 youtube_visualize_pyvis.py               # creates youtube_graph.html
python3 youtube_visualize_pyvis.py input.csv output.html
```
Creates an interactive HTML visualization:
- Drag nodes to reposition
- Zoom and pan
- Hover for video details
- Color coded by depth

## Depth Explanation

- **depth=0**: Initial search results
- **depth=1**: Videos recommended by depth=0 videos
- **depth=2**: Videos recommended by depth=1 videos
- ...and so on

The graph is bidirectional:
- `children` = videos recommended FROM this video
- `parents` = videos that recommended THIS video

## Project Structure

```
youtube_pathfinder/
├── settings.py                 # Configuration
├── youtube_search.py          # Main scraping script (Selenium)
├── youtube_search_api.py     # API-based search (DEPRECATED: related videos don't work)
├── youtube_results.csv        # Output data
├── youtube_results_enriched.csv # API-enriched output (initial only, no related)
├── youtube_node.py           # Node data structure
├── youtube_graph.py          # Graph data structure
├── youtube_create_graph.py   # Graph CLI tool
├── youtube_visualize_map.py  # matplotlib visualization
├── youtube_visualize_pyvis.py # PyVis visualization
├── youtube_dashboard.py      # Streamlit dashboard
├── youtube_graph.pdf         # Generated PDF
├── youtube_graph.html        # Generated HTML
├── AGENTS.md                 # Agent instructions
├── HELPME.md                 # User documentation
└── README.md                 # This file
```

## Important: API vs Selenium

### YouTube Data API (youtube_search_api.py)
- Uses official YouTube Data API v3
- **Works**: Initial search, video details (views, category, tags)
- **Does NOT work**: Related videos (endpoint deprecated Aug 2023)
- Requires: `export YOUTUBE_API_KEY="your_key"`
- Output: `youtube_results_enriched.csv` (depth 0 only)

### Selenium (youtube_search.py)
- Scrapes YouTube's website directly
- **Works**: Everything (initial search, related videos, all metadata)
- **Does NOT work**: None
- Requires: Chrome browser + ChromeDriver
- Output: `youtube_results.csv` (full depth levels)

**Recommendation**: Use `youtube_search.py` (Selenium) for full functionality.

## Examples

### Python Tutorials Search
With `SEARCH_QUERY = "python tutorials"`, `MAX_INITIAL = 3`, `MAX_RECOMMENDATIONS = 3`, `DEPTH = 2`:

```
Depth 0 (Initial):
- Python Full Course for free 🐍
- Learn Python in Only 30 Minutes
- Python Tutorial for Beginners in Hindi

Depth 1 (Recommendations from depth 0):
- → Python Full Course for free 🐍
- → Learn Python in 1 hour!
- → Start coding with PYTHON in 5 minutes!

Depth 2 (Recommendations from depth 1):
- → Every F-String Trick In Python Explained
- → Python Full Crash Course
- → Coding was hard until I learned this
```

## License

MIT