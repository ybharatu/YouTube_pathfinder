import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pyvis.network import Network
import os


CATEGORY_NAMES = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '18': 'Short Movies',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '21': 'Videoblogging',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
    '30': 'Movies',
    '31': 'Anime/Animation',
    '32': 'Action/Adventure',
    '33': 'Classics',
    '34': 'Comedy',
    '35': 'Documentary',
    '36': 'Drama',
    '37': 'Family',
    '38': 'Foreign',
    '39': 'Horror',
    '40': 'Sci-Fi/Fantasy',
    '41': 'Thriller',
    '42': 'Shorts',
    '43': 'Shows',
    '44': 'Trailers',
}

def load_category_names():
    """Load category names from file"""
    try:
        with open('category_ids.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    CATEGORY_NAMES[parts[0]] = parts[1]
    except FileNotFoundError:
        pass

load_category_names()


def load_data(csv_file):
    """Load and prepare the CSV data"""
    df = pd.read_csv(csv_file)
    
    def parse_views(view_str):
        if pd.isna(view_str) or view_str == '':
            return 0
        view_str = str(view_str).lower().replace(',', '').replace(' views', '').replace('view', '')
        try:
            if 'k' in view_str:
                return float(view_str.replace('k', '')) * 1000
            elif 'm' in view_str:
                return float(view_str.replace('m', '')) * 1000000
            elif 'r' in view_str:
                return float(view_str.replace('r', '')) * 1000000
            return float(view_str)
        except:
            return 0
    
    df['view_count'] = df['views'].apply(parse_views)
    df['depth'] = pd.to_numeric(df['depth'], errors='coerce').fillna(0).astype(int)
    df['category_id_str'] = df['category_id'].astype(str)
    df['category_name'] = df['category_id_str'].map(CATEGORY_NAMES).fillna('Unknown')
    
    return df


def create_network_html(df):
    """Create interactive network visualization"""
    net = Network(height='600px', width='100%', bgcolor='#1a1a2e', font_color='white',
                 notebook=False, cdn_resources='remote')
    net.force_atlas_2based()
    net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=150, spring_strength=0.01)
    
    depth_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
    
    for _, row in df.iterrows():
        depth = int(row.get('depth', 0))
        color = depth_colors[depth % len(depth_colors)]
        
        size = 10 + min(30, (row['view_count'] / 1000000) * 20)
        
        title = f"{row['title']}<br>Channel: {row['channel']}<br>Views: {row['views']}<br>Depth: {depth}<br>Category: {row['category_name']}"
        label = row['title'][:30] + '...' if len(str(row['title'])) > 30 else str(row['title'])
        
        net.add_node(row['url'], label=label, title=title, color=color, size=size)
    
    for _, row in df.iterrows():
        if row.get('recommended_from') and row['recommended_from'] != 'initial':
            parent_row = df[df['title'] == row['recommended_from']]
            if not parent_row.empty:
                parent_url = parent_row.iloc[0]['url']
                net.add_edge(parent_url, row['url'], color='gray')
    
    return net.generate_html("network_map.html")


load_category_names()


