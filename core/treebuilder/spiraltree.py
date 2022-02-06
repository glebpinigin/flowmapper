class SpiralTreeNode():
    
    def __init__(self, curve=None, parent=None, root_xy=None):
        self.curve = curve
        self.parent = parent
        self.xy = curve.leaf if root_xy is None else root_xy
        self.children = None


class SpiralTree():
    
    def __init__(self, root_xy):
        self.root = SpiralTreeNode(root_xy)
    
    def insert (self, curve, parent):
        new_node = SpiralTreeNode()
    
    def __add__(self, new_node):
        self.insert(self, new_node)
