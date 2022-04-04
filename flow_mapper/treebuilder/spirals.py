from functools import update_wrapper
import warnings
import numpy as np
import math, copy
from matplotlib import pyplot as plt
from matplotlib import gridspec
from shapely.geometry import LineString

from .local_utils import dst_bearing, polar_logspiral, rect_logspiral, lrsign, rad_back_magic, rad_magic



class NodeRegion():

    s = 100

    def __init__(self, root=None, leaf=None, fake_params=None, crds=None, alpha=None, fake_uplim=None, volumes=None):
        """Constructor"""
        self.root = (0,0) if root is None else root
        self.leaf = (0,0) if leaf is None else leaf
        self.dst, self.ang = dst_bearing(self.root, self.leaf)
        self.ang = rad_back_magic(self.ang)
        self.params = None
        self.deg_alpha = alpha
        if alpha is None:
                raise ValueError("params_r, params_l, alpha are None. Pass them correctly")
        if fake_params is not None:
            self._build_with_params(fake_params)
        else:
            self.alpha = np.radians(alpha)
            self._build_raw()
        
        self.volumes = np.array([1]) if volumes is None else np.array(volumes)



    def cropUpperPart(self, tp, lowerlimit_phi):
        '''
        Crop curve between leaf and intersection point
        '''
        # Проверки и определения
        sign = lrsign(tp)
        self.tp = tp
        alpha = self.params[tp]["alpha"]
        dst = self.dst
        ang = self.ang
        #thmax = (upperlimit_phi - self.ang) / np.tan(sign*self.alpha)
        if lowerlimit_phi-ang > np.pi:
            lowerlimit_phi = rad_magic(lowerlimit_phi)
        elif ang-lowerlimit_phi > np.pi:
            ang = rad_magic(ang)
        thmin = (lowerlimit_phi - ang) / np.tan(sign*alpha)
        self.th = np.linspace(0, thmin, self.s)
        phi, r = polar_logspiral(alpha, dst, ang, self.th, tp)
        self.params = {
            self.tp: {"alpha": alpha, 
                    "dst": dst, 
                    "ang": ang, 
                    "phi": phi, 
                    "r": r}
        }
        self.crds = {
            f"{tp}_xy": rect_logspiral(r, phi)
        }
    
    def cropLowerPart(self, tp, upperlimit_phi):
        '''
        Get curve between intersection point and root
        return: params, crds
        '''
        sign = lrsign(tp)
        alpha = self.params[tp]["alpha"]
        ang = self.ang
        if upperlimit_phi-self.ang > np.pi:
            upperlimit_phi = rad_magic(upperlimit_phi)
        elif self.ang-upperlimit_phi > np.pi:
            ang = rad_magic(self.ang)
        thmax = (upperlimit_phi - ang) / np.tan(sign*alpha)
        th = np.linspace(thmax, np.pi*(1/np.tan(alpha)), self.s)
        phi, r = polar_logspiral(alpha, self.dst, self.ang, th, tp)
        tp_params = {"alpha": alpha, 
                    "dst": self.dst, 
                    "ang": self.ang, 
                    "phi": phi, 
                    "r": r
                    }
        return tp_params
        
    
    def plot(self, ax1=None, ax2=None, polar = True, **kwargs):
        # Отрисовка кривой внутри всей области определения
        fig = plt.figure(1,(8,4)) if ax1 is None else None
        if polar:
            ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
        ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
        
        xr,yr = self.crds["right_xy"]
        xl,yl = self.crds["left_xy"]
        
        rr = self.params['right']['r']
        phir = self.params['right']['phi']
        rl = self.params['left']['r']
        phil = self.params['left']['phi']

        if polar:
            ax1.plot(phir, rr, "-c")
            ax1.plot(phil, rl, "-m")
        ax2.plot(xr,yr, "-c", **kwargs)
        ax2.plot(xl,yl, "-m", **kwargs)
        ax2.plot(self.leaf[0], self.leaf[1], "og")
        ax2.plot(self.root[0], self.root[1], "sg")
        ax2.set_aspect(1)


    def tplot(self, ax1=None, ax2=None, polar = True, limdraw=False):
        # Отрисовка кривой внутри обрезанной области определения
        fig = plt.figure(1,(8,4)) if ax1 is None else None
        if polar:
            ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
        ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2

        x,y = self.crds[f"{self.tp}_xy"]
        
        if self.tp == 'right':
            sign = -1
            color = 'c'
        else:
            sign =1
            color = 'm'

        if polar:
            ax1.plot(self.params[self.tp]["phi"], self.params[self.tp]["r"], f"-{color}")
        
        ax2.plot(x,y, f"-{color}")

        if limdraw:
            ax2.plot(self.lowerlimit_xy[0], self.lowerlimit_xy[1], "^k")
            ax2.plot(self.upperlimit_xy[0], self.upperlimit_xy[1], "vk")

        ax2.plot(self.leaf[0], self.leaf[1], "og")
        ax2.plot(self.root[0], self.root[1], "sg")
        ax2.set_aspect(1)

    def validate_crds(crds):
        """if crds.keys() are not 'right_xy' or 'left_xy', raises KeyError
        if any of crds.values() is not sequence, raises TypeError
        """
        if not all(list(map(lambda x: x == 'right_xy' or x == 'left_xy', list(crds.keys())))) == True:
            raise KeyError(f"{crds.keys()} are invalid keys. Keys must be ('right_xy', 'left_xy')")
        
        if not all(list(map(lambda x: type(x) in (tuple, list), crds.values()))) == True:
            raise TypeError(f"{crds.values()} are invalid values. Coordinates must be tuples or lists")


    def get_dst2(self):
        '''NB! Read comments inside! still counts dst between lowerlimit and upperlimit'''
        warnings.warn("get_dst2 still counts dst between lowerlimit and upperlimit") # NB!!!
        try:
            return np.sqrt((self.upperlimit_xy[0]-self.lowerlimit_xy[0])**2 + (self.upperlimit_xy[1]-self.lowerlimit_xy[1])**2)
        except AttributeError:
            return self.dst

    def collapseRegion(self, falseLeaf, dummypoint):
        self.tp = "right"
        x = [falseLeaf[0], dummypoint[0], self.leaf[0]]
        y = [falseLeaf[1], dummypoint[1], self.leaf[1]]
        self.params[self.tp] = {
                    "phi": (), 
                    "r": ()
                    }
        self.crds["right_xy"] = [x, y]

    def _build_with_params(self, fake_params):
        self.params = fake_params
        self.crds = {
            "right_xy": rect_logspiral(self.params["right"]["r"], self.params["right"]["phi"]),
            "left_xy": rect_logspiral(self.params["left"]["r"], self.params["left"]["phi"])
        }

    def _build_raw(self):
        self.th = np.linspace(0, np.pi*(1/np.tan(self.alpha)), self.s)
        phir, rr = polar_logspiral(self.alpha, self.dst, self.ang, self.th, "right")
        params_r = {"alpha": self.alpha,
                    "dst": self.dst,
                    "ang": self.ang,
                    "phi": phir,
                    "r": rr}
        phil, rl = polar_logspiral(self.alpha, self.dst, self.ang, self.th, "left")
        params_l = {"alpha": self.alpha, "dst": self.dst, "ang": self.ang, "phi": phil, "r": rl}
        self.params = {
            "right": params_r,
            "left": params_l
        }
        self.crds = {
            "right_xy": rect_logspiral(rr, phir),
            "left_xy": rect_logspiral(rl, phil)
        }


if __name__ == "__main__":
    from local_utils import rl_inverse, tdraw, intersect_curves
    curve0 = NodeRegion((0,0), (10, 8), alpha=35)
    curve1 = NodeRegion((0,0), (-5, 5), alpha=35)

    # draw([curve0, curve1])

    intersection = intersect_curves(curve0, curve1)
    tp0 = intersection["position_type"][1]
    tp1 = rl_inverse(tp0)
    ang = intersection["ang"]
    dst = intersection["dst"]
    inter_crds = tuple(rect_logspiral(dst, ang))
    tp_params0 = curve0.cropLowerPart(tp0, ang)
    tp_params1 = curve1.cropLowerPart(tp1, ang)
    fake_params={
        tp0: tp_params0,
        tp1: tp_params1
    }
    curve2 = NodeRegion((0,0), inter_crds, fake_params, alpha=curve0.alpha)
    tdraw([curve2])
    plt.show()