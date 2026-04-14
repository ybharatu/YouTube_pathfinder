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
        
        # Create nodes for all rows - use URL as unique key to handle duplicate titles
        for row in rows:
            node = youtube_node(
                title=row['title'],
                channel=row['channel'],
                views=row['views'],
                recfrom=row['recommended_from'],
                depth=int(row['depth']),
                link=row['url']
            )
            # Use URL as key to handle duplicate titles with different URLs
            self.nodes_by_title[node.link] = node
            
            # Track max depth
            if node.depth > self.depth:
                self.depth = node.depth
        
        # Find head nodes (depth=0, recommended_from='initial')
        for node in self.nodes_by_title.values():
            if node.depth == 0 and node.recfrom == 'initial':
                self.heads.append(node)
        
        # Build bidirectional links - use URL as key
        for node in self.nodes_by_title.values():
            if node.recfrom != 'initial':
                # Find parent by matching title
                for potential_parent in self.nodes_by_title.values():
                    if potential_parent.title == node.recfrom:
                        if potential_parent not in node.parents:
                            node.parents.append(potential_parent)
                        if node not in potential_parent.children:
                            potential_parent.children.append(node)
    
    def __repr__(self):
        return f'youtube_graph(heads={len(self.heads)}, total_nodes={len(self.nodes_by_title)}, depth={self.depth})'