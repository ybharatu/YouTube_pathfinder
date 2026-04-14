import sys
from youtube_graph import youtube_graph


def create_graph_from_csv(filename='youtube_results.csv'):
    graph = youtube_graph()
    graph.load_from_csv(filename)
    return graph


def print_graph(graph, indent=0):
    prefix = '  ' * indent
    
    print(f'{prefix}Graph: {len(graph.nodes_by_title)} total nodes, depth {graph.depth}')
    print(f'{prefix}Heads (depth 0, initial search): {len(graph.heads)} videos')
    
    for i, head in enumerate(graph.heads):
        print(f'{prefix}  Head {i+1}: {head.title[:50]}... (channel: {head.channel}, views: {head.views})')
        print_node_tree(head, indent + 2)


def print_node_tree(node, indent=0, visited=None, depth_limit=3):
    if visited is None:
        visited = set()
    
    prefix = '  ' * indent
    
    # Prevent infinite recursion
    if node.title in visited or indent > depth_limit * 2:
        return
    
    visited.add(node.title)
    
    if node.children:
        for child in node.children:
            print(f'{prefix}→ {child.title[:40]}... (depth={child.depth}, from: {child.recfrom[:30]}...)')
            print_node_tree(child, indent + 1, visited, depth_limit)


def main():
    filename = 'youtube_results.csv'
    
    # Check for command line argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    print(f'Loading graph from: {filename}')
    print('-' * 50)
    
    graph = create_graph_from_csv(filename)
    
    print()
    print_graph(graph)
    print()
    print('Graph structure:')
    print(f'  - Total nodes: {len(graph.nodes_by_title)}')
    print(f'  - Head nodes (initial search): {len(graph.heads)}')
    print(f'  - Max depth: {graph.depth}')
    
    # Print some statistics
    depth_counts = {}
    for node in graph.nodes_by_title.values():
        depth_counts[node.depth] = depth_counts.get(node.depth, 0) + 1
    
    print(f'  - Nodes by depth: {depth_counts}')


if __name__ == '__main__':
    main()