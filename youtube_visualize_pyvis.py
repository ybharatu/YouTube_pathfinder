from youtube_graph import youtube_graph
import sys


def create_pyvis_graph(graph):
    try:
        from pyvis.network import Network
    except ImportError:
        print("PyVis not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pyvis"])
        from pyvis.network import Network
    
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", 
                 notebook=True, cdn_resources='remote')
    net.force_atlas_2based()
    
    for node in graph.nodes_by_title.values():
        color = DEPTH_COLORS[node.depth % len(DEPTH_COLORS)]
        label = node.title[:40] + "..." if len(node.title) > 40 else node.title
        
        title_text = f"{node.title}<br>Channel: {node.channel}<br>Views: {node.views}<br>Depth: {node.depth}<br>From: {node.recfrom}"
        
        net.add_node(node.link, label=label, title=title_text, color=color, size=20 - node.depth * 2)
    
    for node in graph.nodes_by_title.values():
        for parent in node.parents:
            net.add_edge(parent.link, node.link, color="gray")
    
    return net


DEPTH_COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c', '#e67e22', '#34495e']


def visualize_pyvis(graph, output_file='youtube_graph.html'):
    net = create_pyvis_graph(graph)
    net.save_graph(output_file)
    print(f'Saved interactive visualization to: {output_file}')
    return output_file


def print_graph_summary(graph):
    print(f'Graph: {len(graph.nodes_by_title)} total nodes, depth {graph.depth}')
    print(f'Heads (depth 0, initial search): {len(graph.heads)} videos')
    
    for i, head in enumerate(graph.heads):
        print(f'  Head {i+1}: {head.title[:50]}... (channel: {head.channel}, views: {head.views})')
        for child in head.children:
            print(f'    -> {child.title[:40]}... (depth={child.depth}, from: {child.recfrom[:30]}...)')


def main():
    filename = 'youtube_results.csv'
    output_file = 'youtube_graph.html'
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f'Loading graph from: {filename}')
    graph = youtube_graph()
    graph.load_from_csv(filename)
    
    print(f'Graph loaded: {len(graph.nodes_by_title)} nodes, depth {graph.depth}')
    print()
    print_graph_summary(graph)
    print()
    print(f'Creating interactive visualization: {output_file}')
    
    visualize_pyvis(graph, output_file)


if __name__ == '__main__':
    main()