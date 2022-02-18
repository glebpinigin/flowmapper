from .handlers import GeneralQueueHandler
from .wavefronts import W
from .spirals import NodeRegion
from .spiraltree import SpiralTree


def buildTree(root, leaves, b=1.9):
    
    never_activated = [NodeRegion(b=b, root=root, leaf=leaf) for leaf in leaves]
    
    queue = GeneralQueueHandler(never_activated) # assign NodeRegions for leaves as terminal events
    w = W()
    T = SpiralTree()
    for event in queue:
        event(w, T)
        queue.remove(event)
        del event
    return T


if __name__ == "__main__":
    # надо добавить сюда тест
    pass

