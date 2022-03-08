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
        print(nd in self._iBuddies or self in nd._iBuddies)
        return nd in self._iBuddies or self in nd._iBuddies

    def track_jpEvent(self, jp_event, nd):
        self._iBuddies.append(nd)
        self._jp_events.append(jp_event)
    
    def flush_jpEvents(self, chosen=None, Q=None):
        if chosen is not None:
            if not chosen.val in self._jp_events:
                raise Warning("This JPEvent is not being tracked")
            else:
                self._jp_events.remove(chosen.val)
        for eventval in self._jp_events:
            Q.delete_by_val(eventval)

        self._jp_events = []


class W(AbstractSearchTree):
    
    def delete(self, chosen, Q, val):
        val.flush_jpEvents(chosen, Q)
        super().delete_by_val(val)

    def get_nbhood(self, node):
        pred = self.pred(node)
        if pred is None:
            pred = self.get_max()
        succ = self.succ(node)
        if succ is None:
            succ = self.get_min()
        return (pred.val, succ.val)


class Wo():
    
    def __init__(self):
        """Wavefront with presence of obstackles"""
        pass
