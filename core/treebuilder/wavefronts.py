from .abtree import AbstractSearchTree

class WData(AbstractBSTData):
    
    def __init__(self, event):
        self.event = event
    
    def unpack(self):
        return self.event.get_polar()["ang"]


class W(AbstractSearchTree):
    pass


class Wo():
    
    def __init__(self):
        """Wavefront with presence of obstackles"""
        pass
