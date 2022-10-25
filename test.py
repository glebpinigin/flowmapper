from matplotlib import pyplot as plt
from flowmapper.core.drawer.thcktr import thckTr
import flowmapper.core.treebuilder as tbldr
from flowmapper.core import plotting
from expls import *
import numpy as np
import datetime
import networkx as nx
import momepy
from shapely import wkt
from flowmapper.core.drawer import pptr, thcktr

times = np.array([])

import datetime
print("Imports succesfull\n")
r = 1
errs = 0
for i in range(r):
    # preparing sample data
    leaves = getLeaf(8)
    vlarray = np.random.rand(len(leaves))*10000%1000
    vls = [
        ["amount"],
        [[i] for i in vlarray]
    ]
    begin_time = datetime.datetime.now()
    # building tree topology
    T = tbldr.buildTree(leaves=leaves, alpha=35, logshow=0, stop_dst=0, vol_attrs=vls)
    # building tree geometry
    pptr.ppTr(T, 4)
    # smoothing tree geometry
    pptr.smoothTr(T, 21, inplace=True)
    # calculating line widths
    thcktr.thckTr(T, ["amount", "count"], 1, 20, 5, 7)

    times = np.append(times, datetime.datetime.now() - begin_time)

    # testing tree plotting
    plotting.drawTree(T, geom_field="raw_geom")
    plt.clf()
    plotting.drawTree(T, geom_field="spline_geom")
    plt.clf()

print(times)
print(times.mean())
print(f"{errs} errors / {errs/r*100}%")

# save = input("Save? y/n ")
# save = True if save == "y" else False
# if save:
#     savename = input("savename? ")
#     lines = momepy.nx_to_gdf(T, points=False)
#     lines['Wkt'] = lines['Wkt'].apply(wkt.loads)
#     lines.set_geometry(col='Wkt', inplace=True)
#     lines.to_file(f"../shape/{savename}.shp")