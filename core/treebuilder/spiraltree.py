class SpiralTreeNode():
    
    def __init__(self, R=None, parent=None, root_xy=None):
        self.R = R
        self.parent = parent
        self.xy = R.leaf if root_xy is None else root_xy
        self.children = []
    
    def get_polar(self):
        return {"dst": self.R.dst, # angle and dst from NodeRegion
                "ang": self.R.ang}
    


class SpiralTree():
    
    def __init__(self, root_xy):
        self.root = SpiralTreeNode(root_xy = root_xy)
    
    def insertLeaf(self, R) -> SpiralTreeNode:
        leaf_node = SpiralTreeNode(R)
        self.root.children.append(leaf_node)
        return leaf_node
    
    def insertSteinerNode(self, steiner_node, leaf_node1: SpiralTreeNode, leaf_node2: SpiralTreeNode):
        self.root.children.append(steiner_node)
        steiner_node.children = [leaf_node1, leaf_node2]
        self.root.children.remove(leaf_node1)
        self.root.children.remove(leaf_node2)