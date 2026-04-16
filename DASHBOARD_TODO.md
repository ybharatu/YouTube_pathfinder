# YouTube Pathfinder Dashboard - TODO

## Phase 1: Core Features (This Implementation)

### Views Analysis Tab
- [x] Bar chart: Average views by depth level
- [x] Line chart: Views trend as depth increases
- [x] Histogram: Distribution of views at each depth
- [x] Sidebar filters: min/max depth, view count range

### Category Analysis Tab
- [x] Pie charts: Category distribution at each depth
- [x] Stacked bar: Categories by depth
- [x] Category ID to name mapping

### Network Map Tab
- [x] Interactive network visualization
- [x] Nodes colored by depth
- [x] Node size by view count
- [x] Filter by depth level

### General
- [x] Read from enriched CSV
- [x] Sidebar with global filters
- [x] Download data button

---

## Phase 2: Enhanced Features (Future)

### Views Analysis
- [ ] Box plots: View distribution by depth
- [ ] Scatter plot: Views vs depth with channel colors
- [ ] View count growth/decay analysis
- [ ] Top performing videos at each depth

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