from matplotlib import pyplot as plt
import core.treebuilder.treebuilder as tbldr
from core.treebuilder.local_utils import tdraw

leaves = [ (10, 0), (10, 10), (0, 9)]
T = tbldr.buildTree(leaves=leaves)
tdraw(list(T.nodes)[1:])
plt.show()