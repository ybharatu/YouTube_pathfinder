class youtube_node:
    def __init__(self, title, channel, views, recfrom, depth, link):
        self.title = title
        self.channel = channel
        self.views = views
        self.recfrom = recfrom  # title of the video that recommended this one
        self.depth = depth
        self.link = link
        self.children = []  # videos recommended from this node
        self.parent = None   # bidirectional - what recommended this node
    
    def __repr__(self):
        return f'youtube_node(title={self.title[:30]}..., depth={self.depth}, channel={self.channel})'