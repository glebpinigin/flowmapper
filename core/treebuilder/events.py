from .spiraltree import SpiralTree
from .wavefronts import W, WData
from .local_utils import intersect_curves, rl_inverse
from .spirals import NodeRegion

class TerminalEvent:
    
    def __init__(self, node):
        self.R = node # spiral region assigned with terminal event
    
    def __call__(self, w: W, T: SpiralTree):
        
        sptr_node = T.insertLeaf(self.R)# inserting sptr_node to T
        # inserting sptr_node to W
        val = WData(sptr_node) # inserting terminal event into W
        in_w = w.insert(val)
        # find left and right potential neighbours in W
        nbhood = w.get_nbhood(in_w)
        # check if t inside neighbour's region
        
        
        # find intersections with neibourhood
        for nb in nbhood:
            intersection = intersect_curves(in_w.get_curve(), nb.get_curve())
            # creating Spiral Region from intersection
            new_jp_event = JoinPointEvent(intersection)

            # add created R to W
            new_node = w.insert(new_jp_event, rt=True)
            new_jp_event.set_nodeW(new_node)
            sptr_node.track_jpEvent(new_jp_event)
            nb.track_jpEvent(new_jp_event)


    def get_polar(self):
        return {"dst": self.R.dst, # angle and dst from NodeRegion
                "ang": self.R.ang}


class JoinPointEvent:
    
    def __init__(self, intersection):
        self.intersection = intersection
        # unpacking intersection
        lowerlimit_xy, tp1 = intersection["position_type"]
        tp2 = rl_inverse(tp1)
        curve1, curve2 = intersection["curves"]
        # calculating parameters for creating new NodeRegion for SteinerNode
        params1, uplim_th_1 = curve1.crop(tp=tp1, upperlimit_xy=lowerlimit_xy)
        params2, uplim_th_2 = curve2.crop(tp=tp2, upperlimit_xy=lowerlimit_xy)
        fake_uplim = {
            tp1: uplim_th_1,
            tp2: uplim_th_2
            }
        # define which of curves is left and which is right
        params_l = list(filter(lambda x: "left" in list(x.keys()), (params1, params2)))[0]
        params_r = list(filter(lambda x: "right" in list(x.keys()), (params1, params2)))[0]
        # creating NodeRegion for SteinerNode
        steiner_region = NodeRegion(root=curve1.root, # КОСТЫЛЬ. Как бы очевидно, что root у всех один. Но этот класс не расширится на ситуацию, когда корней несколько
        leaf=lowerlimit_xy, 
        params_l=params_l['left'], 
        params_r=params_r['right'],
        fake_uplim=fake_uplim)

        self.R = steiner_region
    
    def __call__(self, w, T: SpiralTree):
        # обрезать кривые узлов
        lowerlimit_xy, tp1 = self.intersection["position_type"]
        tp2 = rl_inverse(tp1)
        curve1, curve2 = self.intersection["curves"]
        curve1.crop(tp=tp1, lowerlimit_xy=lowerlimit_xy, inplace=True)
        curve2.crop(tp=tp2, lowerlimit_xy=lowerlimit_xy, inplace=True)
        # вызвать T.insertSteinerNode()
        T.insertSteinerNode()
        # удалить u и v из W
        # добавить себя в W
        pass
    
    def get_polar(self):
        return {
                "dst": self.intersection["dst"],
                "ang": self.intersection["ang"]}