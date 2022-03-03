from .abst import AbstractSearchTree, AbstractBSTData

class WData(AbstractBSTData):
    
    def __init__(self, R):
        self.R = R
        self._iBuddies = [] # Nodes with which intersection is computed
        self._jp_events = []
    
    def unpack(self):
        return self.R.ang
    
    def get_curve(self):
        return self.R
    
    def isIntersected(self, nd):
        print(nd.val in self._iBuddies or self in nd.val._iBuddies)
        return nd.val in self._iBuddies or self in nd.val._iBuddies

    def track_jpEvent(self, jp_event, nd):
        self._iBuddies.append(nd.val)
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
