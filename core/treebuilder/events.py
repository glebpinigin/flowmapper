from .spiraltree import SpiralTree
from .wavefronts import W, WData
from .local_utils import intersect_curves, rl_inverse
from .spirals import NodeRegion
from .abst import AbstractSearchTree, AbstractBSTData


class GeneralQueueData(AbstractBSTData):
    
    def __init__(self, event):
        self.event = event
    
    def unpack(self):
        return self.event.get_polar()["dst"]
    
    def __call__(self, *args, **kwargs):
        print(f"\n  Event call at {self.unpack()}")
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
        if len(self) == 0:
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
        self._intersection_pars = intersect_curves(self._nds[0].val.get_curve(), self._nds[1].val.get_curve())

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
        print("\n    Terminal event call in")
        T.insertLeaf(self.R)

        val = WData(self.R)
        in_w = w.insert(val)
        # find left and right potential neighbours in W
        nbhood = w.get_nbhood(in_w)
        # check if t inside neighbour's region
        
        
        # find intersections with neibourhood
        for nb in nbhood:
            if nb is None:
                continue
            elif in_w.val.isIntersected(nb):
                print("Found intersected")
                continue
            intersection = Intersection(in_w, nb)
            print(intersection)
            # creating JPEvent from intersection
            new_jp_event = JoinPointEvent(intersection)

            # add created JPEvent to W !!! Do we need this part?
            # new_node = w.insert(WData(new_jp_event))
            # new_jp_event.set_nodeW(new_node)
            # wnode will have to delete jpEvents from w
            jpEvent_node = Q.insert(GeneralQueueData(new_jp_event))
            in_w.val.track_jpEvent(jpEvent_node, nb)
            nb.val.track_jpEvent(jpEvent_node, in_w)
        Q.delete(kwargs["abstnd"])
        print("    Terminal event call out\n")


    def get_polar(self):
        return {"dst": self.R.dst, # angle and dst from NodeRegion
                "ang": self.R.ang}
    
    def get_curve(self):
        return self.R


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
        fake_uplim=fake_uplim)

        self.R = steiner_region
    
    def __call__(self, w, T: SpiralTree, Q, *args, **kwargs):
        print("\n    Join point event call in")
        # cut node curves
        lowerlimit_xy, tp1 = self.intersection.get_intersection_pars()["position_type"]
        tp2 = rl_inverse(tp1)
        curve1, curve2 = self.intersection.get_intersection_pars()["curves"]
        curve1.crop(tp=tp1, lowerlimit_xy=lowerlimit_xy, inplace=True)
        curve2.crop(tp=tp2, lowerlimit_xy=lowerlimit_xy, inplace=True)
        
        T.insertSteinerNode(self.R, curve1, curve2)
        
        # remove JPEvent from queue
        Q.delete(kwargs["abstnd"]) # parent of node is itself!??

        for nd in self.intersection.get_nds():
            w.delete(nd, chosen=kwargs["abstnd"], Q=Q, val=nd.val)
        
        # add TerminalEvent to queue
        tp = TerminalEvent(self.R)
        val = GeneralQueueData(tp)
        Q.insert(val)
        print("    Join point event call out\n")
    
    def get_polar(self):
        return {
                "dst": self.intersection.get_intersection_pars()["dst"],
                "ang": self.intersection.get_intersection_pars()["ang"]}
    
    def get_curve(self):
        return self.R

    def set_nodeW(self, nodeW):
        pass