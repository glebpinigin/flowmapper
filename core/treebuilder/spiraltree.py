import networkx as nx

class SpiralTree(nx.DiGraph):
    
    def __init__(self):
        super().__init__()
        self.root = "root"
        self.add_node(self.root)
    
    def insertLeaf(self, R):
        self.add_node(R)
        self.add_edge(self.root, R, type="root-connection")
    
    def insertSteinerNode(self, steiner_R=None, leaf1_R=None, leaf2_R=None):
        self.add_node(steiner_R)
        self.add_edge(self.root, steiner_R, type="root-connection")
        for leaf_R in (leaf1_R, leaf2_R):
          self.remove_edge(self.root, leaf_R)
          self.add_edge(steiner_R, leaf_R, type="st-connection")
    
    def repairUnderlying(self, close_R, far_R):
        self.remove_edge(self.root, far_R)
        self.add_edge(close_R, far_R, type="false-connection")