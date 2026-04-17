import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyvis.network import Network
import os
import tempfile


# HTML template for standalone export
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Pathfinder Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PyWebUI/0.3.8/pywebui.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/PyWebUI/0.3.8/pywebui.min.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0e1117; color: #fafafa; }
        .header { text-align: center; margin-bottom: 30px; }
        .metric-row { display: flex; justify-content: space-around; margin: 20px 0; }
        .metric { background: #262730; padding: 20px; border-radius: 10px; text-align: center; min-width: 150px; }
        .metric-value { font-size: 24px; font-weight: bold; }
        .metric-label { font-size: 14px; color: #aaa; }
        .section { margin: 40px 0; }
        .chart-container { background: #262730; padding: 20px; border-radius: 10px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
        th { background: #1a1a2e; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 YouTube Pathfinder Dashboard</h1>
        <p>YouTube Video Recommendations Analysis</p>
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
        {views_charts}
    </div>
    
    <div class="section">
        <h2>📂 Category Analysis</h2>
        {category_charts}
    </div>
    
    <div class="section">
        <h2>🌐 Network Map</h2>
        <p>Interactive network map requires JavaScript. Open the HTML file in a browser.</p>
        {network_html}
    </div>
    
    <div class="section">
        <h2>📋 Data</h2>
        {data_table}
    </div>
</body>
</html>"""


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

CATEGORY_COLORS = {
    'Music': '#1DB954',
    'Entertainment': '#FF6B6B',
    'Science & Technology': '#4ECDC4',
    'Education': '#45B7D1',
    'Gaming': '#9B59B6',
    'People & Blogs': '#F39C12',
    'Comedy': '#E74C3C',
    'Sports': '#2ECC71',
    'News & Politics': '#34495E',
    'Howto & Style': '#E91E63',
    'Film & Animation': '#9C27B0',
    'Autos & Vehicles': '#00BCD4',
    'Pets & Animals': '#8BC34A',
    'Travel & Events': '#FF9800',
    'Short Movies': '#795548',
    'Videoblogging': '#607D8B',
    'Nonprofits & Activism': '#CDDC39',
    'Movies': '#FF5722',
    'Anime/Animation': '#673AB7',
    'Action/Adventure': '#3F51B5',
    'Classics': '#FFC107',
    'Documentary': '#009688',
    'Drama': '#FF0097',
    'Family': '#00E676',
    'Foreign': '#AA00FF',
    'Horror': '#212121',
    'Sci-Fi/Fantasy': '#00B8D4',
    'Thriller': '#D50000',
    'Shorts': '#76FF03',
    'Shows': '#FFEA00',
    'Trailers': '#FF9100',
    'Unknown': '#95A5A6',
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
        pass  # Use default categories

load_category_names()


def load_data(csv_file):
    """Load and prepare the CSV data"""
    df = pd.read_csv(csv_file)
    
    # Parse view count
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
    
    # Map category ID to name (convert to string for lookup)
    def clean_category_id(cat_id):
        if pd.isna(cat_id) or cat_id == '':
            return 'Unknown'
        try:
            return str(int(float(cat_id)))
        except:
            return 'Unknown'
    
    df['category_id_str'] = df['category_id'].apply(clean_category_id)
    df['category_name'] = df['category_id_str'].map(CATEGORY_NAMES).fillna('Unknown')
    df['category_color'] = df['category_name'].map(CATEGORY_COLORS).fillna('#95A5A6')
    
    return df


def create_network_html(df):
    """Create interactive network visualization"""
    net = Network(height='600px', width='100%', bgcolor='#1a1a2e', font_color='white',
                 notebook=False, cdn_resources='remote')
    net.force_atlas_2based()
    
    # Color palette for depths
    depth_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
    
    for _, row in df.iterrows():
        depth = int(row.get('depth', 0))
        color = depth_colors[depth % len(depth_colors)]
        
        # Size based on view count (log scale for readability)
        size = 10 + min(30, (row['view_count'] / 1000000) * 20)
        
        title = f"{row['title']}<br>Channel: {row['channel']}<br>Views: {row['views']}<br>Depth: {depth}<br>Category: {row['category_name']}"
        label = row['title'][:30] + '...' if len(str(row['title'])) > 30 else str(row['title'])
        
        net.add_node(row['url'], label=label, title=title, color=color, size=size)
    
    # Add edges
    for _, row in df.iterrows():
        if row.get('recommended_from') and row['recommended_from'] != 'initial':
            parent_row = df[df['title'] == row['recommended_from']]
            if not parent_row.empty:
                parent_url = parent_row.iloc[0]['url']
                net.add_edge(parent_url, row['url'], color='gray')
    
    # Save to temp file and read back
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html_content = f2.read()
        os.unlink(f.name)
    
    return html_content


def main():
    st.set_page_config(page_title="YouTube Pathfinder Dashboard", layout="wide", page_icon="📊")
    
    # Add CSS for tables
    st.markdown("""
    <style>
    .data-table { width: 100%; border-collapse: collapse; }
    .data-table th { background: #1e3a5f; color: white; padding: 10px; text-align: left; }
    .data-table td { padding: 8px; border-bottom: 1px solid #444; }
    .data-table tr:hover { background: #2a2a2a; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 YouTube Pathfinder Dashboard")
    st.markdown("Analyze YouTube video recommendations across depth levels")
    
    # File input
    csv_file = st.sidebar.file_uploader("Upload enriched CSV", type=['csv'])
    
    if not csv_file:
        st.info("Please upload an enriched CSV file. You can create one using:")
        st.code("python3 youtube_enrich_data.py")
        st.stop()
    
    df = load_data(csv_file)
    
    st.sidebar.header("Global Filters")
    
    # Depth filter
    depth_options = sorted(df['depth'].unique())
    selected_depths = st.sidebar.multiselect(
        "Depth Levels",
        options=depth_options,
        default=depth_options
    )
    
    # Apply filters
    filtered_df = df[df['depth'].isin(selected_depths)]
    
    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs(["🌐 Network Map", "📈 Views Analysis", "📂 Category Analysis", "📋 Data"])
    
    # === TAB 1: NETWORK MAP ===
    with tab1:
        st.header("Video Recommendation Network")
        
        network_df = filtered_df[filtered_df['depth'].isin(selected_depths)]
        
        if len(network_df) > 150:
            st.warning(f"Showing first 100 nodes (total: {len(network_df)})")
            network_df = network_df.head(100)
        
        try:
            network_html = create_network_html(network_df)
            st.components.v1.html(network_html, height=650, scrolling=True)
        except Exception as e:
            st.error(f"Error creating network: {e}")
        
        st.caption("Nodes colored by depth. Size = view count. Hover for details.")
    
    # === TAB 2: VIEWS ANALYSIS ===
    with tab2:
        st.header("Views Analysis by Depth")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Average Views by Depth")
            avg_views = filtered_df.groupby('depth')['view_count'].mean().reset_index()
            avg_views['depth'] = avg_views['depth'].astype(str)
            fig = px.bar(avg_views, x='depth', y='view_count', 
                        title="Average View Count at Each Depth",
                        labels={'depth': 'Depth Level', 'view_count': 'Average Views'},
                        color_discrete_sequence=['#3498db'])
            fig.update_yaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Total Views by Depth")
            total_views = filtered_df.groupby('depth')['view_count'].sum().reset_index()
            total_views['depth'] = total_views['depth'].astype(str)
            fig2 = px.bar(total_views, x='depth', y='view_count',
                         title="Total View Count at Each Depth",
                         labels={'depth': 'Depth Level', 'view_count': 'Total Views'},
                         color_discrete_sequence=['#2ecc71'])
            fig2.update_yaxes(tickformat=",.0f")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Views Distribution")
        fig3 = px.box(filtered_df, x='depth', y='view_count',
                     title="View Count Distribution by Depth",
                     labels={'depth': 'Depth Level', 'view_count': 'Views'},
                     color_discrete_sequence=['#9b59b6'])
        fig3.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig3, use_container_width=True)
        
        st.subheader("Views Trend")
        trend_data = filtered_df.groupby('depth')['view_count'].agg(['mean', 'median']).reset_index()
        trend_data['depth'] = trend_data['depth'].astype(str)
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=trend_data['depth'], y=trend_data['mean'], 
                                 mode='lines+markers', name='Mean Views', line=dict(color='#3498db')))
        fig4.add_trace(go.Scatter(x=trend_data['depth'], y=trend_data['median'],
                                 mode='lines+markers', name='Median Views', line=dict(color='#e74c3c')))
        fig4.update_layout(title="Views Trend Across Depths", xaxis_title="Depth", yaxis_title="Views")
        fig4.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig4, use_container_width=True)
        
        st.subheader("View Count Growth/Decay Analysis")
        avg_by_depth = filtered_df.groupby('depth')['view_count'].mean().reset_index()
        if len(avg_by_depth) > 1:
            avg_by_depth['pct_change'] = avg_by_depth['view_count'].pct_change() * 100
            avg_by_depth['depth_str'] = avg_by_depth['depth'].astype(str)
            
            growth_data = avg_by_depth[avg_by_depth['pct_change'].notna()].copy()
            growth_data['change_label'] = growth_data['pct_change'].apply(
                lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%"
            )
            
            fig_growth = go.Figure()
            fig_growth.add_trace(go.Bar(
                x=growth_data['depth_str'], 
                y=growth_data['pct_change'],
                text=growth_data['change_label'],
                textposition='auto',
                marker=dict(color=growth_data['pct_change'].apply(
                    lambda x: '#2ecc71' if x >= 0 else '#e74c3c'
                ))
            ))
            fig_growth.update_layout(
                title="Average Views Change Between Depths (%)",
                xaxis_title="Depth",
                yaxis_title="Percent Change (%)"
            )
            st.plotly_chart(fig_growth, use_container_width=True)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                start_views = avg_by_depth.iloc[0]['view_count'] if len(avg_by_depth) > 0 else 0
                end_views = avg_by_depth.iloc[-1]['view_count'] if len(avg_by_depth) > 0 else 0
                overall_change = ((end_views - start_views) / start_views * 100) if start_views > 0 else 0
                st.metric("Overall Change (Depth 0 → Max)", f"{overall_change:+.1f}%", 
                         f"{end_views - start_views:,.0f} views")
            with col_g2:
                max_drop = growth_data['pct_change'].min() if len(growth_data) > 0 else 0
                st.metric("Largest Drop", f"{max_drop:.1f}%")
        
        st.subheader("Views Distribution by Depth (Histogram)")
        fig_hist = px.histogram(
            filtered_df, 
            x='view_count', 
            color='depth',
            title="Distribution of Views at Each Depth",
            labels={'view_count': 'Views', 'depth': 'Depth'},
            barmode='overlay',
            opacity=0.7
        )
        fig_hist.update_xaxes(tickformat=",.0f")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.subheader("Scatter: Views vs Depth by Channel")
        top_channels = filtered_df['channel'].value_counts().nlargest(12).index.tolist()
        channel_filter = st.selectbox("Select channels to display:", 
                                      ["All Channels"] + top_channels, 
                                      index=0)
        
        if channel_filter != "All Channels":
            scatter_df = filtered_df[filtered_df['channel'] == channel_filter]
        else:
            scatter_df = filtered_df[filtered_df['channel'].isin(top_channels)]
        
        fig_scatter = px.scatter(
            scatter_df,
            x='depth',
            y='view_count',
            color='channel',
            size='view_count',
            size_max=30,
            title="Views vs Depth (colored by channel, size = view count)",
            labels={'depth': 'Depth', 'view_count': 'Views', 'channel': 'Channel'},
            hover_data=['title']
        )
        fig_scatter.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.subheader("Top Performing Videos by Depth")
        top_n = st.slider("Number of top videos per depth", 3, 10, 5)
        
        def format_views(view_val):
            if pd.isna(view_val) or view_val == '':
                return 'N/A'
            try:
                view_str = str(view_val).lower().replace(',', '').replace(' views', '').replace('view', '').strip()
                return f"{int(float(view_str)):,.0f}"
            except:
                return 'N/A'
        
        for depth in sorted(filtered_df['depth'].unique()):
            depth_data = filtered_df[filtered_df['depth'] == depth].nlargest(top_n, 'view_count')
            if not depth_data.empty:
                st.markdown(f"**Depth {int(depth)}** - Top {top_n} by views")
                top_table = depth_data[['title', 'channel', 'views', 'category_name']].copy()
                top_table['views'] = top_table['views'].apply(format_views)
                st.write(top_table.to_html(index=False, classes='table'), unsafe_allow_html=True)
    
    # === TAB 3: CATEGORY ANALYSIS ===
    with tab3:
        st.header("Category Analysis by Depth")
        
        # Get unique categories and their colors
        unique_categories = filtered_df['category_name'].unique()
        category_color_map = {cat: CATEGORY_COLORS.get(cat, '#95A5A6') for cat in unique_categories}
        
        # Show category color legend
        st.markdown("**Category Colors:**")
        legend_cols = st.columns(min(4, len(unique_categories)))
        for i, cat in enumerate(sorted(unique_categories)):
            with legend_cols[i % 4]:
                st.markdown(
                    f'<span style="background-color:{category_color_map[cat]}; padding: 2px 8px; '
                    f'border-radius: 4px; color: white; font-size: 12px;">{cat}</span>',
                    unsafe_allow_html=True
                )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Category Distribution (Pie)")
            category_counts = filtered_df['category_name'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            fig = px.pie(category_counts, values='Count', names='Category',
                        title="Overall Category Distribution",
                        color='Category',
                        color_discrete_map=category_color_map)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Categories by Depth (Stacked)")
            category_by_depth = filtered_df.groupby(['depth', 'category_name']).size().reset_index(name='count')
            fig2 = px.bar(category_by_depth, x='depth', y='count', color='category_name',
                        title="Categories at Each Depth",
                        labels={'depth': 'Depth', 'count': 'Video Count'},
                        color_discrete_map=category_color_map)
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Category by Depth (Detailed)")
        for depth in sorted(filtered_df['depth'].unique()):
            depth_data = filtered_df[filtered_df['depth'] == depth]
            cat_counts = depth_data['category_name'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            
            st.markdown(f"**Depth {int(depth)}**: {len(depth_data)} videos")
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.write(cat_counts.head(5).to_html(index=False, classes='table'), unsafe_allow_html=True)
            with col_b:
                fig = px.pie(cat_counts.head(5), values='Count', names='Category',
                           title=f"Category breakdown at Depth {int(depth)}",
                           color='Category',
                           color_discrete_map=category_color_map)
                st.plotly_chart(fig, use_container_width=True)
    
    # === TAB 4: DATA ===
    with tab4:
        st.header("Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Videos", len(filtered_df))
        with col2:
            st.metric("Total Views", f"{filtered_df['view_count'].sum():,.0f}")
        with col3:
            st.metric("Max Depth", int(filtered_df['depth'].max()))
        with col4:
            st.metric("Unique Channels", filtered_df['channel'].nunique())
        
        st.subheader("Filtered Data")
        # Convert dataframe to HTML to avoid pyarrow issue
        html_table = filtered_df.to_html(index=False, classes='data-table', escape=False)
        st.markdown(html_table, unsafe_allow_html=True)
        
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Data", csv, "filtered_data.csv", "text/csv")


if __name__ == '__main__':
    main()