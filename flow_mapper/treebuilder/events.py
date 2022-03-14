import numpy as np
from .spiraltree import SpiralTree
from .wavefronts import W, WData
from .local_utils import intersect_curves, rl_inverse, intersect
from .spirals import NodeRegion
from .abst import AbstractSearchTree, AbstractBSTData


class GeneralQueueData(AbstractBSTData):
    
    def __init__(self, event):
        self.event = event
    
    def unpack(self):
        return self.event.get_polar()["dst"]
    
    def __call__(self, *args, **kwargs):
        # print(f"\n  Event call at {self}, {self.event.R.leaf}")
        self.event(*args, **kwargs)


class GeneralQueueHandler(AbstractSearchTree):
    
    def __init__(self, init_nodes): # assign NodeRegions for leaves as terminal events
        super().__init__()
        for node in init_nodes:
            tp = TerminalEvent(node)
            val = GeneralQueueData(tp)
            self.insert(val)
            
    def __iter__(self):
        return self

    def __next__(self):
        if self.root == self.nil:
            raise StopIteration
        return self.get_max()
    
    def delete(self, *args, **kwargs):
        super()._delete(*args, **kwargs)


class Intersection:

    def __init__(self, *args):
        """
        args: exactly 2 wavefront nodes
        """
        self._nds = (args[0], args[1])
        self._intersection_pars = intersect_curves(self._nds[0].get_curve(), self._nds[1].get_curve())

    def get_nds(self):
        return self._nds
    
    def get_intersection_pars(self):
        return self._intersection_pars
    
    def __repr__(self):
        return self._intersection_pars.__repr__()

class TerminalEvent:
    
    def __init__(self, R):
        self.R = R # spiral region assigned with terminal event
    
    def __call__(self, w: W, T: SpiralTree, Q, *args, **kwargs):
        # print("\n    Terminal event call in")
        T.insertLeaf(self.R)

        val = WData(self.R)
        in_w = w.insert(val)
        # find left and right potential neighbours in W
        nbhood = w.get_nbhood(in_w)
        
        # working with neighbours
        for nb in nbhood:
            if nb == in_w.val:
                continue
            elif in_w.val.isIntersected(nb):
                # print("Found intersected")
                continue
            # check if t inside neighbour's region
            out_key = checkUnderlying(in_w.val, nb, kwargs["extent"])
            if out_key:
                self.R.volume += nb.R.volume
                T.repairUnderlying(in_w.val.R, nb.R)
                w.delete(Q=Q, val=nb, chosen=None)
                nb.R.collapseRegion(self.R.leaf, nb.R.leaf)
                continue
            # find intersections with neibourhood
            intersection = Intersection(in_w.val, nb)
            # print(intersection)
            # creating JPEvent from intersection
            new_jp_event = JoinPointEvent(intersection)

            # add created JPEvent to W !!! Do we need this part?
            # new_node = w.insert(WData(new_jp_event))
            # new_jp_event.set_nodeW(new_node)
            # wnode will have to delete jpEvents from w
            jpEvent_node = Q.insert(GeneralQueueData(new_jp_event))
            in_w.val.track_jpEvent(jpEvent_node.val, nb)
            nb.track_jpEvent(jpEvent_node.val, in_w.val)
        Q.delete_by_val(kwargs["abstnd"].val)
        # print("    Terminal event call out\n")


    def get_polar(self):
        return {"dst": self.R.dst, # angle and dst from NodeRegion
                "ang": self.R.ang}
    
    def get_curve(self):
        return self.R

def checkUnderlying(close_val, far_val, extent) -> bool:
    # building region as linestring
    x1, y1 = far_val.R.crds["right_xy"]
    x12, y12 = far_val.R.crds["left_xy"]
    x1 = np.append(x1, x12[-2::-1])
    y1 = np.append(y1, y12[-2::-1])
    # duilding checker line
    x2, y2 = close_val.R.leaf
    x22, y22 = extent[1]
    x2 = (x2, x22)
    y2 = (y2, y22)
    # intersecting
    intersection = intersect((x1, y1), (x2, y2))
    # checking number of intersections
    if len(intersection) == 2 or intersection == ((),):
        out_key = False
    else:
        out_key = True
    return out_key

class JoinPointEvent:
    
    def __init__(self, intersection: Intersection):
        self.intersection = intersection
        intersection_pars = intersection.get_intersection_pars()
        # unpacking intersection
        lowerlimit_xy, tp1 = intersection_pars["position_type"]
        tp2 = rl_inverse(tp1)
        curve1, curve2 = intersection_pars["curves"]
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
        fake_uplim=fake_uplim, 
        volume=curve1.volume+curve2.volume)

        self.R = steiner_region
    
    def __call__(self, w, T: SpiralTree, Q, *args, **kwargs):
        # print("\n    Join point event call in")
        # cut node curves
        lowerlimit_xy, tp1 = self.intersection.get_intersection_pars()["position_type"]
        tp2 = rl_inverse(tp1)
        curve1, curve2 = self.intersection.get_intersection_pars()["curves"]
        curve1.crop(tp=tp1, lowerlimit_xy=lowerlimit_xy, inplace=True)
        curve2.crop(tp=tp2, lowerlimit_xy=lowerlimit_xy, inplace=True)
        
        T.insertSteinerNode(self.R, curve1, curve2)
        
        # remove JPEvent from queue
        Q.delete_by_val(kwargs["abstnd"].val) # parent of node is itself!??

        for val in self.intersection.get_nds():
            w.delete(chosen=kwargs["abstnd"], Q=Q, val=val)
        
        # add TerminalEvent to queue
        tp = TerminalEvent(self.R)
        val = GeneralQueueData(tp)
        Q.insert(val)
        # print("    Join point event call out\n")
    
    def get_polar(self):
        return {
                "dst": self.intersection.get_intersection_pars()["dst"],
                "ang": self.intersection.get_intersection_pars()["ang"]}
    
    def get_curve(self):
        return self.R

    def set_nodeW(self, nodeW):
        pass