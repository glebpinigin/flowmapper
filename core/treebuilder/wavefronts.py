from .events import JoinPointEvent
from .spiraltree import SpiralTreeNode
from .abst import AbstractSearchTree, AbstractBSTData

class WData(AbstractBSTData):
    
    def __init__(self, R):
        self.R = R
        self._jp_events = []
    
    def unpack(self):
        return self.R.ang
    
    def get_curve(self):
        return self.R
    
    def track_jpEvent(self, jp_event):
        self._jp_events.append(jp_event)
    
    def flush_jpEvents(self, chosen, Q):
        if not chosen in self._jp_events:
            raise Warning("This JPEvent is not being tracked")
        else:
            self._jp_events.remove(chosen)
            for event in self._jp_events:
                Q.remove(event)


class W(AbstractSearchTree):
    
    def flush_delete(self, node, chosen, Q):
        self.delete(node)
        node.flush_jpEvents(chosen, Q)


class Wo():
    
    def __init__(self):
        """Wavefront with presence of obstackles"""
        pass
