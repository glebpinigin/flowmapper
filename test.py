from matplotlib import pyplot as plt
import core.treebuilder.treebuilder as tbldr
from core.treebuilder.local_utils import tdraw
from expls import *

leaves = getLeaf(1)
#leaves = list(filter(lambda x: x[0] > 0, leaves))
#leaves.append((-25.11407890334805, -153.18910434475615))

T = tbldr.buildTree(leaves=leaves)
tdraw(list(T.nodes)[1:])
plt.show()