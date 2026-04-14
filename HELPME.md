# YouTube Video Scraper

A Selenium-based Python script to search YouTube and collect recommended videos.

## What It Does

1. Searches YouTube for videos matching a query
2. Collects initial videos from search results (depth=0)
3. For each depth level, visits videos and collects recommendations (depth=1, 2, etc.)
4. Saves results to a CSV file with trackable depth and source
5. Can create a graph visualization from the CSV

## Installation

### 1. Install Python
Make sure you have Python 3.7+ installed:
```bash
python3 --version
```

### 2. Install Chrome Driver
Download ChromeDriver matching your Chrome version:
- Check Chrome version: Open Chrome → Menu → Help → About Google Chrome
- Download from: https://chromedriver.chromium.org/downloads
- Extract and add to PATH, or place in project directory

### 3. Install Dependencies
```bash
pip install selenium
```

(Selenium should already be installed - this just confirms)

## Configuration

Edit `settings.py` to customize:

```python
# Settings for youtube_search.py

MAX_INITIAL = 3              # Number of videos from initial search
MAX_RECOMMENDATIONS = 3        # Recommendations per video
DEPTH = 2                   # Recursion depth (1 = initial only, 2 = depth-1 recs get recs, etc.)
SEARCH_QUERY = "python tutorials"  # Your search query
OUTPUT_FILE = "youtube_results.csv"  # Output filename
```

## Running

```bash
python3 youtube_search.py
```

## Output

The script creates `youtube_results.csv` with these columns:

| Column | Description |
|--------|-------------|
| title | Video title |
| channel | YouTube channel name |
| views | View count |
| url | Video URL |
| depth | 0 for initial search, 1+ for recommendations |
| recommended_from | Title of video it was recommended from, or "initial" |

## Example Output

```csv
title,channel,views,url,depth,recommended_from
Python Tutorial for Beginners,CodeWithHarry,18M views,https://www.youtube.com/watch?v=...,0,initial
SQL Tutorial for Beginners,somechannel,1M views,https://www.youtube.com/watch?v=...,1,Python Tutorial for Beginners
```

## How It Works

1. **Initial Search**: Opens YouTube search results page, scrolls to load all videos, extracts video info using JavaScript
2. **Recommendations**: Visits each video page, finds links in the "Up next" sidebar, filters out chapters/timestamps
3. **Depth Tracking**: 
   - depth=0: Videos from initial search
   - depth=1: Videos recommended from depth=0 videos
4. **Deduplication**: Prevents same URL from being added multiple times from the same source video

## Troubleshooting

### "command not found: python"
Use `python3` instead of `python`:
```bash
python3 youtube_search.py
```

### No recommendations found
- YouTube loads recommendations dynamically - the script attempts to scroll to trigger loading
- Some videos may not have visible recommendations
- The script requires internet connection to YouTube

### Chrome driver issues
- Ensure ChromeDriver version matches your Chrome version
- On macOS, you may need to allow the driver in System Preferences → Security & Privacy

## Files

- `youtube_search.py` - Main script
- `settings.py` - Configuration settings
- `youtube_results.csv` - Output file (generated)
- `youtube_node.py` - Node data structure for graph
- `youtube_graph.py` - Graph data structure
- `youtube_create_graph.py` - Create graph from CSV
- `youtube_visualize_map.py` - Create visualization (PDF)
- `youtube_graph.pdf` - Visualization output (generated)
- `HELPME.md` - This file

## Graph Visualization

Create a graph from the CSV results:

```bash
python3 youtube_create_graph.py                    # uses youtube_results.csv
python3 youtube_create_graph.py some_file.csv        # uses custom CSV file
```

This creates a bidirectional graph showing:
- Head nodes (depth 0, initial search results)
- Recommendations by depth level
- Links between parent and child videos

## Visualization

Create a PDF visualization of the graph:

```bash
python3 youtube_visualize_map.py                    # uses youtube_results.csv, saves youtube_graph.pdf
python3 youtube_visualize_map.py input.csv     # custom input file
python3 youtube_visualize_map.py input.csv output.pdf  # custom output
```

This creates a hierarchical visualization:
- Nodes colored by depth level
- Arrows showing parent → child relationships
- Saved as PDF (youtube_graph.pdf by default)