import networkx as nx

class SpiralTree(nx.DiGraph):
    
    def __init__(self):
        super().__init__()
        self.add_node("root")
    
    def insertLeaf(self, R):
        self.add_node(R)
        self.add_edge("root", R)
    
    def insertSteinerNode(self, *args, steiner_R=None, leaf1_R=None, leaf2_R=None):
        for i, param in enumerate(steiner_R, leaf1_R, leaf2_R):
            param = args[i] if param is None else param

        self.add_node(steiner_R)
        self.add_edge("root", steiner_R)
        for leaf_R in (leaf1_R, leaf2_R):
          self.remove_edge("root", leaf_R)
          self.add_edge(steiner_R, leaf_R)