from matplotlib import pyplot as plt
import core.treebuilder.treebuilder as tbldr
from core.treebuilder.local_utils import tdraw
from expls import *
import numpy as np
import datetime

times = np.array([])

import datetime

for i in range(25):
    leaves = getLeaf(7)
    #leaves = list(filter(lambda x: x[0] > 0, leaves))
    #leaves.append((-25.11407890334805, -153.18910434475615))
    begin_time = datetime.datetime.now()
    T = tbldr.buildTree(leaves=leaves)
    tdraw(list(T.nodes)[1:])
    # plt.show()
    plt.savefig(f"figs/30/fig{i}.png")
    times = np.append(times, datetime.datetime.now() - begin_time)

print(times)
print(times.mean())