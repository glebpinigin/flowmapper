import networkx as nx
import numpy as np
from shapely import wkt
from shapely.geometry import LineString


class SpiralTree(nx.DiGraph):
    

    def __init__(self, root, bias, vol_attrs=None):
        super().__init__()
        self.Rs = {}
        self.root = root
        self.bias = np.array(bias)
        self.add_node(self.applyNdBias(root, self.bias))
        self.vol_attrs = ["count"] if vol_attrs is None else vol_attrs
    

    def insertLeaf(self, R):
        self.add_node(self.applyNdBias(R, self.bias), R=R)
        attr = {name: value for value, name in zip(R.volumes, self.vol_attrs)}
        self.add_edge(self.Rs["root"], self.Rs[R], type="root-connection", **attr)
    

    def insertSteinerNode(self, steiner_R=None, leaf1_R=None, leaf2_R=None):
        self.add_node(self.applyNdBias(steiner_R, self.bias), R=steiner_R)
        self.add_edge(self.Rs["root"], self.Rs[steiner_R], type="root-connection")
        for leaf_R in (leaf1_R, leaf2_R):
            tp = leaf_R.tp
            self.remove_edge(self.Rs["root"], self.Rs[leaf_R])
            attr = {name: value for value, name in zip(leaf_R.volumes, self.vol_attrs)}
            self.add_edge(self.Rs[steiner_R], self.Rs[leaf_R], type=f"st-connection-{tp}", **attr)
    

    def insertFalseNode(self, close_R, far_R1, far_R2, collapse_args):
        self.remove_edge(self.Rs["root"], self.Rs[far_R1])
        self.remove_edge(self.Rs["root"], self.Rs[far_R2])
        self.insertLeaf(close_R)
        self.add_node(self.applyNdBias(far_R1, self.bias), R=far_R1)
        attr = {name: value for value, name in zip(far_R1.volumes, self.vol_attrs)}
        far_R2.collapseRegion(*collapse_args)
        self.add_edge(self.Rs[close_R], self.Rs[far_R1], type=f"st-connection-{far_R1.tp}", **attr)
        attr = {name: value for value, name in zip(far_R2.volumes, self.vol_attrs)}
        self.add_edge(self.Rs[close_R], self.Rs[far_R2], type=f"false-connection-{far_R2.tp}", **attr)
        # nx.set_edge_attributes(self, {(self.root, close_R): list(close_R.volumes)}, name="volumes")


    def applyNdBias(self, val, bias):
        if type(val) is tuple:
            leaf = tuple(np.array(val) + bias)
            self.Rs["root"] = leaf
        else:
            leaf = tuple(np.array(val.leaf) + bias)
            self.Rs[val] = leaf
        return leaf


def connectionsToWkt(T: SpiralTree):
    biasX, biasY = T.bias
    bias = np.array((biasX, biasY))
    for node1, node2, data in T.edges.data():
        if data["type"] == "root-connection":
            node1_crds = np.array(node1) + bias
            leaf = np.array(node2.leaf) + bias
            crds = (node1_crds, leaf)
            line = LineString(crds)
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")
        else:
            R = node2
            tp = R.tp
            crds = R.crds[f"{tp}_xy"]
            crds = np.column_stack(crds)
            crds = crds + bias
            line = LineString(crds)
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")


def spiraltreeToPandas(T):
    pdtb = nx.to_pandas_edgelist(T)
    pdtb["Wkt"] = pdtb["Wkt"].apply(wkt.loads)
    return pdtb