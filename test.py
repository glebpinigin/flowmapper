from matplotlib import pyplot as plt
import flow_mapper.treebuilder.treebuilder as tbldr
from flow_mapper.treebuilder.local_utils import tdraw
from expls import *
import numpy as np
import datetime
import networkx as nx
import momepy
from shapely import wkt

times = np.array([])

import datetime

for i in range(1):
    leaves = getLeaf(7)
    #leaves = list(filter(lambda x: x[0] > 0, leaves))
    #leaves.append((-25.11407890334805, -153.18910434475615))
    begin_time = datetime.datetime.now()
    T = tbldr.buildTree(leaves=leaves)
    # tdraw(list(T.nodes)[1:])
    # plt.show()
    #plt.savefig(f"figs/30/fig{i}.png")
    times = np.append(times, datetime.datetime.now() - begin_time)

print(times)
print(times.mean())

lines = momepy.nx_to_gdf(T, points=False)
lines['Wkt'] = lines['Wkt'].apply(wkt.loads)
lines.set_geometry(col='Wkt', inplace=True)
lines.to_file("../shape/shape3.shp")