from multiprocessing import connection
from .distributor.events import GeneralQueueHandler
from .distributor.wavefronts import W
from .distributor.spirals import NodeRegion
from .distributor.spiraltree import SpiralTree, connectionsToWkt
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from .plotting import tdrawCurves

def buildTree(root=(0, 0), leaves=None, alpha=15, logshow=0, bias=(0,0), vol_attrs=None, stop_dst=0):
    
    stacked = np.column_stack(leaves)
    
    extent = [(stacked[0].min(), stacked[1].min()), (stacked[0].max(), stacked[1].max())] # (lowerleft), (upperright)
    #print(extent, "\n")
    if vol_attrs is not None:
        vol_attrs[0].append("count")
        for i in vol_attrs[1]:
            i.append(1)
        never_activated = [NodeRegion(alpha=alpha, root=root, leaf=zipped[0], volumes=zipped[1]) for zipped in zip(leaves, vol_attrs[1])]
    else:
        never_activated = [NodeRegion(alpha=alpha, root=root, leaf=leaf) for leaf in leaves]
        vol_attrs = [["count"]]
    if logshow > 0:
        tdrawCurves(never_activated)
        plt.show()
    
    if vol_attrs is not None:
        T = SpiralTree(root=root, bias=bias, vol_attrs=vol_attrs[0])
    else:
        T = SpiralTree(root=root, bias=bias)
    
    queue = GeneralQueueHandler(never_activated, T, stop_dst=stop_dst) # assign NodeRegions for leaves as terminal events
    w = W()

    for event in queue:
        # if event.val.unpack() == 73.95291165118905:
        #     tdraw(list(T.nodes)[1:])
        #     plt.show()
        event(w, T, queue, extent=extent)
        # queue.delete(event)
        #print(len(queue))
        if logshow > 1:
            tdrawCurves(list(T.nodes)[1:])
            plt.show()
        # if len(queue) == 6:
        #     break
    return T


if __name__ == "__main__":
    leaves = [ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20), (20, 0), (5, 10), (22, 4), (-30, 5), (-35, -6)]
    buildTree(leaves=leaves)

