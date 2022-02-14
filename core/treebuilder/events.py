from .wavefronts import WData
from .local_utils import intersect

class TerminalEvent:
    
    def __init__(self, node):
        self.R = node # spiral region assigned with terminal event
    
    def __call__(self, w, T):
        
        val = WData(self) # inserting terminal event into W
        self.in_w = w.insert(val, True)
        # find left and right potential neighbours in W
        nbhood = w.get_nbhood(self.in_w)
        # check if t inside neighbour's region
        
        
        # find intersections with neibourhood
        for nb in nbhood:
            nbR = nb.get_curve()
            intersection = intersect(self.R, nbR)
            # create R from intersection
            # add created R to W
        
    def get_polar(self):
        return {"dst": self.R.dst, # angle and dst from NodeRegion
                "ang": self.R.ang}


class JoinPointEvent:
    
    def __init__(self, intersection):
        self.intersection = intersection
    
    def __call__(self, w, T):
        pass
    
    def get_polar(self):
        return {
                "dst": self.intersection["dst"],
                "ang": self.intersection["ang"]}