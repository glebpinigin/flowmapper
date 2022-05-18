from lib2to3.pytree import Node
from urllib.parse import _SplitResultBase
import numpy as np
from .spiraltree import SpiralTree
from .wavefronts import W, WData
from .local_utils import intersect_curves, rl_inverse, intersect_num, rect_logspiral
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
    
    def __init__(self, init_nodes, T: SpiralTree, stop_dst=0): # assign NodeRegions for leaves as terminal events
        super().__init__()
        for node in init_nodes:
            tp = TerminalEvent(node, T)
            val = GeneralQueueData(tp)
            self.insert(val)
        self.stop_dst = stop_dst
            
    def __iter__(self):
        return self

    def __next__(self):
        if self.root == self.nil:
            raise StopIteration
        elif self.get_max().val.unpack() < self.stop_dst:
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
    
    def __init__(self, R: NodeRegion, T: SpiralTree):
        self.R = R # spiral region assigned with terminal event
        T.insertLeaf(self.R)
    
    def __call__(self, w: W, T: SpiralTree, Q, *args, **kwargs):
        # print("\n    Terminal event call in")

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
            # find intersection with neighbour
            # TODO: убрать костыли, убрать лишнюю функцию checkUnderlying
            try:
                intersection = Intersection(in_w.val, nb)
                out_key = False
            except Warning:
                out_key = True
            #out_key = checkUnderlying(in_w.val, nb, kwargs["extent"])
            if out_key:
                out_volumes = self.R.volumes + nb.R.volumes
                w.delete(Q=Q, val=nb, chosen=None)
                w.delete(Q=Q, val=in_w.val, chosen=None)
                mid_ang = nb.R.ang
                new_r = self.R.dst
                # unpack right spiral params from nb.R
                alpha, dst, ang, _, _ = nb.R.params["right"].values()
                new_phi_r = -np.log(new_r/dst)*np.tan(alpha) + ang
                # unpack left spiral params from nb.R
                alpha, dst, ang, _, _ = nb.R.params["left"].values()
                new_phi_l = np.log(new_r/dst)*np.tan(alpha) + ang
                q = (mid_ang - new_phi_l)/2
                q1 = mid_ang - q
                q3 = mid_ang + q
                quartiles = {self.R.ang-i: i for i in [new_phi_l, q1, mid_ang, q3, new_phi_r]}
                quartiles.pop(min(quartiles.keys(), key=lambda x: abs(x)))
                new_phi = quartiles[min(quartiles.keys(), key=lambda x: abs(x))]
                leaf = tuple(rect_logspiral(new_r, new_phi))
                new = NodeRegion(root=self.R.root, leaf=leaf, alpha=self.R.deg_alpha)
                intersection = intersect_curves(self.R, new)

                tp0 = intersection["position_type"][1]
                tp1 = rl_inverse(tp0)
                i_phi = intersection["ang"]
                inter_crds = intersection["position_type"][0]
                curve0, curve1 = intersection["curves"]
                # calculating parameters for creating new NodeRegion for false-connection
                tp_params0 = curve0.cropLowerPart(tp0, i_phi)
                tp_params1 = curve1.cropLowerPart(tp1, i_phi)
                fake_params={
                    tp0: tp_params0,
                    tp1: tp_params1
                }
                # creating NodeRegion for false-connection
                falseR = NodeRegion(curve1.root, inter_crds, fake_params,alpha=curve1.deg_alpha, volumes=out_volumes)

                T.insertFalseNode(falseR, self.R, nb.R, collapse_args = (inter_crds, leaf))
                self.R.cropUpperPart(tp0, i_phi)
                tp = TerminalEvent(falseR, T)
                val = GeneralQueueData(tp)
                Q.insert(val)
                break
            
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
    if far_val.R.leaf != extent[1]:
        x22, y22 = extent[1]
    else:
        x22, y22 = extent[0]
    x2 = (x2, x22)
    y2 = (y2, y22)
    # intersecting
    intersection = intersect_num((x1, y1), (x2, y2))
    # checking number of intersections
    if len(intersection) == 2 or intersection == ((),):
        out_key = False
    else:
        out_key = True
    return out_key

class JoinPointEvent:
    
    def __init__(self, intersection: Intersection):
        self.intersection = intersection
        intersection = intersection.get_intersection_pars()
        # unpacking intersection
        tp0 = intersection["position_type"][1]
        tp1 = rl_inverse(tp0)
        i_phi = intersection["ang"]
        inter_crds = intersection["position_type"][0]
        curve0, curve1 = intersection["curves"]
        # calculating parameters for creating new NodeRegion for SteinerNode
        tp_params0 = curve0.cropLowerPart(tp0, i_phi)
        tp_params1 = curve1.cropLowerPart(tp1, i_phi)
        fake_params={
            tp0: tp_params0,
            tp1: tp_params1
        }
        # creating NodeRegion for SteinerNode
        steiner_region = NodeRegion(curve1.root, inter_crds, fake_params, alpha=curve1.deg_alpha, volumes=curve0.volumes+curve1.volumes)

        self.R = steiner_region
    
    def __call__(self, w, T: SpiralTree, Q, *args, **kwargs):
        # print("\n    Join point event call in")
        # cut node curves
        intersection = self.intersection.get_intersection_pars()
        ang = intersection["ang"]
        curve0, curve1 = intersection["curves"]
        tp0 = intersection["position_type"][1]
        tp1 = rl_inverse(tp0)
        curve0.cropUpperPart(tp=tp0, lowerlimit_phi=ang)
        curve1.cropUpperPart(tp=tp1, lowerlimit_phi=ang)
        
        T.insertSteinerNode(self.R, curve0, curve1)
        
        # remove JPEvent from queue
        Q.delete_by_val(kwargs["abstnd"].val)

        for val in self.intersection.get_nds():
            w.delete(chosen=kwargs["abstnd"], Q=Q, val=val)
        
        # add TerminalEvent to queue
        tp = TerminalEvent(self.R, T)
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