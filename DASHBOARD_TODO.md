# YouTube Pathfinder Dashboard - TODO

## Phase 1: Core Features (COMPLETED)

### Views Analysis Tab
- [x] Bar chart: Average views by depth level
- [x] Bar chart: Total views by depth level
- [x] Box plot: View distribution by depth
- [x] Line chart: Views trend as depth increases (mean + median)
- [x] Sidebar filters: depth selection

### Category Analysis Tab
- [x] Pie charts: Category distribution at each depth
- [x] Stacked bar: Categories by depth
- [x] Category ID to name mapping (fixed float/int parsing)
- [x] Per-depth category breakdown with pie charts
- [x] Consistent category colors across all charts
- [x] Category color legend

### Network Map Tab
- [x] Interactive network visualization (PyVis)
- [x] Nodes colored by depth
- [x] Node size by view count
- [x] Filter by depth level
- [x] Node limit (100 nodes max for performance)

### Data Tab
- [x] Metrics: Total Videos, Total Views, Max Depth, Unique Channels
- [x] Data table with all columns
- [x] Download filtered data as CSV
- [x] HTML table rendering (fixed pyarrow issue)

### General
- [x] Read from enriched CSV (file uploader)
- [x] Sidebar with global depth filters
- [x] Tab layout for different views
- [x] Category name mapping (from category_ids.txt + defaults)

---

## Phase 2: Enhanced Features (Future)

### Views Analysis
- [x] Box plots: View distribution by depth
- [x] Scatter plot: Views vs depth with channel colors
- [x] View count growth/decay analysis
- [x] Top performing videos at each depth
- [x] Histogram: Distribution of views at each depth

### Category Analysis
- [ ] Category transitions: How categories change parent→child
- [ ] Category correlation matrix
- [ ] Dominant category at each depth level

### Channel Analysis (New Tab)
- [ ] Top recommended channels by depth
- [ ] Channel Sankey diagram showing flow
- [ ] Channel reach analysis (how far channels propagate)
- [ ] Most influential channels (most recommendations)

### Network Enhancements
- [ ] Filter by category (show only selected categories)
- [ ] Filter by channel
- [ ] Highlight paths from specific video
- [ ] Export network to static image

### Dashboard Enhancements
- [ ] Dark/Light theme toggle
- [ ] Save dashboard state
- [ ] Shareable configurations
- [ ] Comparison mode (compare two different searches)

### Data Enrichment
- [ ] Add more API fields (likes, comments, duration)
- [ ] Sentiment analysis on titles
- [ ] Keyword extraction

---

## Notes
- Uses Streamlit for interactive dashboard
- Plotly for charts (exportable to HTML)
- PyVis-compatible network data
- Reads from youtube_results_enriched.csv (enriched with YouTube API)
- Category parsing: handles float IDs (27.0 → "27")
- Consistent category colors: Music=#1DB954, Entertainment=#FF6B6B, Science & Tech=#4ECDC4, etc.