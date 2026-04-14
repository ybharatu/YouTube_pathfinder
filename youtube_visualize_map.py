import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from youtube_graph import youtube_graph
import sys


DEPTH_COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c', '#e67e22', '#34495e']

def get_depth_color(depth):
    """Get color for a depth level, cycling through colors if needed"""
    return DEPTH_COLORS[depth % len(DEPTH_COLORS)]

MAX_LABEL_LENGTH = 100


def create_graph_from_csv(filename):
    graph = youtube_graph()
    graph.load_from_csv(filename)
    return graph


def build_networkx_graph(youtube_graph):
    G = nx.DiGraph()
    
    for node in youtube_graph.nodes_by_title.values():
        label = node.title[:MAX_LABEL_LENGTH] + "..." if len(node.title) > MAX_LABEL_LENGTH else node.title
        G.add_node(node.link, label=label, depth=node.depth, channel=node.channel, title=node.title)
    
    for node in youtube_graph.nodes_by_title.values():
        for parent in node.parents:
            G.add_edge(parent.link, node.link)
    
    return G


def visualize(graph, output_file='youtube_graph.pdf', figsize=(30, 24)):
    G = build_networkx_graph(graph)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    depth_groups = {}
    for node in graph.nodes_by_title.values():
        if node.depth not in depth_groups:
            depth_groups[node.depth] = []
        depth_groups[node.depth].append(node.link)
    
    pos = {}
    max_depth = graph.depth
    
    for depth, links in depth_groups.items():
        y = max_depth - depth
        x_spacing = 1.0 / (len(links) + 1)
        for i, link in enumerate(links):
            # Add vertical stagger that increases with depth
            y_offset = (i % 3) * 0.05 * (1 + depth * 0.3)
            pos[link] = ((i + 1) * x_spacing, y - y_offset)
    
    node_colors = [DEPTH_COLORS[G.nodes[n]['depth'] % len(DEPTH_COLORS)] for n in G.nodes()]
    
    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True,
                        arrowstyle='->', edge_color='gray',
                        connectionstyle='arc3,rad=0.1',
                        alpha=0.6, arrowsize=10)
    
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                        node_size=150, alpha=0.9)
    
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=3)
    
    legend_elements = [
        mpatches.Patch(color=get_depth_color(i), label=f'Depth {i}')
        for i in range(max_depth + 1)
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    depth_labels = {depth: f'Depth {depth}' for depth in depth_groups.keys()}
    for i, (x, y) in pos.items():
        pass
    
    plt.title(f'YouTube Video Recommendations Graph\nMax Depth: {graph.depth} | Total Nodes: {len(G.nodes())}',
              fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    plt.savefig(output_file, format='pdf', bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f'Saved visualization to: {output_file}')
    return output_file


def print_graph_summary(graph):
    print(f'Graph: {len(graph.nodes_by_title)} total nodes, depth {graph.depth}')
    print(f'Heads (depth 0, initial search): {len(graph.heads)} videos')
    
    for i, head in enumerate(graph.heads):
        print(f'  Head {i+1}: {head.title[:50]}... (channel: {head.channel}, views: {head.views})')
        for child in head.children:
            print(f'    -> {child.title[:40]}... (depth={child.depth}, from: {child.recfrom[:30]}...)')


def main():
    import sys
    from youtube_graph import youtube_graph
    from youtube_node import youtube_node
    
    filename = 'youtube_results.csv'
    output_file = 'youtube_graph.pdf'
    
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
    print(f'Creating visualization: {output_file}')
    
    visualize(graph, output_file)


if __name__ == '__main__':
    main()