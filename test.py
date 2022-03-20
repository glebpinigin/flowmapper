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
print("Imports succesfull\n")
r = 150
errs = 0
for i in range(r):
    leaves = getLeaf(7)
    #leaves = list(filter(lambda x: x[0] > 0, leaves))
    #leaves.append((-25.11407890334805, -153.18910434475615))
    #leaves = [(-20, 5), (-21, -7)] 
    begin_time = datetime.datetime.now()
    try:
        T = tbldr.buildTree(leaves=leaves, alpha=35, logshow=0)
        times = np.append(times, datetime.datetime.now() - begin_time)
    except Exception:
        errs += 1
        print(f"Error at {i}")
    # tdraw(list(T.nodes)[1:])
    # plt.show()
    # plt.savefig(f"figs/30/fig{i}.png")

print(times)
print(times.mean())
print(f"{errs} errors / {errs/r*100}%")

save = input("Save? y/n ")
save = True if save == "y" else False
if save:
    savename = input("savename? ")
    lines = momepy.nx_to_gdf(T, points=False)
    lines['Wkt'] = lines['Wkt'].apply(wkt.loads)
    lines.set_geometry(col='Wkt', inplace=True)
    lines.to_file(f"../shape/{savename}.shp")