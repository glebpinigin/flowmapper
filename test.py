from matplotlib import pyplot as plt
from flow_mapper.core.drawer.thcktr import thckTr
import flow_mapper.core.treebuilder as tbldr
from flow_mapper.core import plotting
from expls import *
import numpy as np
import datetime
import networkx as nx
import momepy
from shapely import wkt
from flow_mapper.core.drawer import pptr, thcktr

times = np.array([])

import datetime
print("Imports succesfull\n")
r = 1
errs = 0
for i in range(r):
    leaves = getLeaf(8)
    # vls = [
    #     ["amount"],
    #     [[5], [3], [4], [1], [9]]
    # ]
    # leaves = list(filter(lambda x: x[0] > 0, leaves))
    #leaves.append((-25.11407890334805, -153.18910434475615))
    #leaves = [(-20, 5), (-21, -7)] 
    begin_time = datetime.datetime.now()
    # try:
    # T = tbldr.buildTree(leaves=leaves, alpha=35, logshow=0, stop_dst=0, vol_attrs=vls)
    T = tbldr.buildTree(leaves=leaves, alpha=35, logshow=0, stop_dst=0)
    times = np.append(times, datetime.datetime.now() - begin_time)
    # except Exception as e:
    #     errs += 1
    #     print(f"Error {e} at {i}")
    # tdraw(list(T.nodes)[1:])
    # plt.show()
    # plt.savefig(f"../figs/40/fig{i}.png")
    # plt.clf()

print(times)
print(times.mean())
print(f"{errs} errors / {errs/r*100}%")

pptr.ppTr(T, 4)
plotting.drawTree(T)
# pptr.run()
plt.show()

thcktr.thckTr(T, ["amount", "count"], 1, 20, 5, 7)
for node1, node2, data in T.edges.data():
        print(data)
save = input("Save? y/n ")
save = True if save == "y" else False
if save:
    savename = input("savename? ")
    lines = momepy.nx_to_gdf(T, points=False)
    lines['Wkt'] = lines['Wkt'].apply(wkt.loads)
    lines.set_geometry(col='Wkt', inplace=True)
    lines.to_file(f"../shape/{savename}.shp")