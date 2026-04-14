# AGENTS.md

## Run Command
```bash
python3 youtube_search.py
```

## Settings (settings.py)
- `MAX_INITIAL`: Videos from search
- `MAX_RECOMMENDATIONS`: Recommendations per video  
- `DEPTH`: Recursion depth (1 = initial only, 2 = depth-1 recs get recs, etc.)
- `SEARCH_QUERY`: YouTube search term
- `OUTPUT_FILE`: CSV output filename

## YouTube HTML Quirks
- YouTube uses custom elements (`ytd-video-renderer`, `ytLockupViewModelHost`)
- Video page recommendations are in `#secondary`, `#related` containers
- Many links are chapters/timestamps from video descriptions - must filter these out
- Use `innerText` not `textContent` for YouTube elements

## Depth Recursion
The script collects recursively:
- depth 0 = initial search results
- depth 1 = recommendations from depth 0 videos
- depth 2 = recommendations from depth 1 videos, etc.

## Dependencies
- Selenium
- ChromeDriver matching Chrome version

## Files
- `settings.py` - Configuration
- `youtube_search.py` - Main script
- `youtube_results.csv` - Output
- `HELPME.md` - User documentation