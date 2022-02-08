from .handlers import GeneralQueueHandler
from .wavefronts import W
from .spirals import NodeRegion


class SpiralTree:
    pass


def buildTree(root, leaves):
    
    never_activated = [NodeRegion(b=b, root=root, leaf=leaf) for leaf in leaves]
    
    queue = GeneralQueueuHandler(never_activated) # assign NodeResions for leaves as terminal events
    w = W()
    T = SpiralTree()
    for event in queue:
        event(W, T)
    return T


if __name__ == "__main__":
    # надо добавить сюда тест
    pass

