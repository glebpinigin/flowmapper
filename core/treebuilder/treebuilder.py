from .events import GeneralQueueHandler
from .wavefronts import W
from .spirals import NodeRegion
from .spiraltree import SpiralTree


def buildTree(root=(0, 0), leaves=None, b=1.9):
    
    never_activated = [NodeRegion(b=b, root=root, leaf=leaf) for leaf in leaves]
    
    queue = GeneralQueueHandler(never_activated) # assign NodeRegions for leaves as terminal events
    w = W()
    T = SpiralTree()
    for event in queue:
        event(w, T, queue)
        # queue.delete(event)
        print(len(queue))
        if len(queue) == 1:
            break
    return T


if __name__ == "__main__":
    leaves = [ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20), (20, 0), (5, 10), (22, 4), (-30, 5), (-35, -6)]
    buildTree(leaves=leaves)

