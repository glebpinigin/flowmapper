from matplotlib import pyplot as plt
import core.treebuilder.treebuilder as tbldr
from core.treebuilder.local_utils import tdraw

leaves = [ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20), (20, 0), (5, 10), (22, 4), (-30, 5), (-35, -6)]
# leaves = [ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20)]
# leaves = [ (10, 0), (10, 10), (0, 9), (15, 8.2), (10, 3.6), (3.66, 10.13)]
T = tbldr.buildTree(leaves=leaves)
tdraw(list(T.nodes)[1:])
plt.show()