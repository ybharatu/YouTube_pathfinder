from youtube_node import youtube_node

class youtube_graph:
    def __init__(self):
        self.heads = []
        self.depth = 0
        self.nodes_by_title = {}
    
    def load_from_csv(self, filename):
        import csv
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Create nodes for all rows
        for row in rows:
            node = youtube_node(
                title=row['title'],
                channel=row['channel'],
                views=row['views'],
                recfrom=row['recommended_from'],
                depth=int(row['depth']),
                link=row['url']
            )
            self.nodes_by_title[node.title] = node
            
            # Track max depth
            if node.depth > self.depth:
                self.depth = node.depth
        
        # Find head nodes (depth=0, recommended_from='initial')
        for node in self.nodes_by_title.values():
            if node.depth == 0 and node.recfrom == 'initial':
                self.heads.append(node)
        
        # Build bidirectional links
        for node in self.nodes_by_title.values():
            if node.recfrom != 'initial' and node.recfrom in self.nodes_by_title:
                parent = self.nodes_by_title[node.recfrom]
                node.parent = parent
                parent.children.append(node)
    
    def __repr__(self):
        return f'youtube_graph(heads={len(self.heads)}, total_nodes={len(self.nodes_by_title)}, depth={self.depth})'