from .abst import AbstractSearchTree, AbstractBSTData
from .local_utils import rad_back_magic

class WData(AbstractBSTData):
    
    def __init__(self, R):
        self.R = R
        self._iBuddies = [] # Nodes with which intersection is computed
        self._jp_events = []
    
    def unpack(self):
        return rad_back_magic(self.R.ang)
    
    def get_curve(self):
        return self.R
    
    def isIntersected(self, nd):
        print(nd.val in self._iBuddies or self in nd.val._iBuddies)
        return nd.val in self._iBuddies or self in nd.val._iBuddies

    def track_jpEvent(self, jp_event, nd):
        self._iBuddies.append(nd.val)
        self._jp_events.append(jp_event.val)
    
    def flush_jpEvents(self, chosen, Q):
        if not chosen.val in self._jp_events:
            raise Warning("This JPEvent is not being tracked")
        else:
            self._jp_events.remove(chosen.val)
            for eventval in self._jp_events:
                if chosen.val > eventval: # sometimes old nodes stored in events, however they are not in queue
                    Q.delete_by_val(eventval)
            self._jp_events = []


class W(AbstractSearchTree):
    
    def delete(self, z, chosen, Q, val):
        val.flush_jpEvents(chosen, Q)
        super().delete_by_val(z.val)

    def succ(self, node):
        succ = super().succ(node)
        if succ is not None:
            return succ
        else:
            return self.get_min()

    def pred(self, node):
        pred = super().pred(node)
        if pred is not None:
            return pred
        else:
            return self.get_max()


class Wo():
    
    def __init__(self):
        """Wavefront with presence of obstackles"""
        pass
