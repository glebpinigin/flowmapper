import networkx as nx
from shapely.geometry import LineString
import numpy as np

class SpiralTree(nx.DiGraph):
    
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.add_node(self.root)
    
    def insertLeaf(self, R):
        self.add_node(R)
        self.add_edge(self.root, R, type="root-connection", volume=R.volume)
    
    def insertSteinerNode(self, steiner_R=None, leaf1_R=None, leaf2_R=None):
        self.add_node(steiner_R)
        self.add_edge(self.root, steiner_R, type="root-connection")
        for leaf_R in (leaf1_R, leaf2_R):
          self.remove_edge(self.root, leaf_R)
          self.add_edge(steiner_R, leaf_R, type="st-connection", volume=leaf_R.volume)
    
    def insertFalseNode(self, close_R, far_R1, far_R2):
        self.remove_edge(self.root, far_R1)
        self.remove_edge(self.root, far_R2)
        self.add_node(close_R)
        self.add_node(far_R1)
        self.add_edge(close_R, far_R1, type="false-connection", volume=far_R1.volume)
        self.add_edge(close_R, far_R2, type="false-connection", volume=far_R2.volume)
        nx.set_edge_attributes(self, {(self.root, close_R): close_R.volume}, name="volume")

def connectionsToWkt(T: SpiralTree):
    for node1, node2, data in T.edges.data():
        if data["type"] == "root-connection":
            crds = (node1, node2.leaf)
            line = LineString(crds)
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")
        else:
            R = node2
            tp = R.tp
            crds = R.crds[f"{tp}_xy"]
            line = LineString(np.column_stack(crds))
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")

    # for node1, node2, data in T.edges.data():
    #     if data["type"] == "root-connection":
    #         xx = (node1[0], node2.leaf[0])
    #         yy = (node1[1], node2.leaf[1])
    #     else:
    #         R = node2
    #         tp = R.tp
    #         xx, yy = R.crds[f"{tp}_xy"]
    #     nx.set_edge_attributes(T, {(node1, node2): (xx, yy)}, name="loc")
    
    # for node, data in T.nodes.data():
    #     if node == T.root:
    #         x = T.root[0]
    #         y = T.root[1]
    #     else:
    #         x = node.leaf[0]
    #         y = node.leaf[1]
    #     nx.set_node_attributes(T, {node: (x, y)}, 'loc')