from .abst import AbstractSearchTree, AbstractBSTData
from .events import TerminalEvent


class GeneralQueueData(AbstractBSTData):
    
    def __init__(self, event):
        self.event = event
    
    def unpack(self):
        return self.event.get_polar()["dst"]
    
    def __call__(self, *args, **kwargs):
        self.event(*args, **kwargs)


class GeneralQueueHandler(AbstractSearchTree):
    
    def __init__(self, init_nodes): # assign NodeRegions for leaves as terminal events
        super().__init__()
        for node in init_nodes:
            tp = TerminalEvent(node)
            val = GeneralQueueData(tp)
            self.insert(val)
            
    
    # перегрузка получения следующего