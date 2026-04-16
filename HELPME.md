# YouTube Pathfinder - User Documentation

A Selenium-based Python tool to search YouTube, collect recommended videos recursively, and visualize the video relationship graph.

## What It Does

1. Searches YouTube for videos matching a query
2. Collects initial videos from search results (depth=0)
3. For each depth level, visits videos and collects recommendations (depth=1, 2, etc.)
4. Builds a bidirectional graph showing video relationships
5. Creates visualizations (PDF or interactive HTML)

## Installation

### 1. Install Python
```bash
python3 --version  # Requires Python 3.7+
```

### 2. Install Chrome Driver
Download ChromeDriver matching your Chrome version:
- Check Chrome version: Chrome → Menu → Help → About Google Chrome
- Download from: https://chromedriver.chromium.org/downloads
- Extract and add to PATH, or place in project directory

### 3. Install Dependencies
```bash
pip install selenium networkx matplotlib
pip install pyvis  # For interactive visualization
```

## Configuration

Edit `settings.py`:

```python
MAX_INITIAL = 1           # Number of videos from initial search
MAX_RECOMMENDATIONS = 2   # Recommendations per video
DEPTH = 4                 # Recursion depth (1 = initial only, 2 = +depth1 recs, etc.)
SEARCH_QUERY = "your search query"
OUTPUT_FILE = "youtube_results.csv"
```

## Running

```bash
python3 youtube_search.py
```

## Output Format

The script creates `youtube_results.csv` with columns:

| Column | Description |
|--------|-------------|
| title | Video title |
| channel | YouTube channel name |
| views | View count |
| url | Video URL |
| depth | 0 for initial search, 1+ for recommendations |
| recommended_from | Title of video it was recommended from, or "initial" |

## Commands

### Search and Scrape
```bash
python3 youtube_search.py
```

### Create Graph from CSV
```bash
python3 youtube_create_graph.py                    # uses youtube_results.csv
python3 youtube_create_graph.py custom.csv       # custom input
```

### Static Visualization (matplotlib)
```bash
python3 youtube_visualize_map.py                  # creates youtube_graph.pdf
python3 youtube_visualize_map.py input.csv output.pdf
```

### Interactive Visualization (PyVis)
```bash
python3 youtube_visualize_pyvis.py                # creates youtube_graph.html
python3 youtube_visualize_pyvis.py input.csv output.html
```

## Files

- `settings.py` - Configuration
- `youtube_search.py` - Main scraping script
- `youtube_results.csv` - Output CSV
- `youtube_node.py` - Node data structure
- `youtube_graph.py` - Graph data structure
- `youtube_create_graph.py` - Create graph from CSV
- `youtube_visualize_map.py` - matplotlib visualization (PDF)
- `youtube_visualize_pyvis.py` - PyVis visualization (HTML)
- `youtube_enrich_data.py` - Add YouTube API data to CSV
- `youtube_graph.pdf` - Generated PDF visualization
- `youtube_graph.html` - Generated interactive visualization

## How It Works

1. **Initial Search**: Opens YouTube search results, scrolls to load videos, extracts info via JavaScript
2. **Recommendations**: Visits each video, finds links in sidebar, filters timestamps/chapters
3. **Depth Tracking**: depth=0 (initial), depth=1 (from depth 0), depth=2 (from depth 1), etc.
4. **Bidirectional Links**: Each node tracks both children (recommended videos) and parents (videos that recommended it)
5. **Multiple Parents**: A video can be recommended by multiple different videos

## Troubleshooting

### No recommendations found
- YouTube loads recommendations dynamically
- Some videos may not have visible recommendations
- Requires internet connection to YouTube

### Chrome driver issues
- Ensure ChromeDriver version matches your Chrome version
- On macOS, may need to allow in System Preferences → Security & Privacy

### Numeric/bad titles in CSV
- Run the search fresh - filters remove numeric-only titles like "128", "17", etc.
- Can manually clean CSV by removing rows where title is purely numeric

## Enrich Data with YouTube API

Add category_id, tags, and thumbnail_url using YouTube Data API:

```bash
export YOUTUBE_API_KEY="your_api_key"
python3 youtube_enrich_data.py                    # enriches youtube_results.csv
python3 youtube_enrich_data.py input.csv          # custom input
python3 youtube_enrich_data.py input.csv output.csv  # custom output
```

Get API key from: https://console.cloud.google.com/apis/credentials

New columns added:
- category_id - Video category (e.g., 24 = Entertainment)
- tags - Comma-separated video tags  
- thumbnail_url - URL to best quality thumbnail