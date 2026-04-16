# YouTube Pathfinder - Agent Instructions

## Quick Start
```bash
python3 youtube_search.py
```

## Settings (settings.py)
- `MAX_INITIAL`: Number of videos from initial search
- `MAX_RECOMMENDATIONS`: Recommendations per video
- `DEPTH`: Recursion depth (1 = initial only, 2+ = recursive recommendations)
- `SEARCH_QUERY`: YouTube search term
- `OUTPUT_FILE`: CSV output filename

## Commands

### Search and Scrape
```bash
python3 youtube_search.py
```

### Create Graph from CSV
```bash
python3 youtube_create_graph.py                    # uses youtube_results.csv
python3 youtube_create_graph.py custom.csv     # custom input
```

### Static Visualization (matplotlib)
```bash
python3 youtube_visualize_map.py                    # creates youtube_graph.pdf
python3 youtube_visualize_map.py input.csv output.pdf
```

### Interactive Visualization (PyVis)
```bash
python3 youtube_visualize_pyvis.py                   # creates youtube_graph.html
python3 youtube_visualize_pyvis.py input.csv output.html
```

### Enrich Data with YouTube API
```bash
export YOUTUBE_API_KEY="your_api_key"
python3 youtube_enrich_data.py                     # enriches youtube_results.csv
python3 youtube_enrich_data.py input.csv output.csv  # custom input/output
```
Adds: category_id, tags, thumbnail_url

## YouTube Scraping Quirks
- Uses Selenium with JavaScript parsing
- Video page recommendations in `#secondary`, `#related` containers
- Filters out timestamps, chapters, lesson counts
- Uses `innerText` not `textContent` for YouTube elements

## Data Structure
- `youtube_node.py` - Node class (title, channel, views, depth, link, children, parents)
- `youtube_graph.py` - Graph class with bidirectional links

## Graph Properties
- Head nodes = depth 0 (initial search results)
- children = recommendations from this video
- parents = videos that recommended this one
- Multiple parents supported (video can be recommended by multiple sources)

## Files
- `settings.py` - Configuration
- `youtube_search.py` - Main scraping script
- `youtube_results.csv` - Output CSV
- `youtube_enrich_data.py` - Enrich CSV with YouTube API
- `youtube_node.py` - Node data structure
- `youtube_graph.py` - Graph data structure
- `youtube_create_graph.py` - Graph CLI
- `youtube_visualize_map.py` - matplotlib visualization
- `youtube_visualize_pyvis.py` - PyVis interactive visualization
- `HELPME.md` - User documentation
- `README.md` - Project overview