def create_dashboard(input_file, output_file='youtube_dashboard.html'):
    """Create a standalone HTML dashboard"""
    
    df = load_data(input_file)
    
    # === VIEWS CHARTS ===
    
    # Average views by depth
    avg_views = df.groupby('depth')['view_count'].mean().reset_index()
    avg_views['depth'] = avg_views['depth'].astype(str)
    fig_avg = px.bar(avg_views, x='depth', y='view_count', 
                    title="Average View Count at Each Depth",
                    labels={'depth': 'Depth Level', 'view_count': 'Average Views'},
                    color_discrete_sequence=['#3498db'])
    fig_avg.update_yaxes(tickformat=",.0f")
    avg_chart = pio.to_html(fig_avg, full_html=False, include_plotlyjs='cdn')
    
    # Total views by depth
    total_views = df.groupby('depth')['view_count'].sum().reset_index()
    total_views['depth'] = total_views['depth'].astype(str)
    fig_total = px.bar(total_views, x='depth', y='view_count',
                      title="Total View Count at Each Depth",
                      labels={'depth': 'Depth Level', 'view_count': 'Total Views'},
                      color_discrete_sequence=['#2ecc71'])
    fig_total.update_yaxes(tickformat=",.0f")
    total_chart = pio.to_html(fig_total, full_html=False, include_plotlyjs='cdn')
    
    # Views distribution box plot
    fig_box = px.box(df, x='depth', y='view_count',
                    title="View Count Distribution by Depth",
                    labels={'depth': 'Depth Level', 'view_count': 'Views'},
                    color_discrete_sequence=['#9b59b6'])
    fig_box.update_yaxes(tickformat=",.0f")
    box_chart = pio.to_html(fig_box, full_html=False, include_plotlyjs='cdn')
    
    # Views trend
    trend_data = df.groupby('depth')['view_count'].agg(['mean', 'median']).reset_index()
    trend_data['depth'] = trend_data['depth'].astype(str)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=trend_data['depth'], y=trend_data['mean'], 
                                   mode='lines+markers', name='Mean Views', line=dict(color='#3498db')))
    fig_trend.add_trace(go.Scatter(x=trend_data['depth'], y=trend_data['median'],
                                   mode='lines+markers', name='Median Views', line=dict(color='#e74c3c')))
    fig_trend.update_layout(title="Views Trend Across Depths", xaxis_title="Depth", yaxis_title="Views")
    fig_trend.update_yaxes(tickformat=",.0f")
    trend_chart = pio.to_html(fig_trend, full_html=False, include_plotlyjs='cdn')
    
    # === CATEGORY CHARTS ===
    
    # Pie chart - overall distribution
    category_counts = df['category_name'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    fig_pie = px.pie(category_counts, values='Count', names='Category',
                    title="Overall Category Distribution")
    pie_chart = pio.to_html(fig_pie, full_html=False, include_plotlyjs='cdn')
    
    # Stacked bar - categories by depth
    category_by_depth = df.groupby(['depth', 'category_name']).size().reset_index(name='count')
    fig_stack = px.bar(category_by_depth, x='depth', y='count', color='category_name',
                      title="Categories at Each Depth",
                      labels={'depth': 'Depth', 'count': 'Video Count'})
    stack_chart = pio.to_html(fig_stack, full_html=False, include_plotlyjs='cdn')
    
    # === NETWORK ===
    network_html = create_network_html(df)
    
    # === DATA TABLE ===
    data_table = df.to_html(index=False, classes='data-table')
    
    # === METRICS ===
    total_videos = len(df)
    total_views = f"{df['view_count'].sum():,.0f}"
    max_depth = int(df['depth'].max())
    unique_channels = df['channel'].nunique()
    
    # === CREATE FULL HTML ===
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Pathfinder Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fafafa;
            min-height: 100vh;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ color: #aaa; font-size: 1.1em; }}
        
        .metric-row {{ 
            display: flex; 
            justify-content: center; 
            gap: 30px; 
            margin: 30px 0;
            flex-wrap: wrap;
        }}
        .metric {{ 
            background: linear-gradient(145deg, #1e3a5f, #162447);
            padding: 25px 40px; 
            border-radius: 15px; 
            text-align: center; 
            min-width: 180px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #4fc3f7; }}
        .metric-label {{ font-size: 0.9em; color: #aaa; margin-top: 5px; }}
        
        .section {{ margin: 50px 0; }}
        .section h2 {{ 
            border-bottom: 2px solid #4fc3f7; 
            padding-bottom: 10px; 
            margin-bottom: 25px;
            color: #4fc3f7;
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }}
        .chart-container {{ 
            background: rgba(255,255,255,0.03);
            padding: 20px; 
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .chart-full {{ 
            background: rgba(255,255,255,0.03);
            padding: 20px; 
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .network-container {{
            background: rgba(255,255,255,0.03);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-top: 20px;
        }}
        
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
            background: rgba(255,255,255,0.02);
        }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ background: #162447; color: #4fc3f7; }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        
        .data-table-container {{
            max-height: 500px;
            overflow: auto;
            border-radius: 10px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        
        @media (max-width: 768px) {{
            .chart-grid {{ grid-template-columns: 1fr; }}
            .metric-row {{ flex-direction: column; align-items: center; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 YouTube Pathfinder Dashboard</h1>
        <p>Interactive Analysis of YouTube Video Recommendations</p>
    </div>
    
    <div class="metric-row">
        <div class="metric">
            <div class="metric-value">{total_videos}</div>
            <div class="metric-label">Total Videos</div>
        </div>
        <div class="metric">
            <div class="metric-value">{total_views}</div>
            <div class="metric-label">Total Views</div>
        </div>
        <div class="metric">
            <div class="metric-value">{max_depth}</div>
            <div class="metric-label">Max Depth</div>
        </div>
        <div class="metric">
            <div class="metric-value">{unique_channels}</div>
            <div class="metric-label">Unique Channels</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 Views Analysis</h2>
        <div class="chart-grid">
            <div class="chart-container">
                {avg_chart}
            </div>
            <div class="chart-container">
                {total_chart}
            </div>
        </div>
        <div class="chart-full">
            {box_chart}
        </div>
        <div class="chart-full">
            {trend_chart}
        </div>
    </div>
    
    <div class="section">
        <h2>📂 Category Analysis</h2>
        <div class="chart-grid">
            <div class="chart-container">
                {pie_chart}
            </div>
            <div class="chart-container">
                {stack_chart}
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🌐 Network Map</h2>
        <p style="color: #aaa; margin-bottom: 20px;">
            Interactive network showing video recommendations. 
            Nodes are colored by depth (red=0, blue=1, green=2, etc.) and sized by view count.
        </p>
        <div class="network-container">
            {network_html}
        </div>
    </div>
    
    <div class="section">
        <h2>📋 Data Overview</h2>
        <div class="data-table-container">
            {data_table}
        </div>
    </div>
    
    <div class="footer">
        <p>Generated with YouTube Pathfinder</p>
    </div>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Dashboard saved to: {output_file}")
    return output_file


if __name__ == '__main__':
    import sys
    
    input_file = 'youtube_results_enriched.csv'
    output_file = 'youtube_dashboard.html'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    create_dashboard(input_file, output_file)