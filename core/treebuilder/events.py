from .wavefronts import WData

class TerminalEvent:
    
    def __init__(self, node):
        self.R = node
    
    def __call__(self, w, T):
        
        # find left and right potential neighbours in W
        neibourhood = 
        # check if t inside neighbour's region
        val = WData(self)
        self.in_w = w.insert(val, True)
        
        # find intersections with neibourhood

    def get_polar(self):
        return {"dst": self.R.dst, # angle and dst from NodeRegion
                "ang": self.R.ang}


class JoinPointEvent:
    pass

