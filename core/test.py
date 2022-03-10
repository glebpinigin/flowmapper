from matplotlib import pyplot as plt
import treebuilder.treebuilder as tbldr
from treebuilder.local_utils import tdraw
from expls import *
import numpy as np
import datetime
import networkx as nx
import momepy
from shapely import wkt

times = np.array([])

import datetime

for i in range(100):
    leaves = getLeaf(7)
    #leaves = list(filter(lambda x: x[0] > 0, leaves))
    #leaves.append((-25.11407890334805, -153.18910434475615))
    begin_time = datetime.datetime.now()
    T = tbldr.buildTree(leaves=leaves, bias = (64124.627402732105, -1502323.79394796))
    times = np.append(times, datetime.datetime.now() - begin_time)
    # tdraw(list(T.nodes)[1:])
    # plt.show()
    #plt.savefig(f"figs/30/fig{i}.png")
    

print(times)
print(times.mean())

# lines = momepy.nx_to_gdf(T, points=False)
# lines['Wkt'] = lines['Wkt'].apply(wkt.loads)
# lines.set_geometry(col='Wkt', inplace=True)
# lines.to_file("../shape/shape4.shp")