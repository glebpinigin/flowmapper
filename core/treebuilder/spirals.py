import warnings
import numpy as np
import math, copy
from matplotlib import pyplot as plt
from matplotlib import gridspec
from shapely.geometry import LineString

from .local_utils import dst_bearing, rl_inverse, draw, tdraw, intersect_curves, rad_magic, rad_back_magic, polar_logspiral, rect_logspiral, eval_a_logspiral



class NodeRegion():

    s = 100

    def __init__(self, root=None, leaf=None, params_r=None, params_l=None, crds=None, b=None, fake_uplim=None):
        """Constructor"""
        self.thmax = {'right': np.pi, 'left': np.pi} if fake_uplim is None else fake_uplim

        self.root = (0,0) if root is None else root
        self.leaf = (0,0) if leaf is None else leaf

        self.dst, self.ang = dst_bearing(self.root, self.leaf)
        self.th = np.linspace(0, np.pi, self.s)
        self.params = None
        if params_r is not None and params_l is not None:
            thr = np.linspace(0, self.thmax['right'], self.s)
            thl = np.linspace(0, self.thmax['left'], self.s)

            # надо вычитать из пи разницу угла родительской спирали и текущей спирали перед вычислениями
            rr = polar_logspiral(params_r["a"], params_r["b"], thr)
            rl = polar_logspiral(params_l["a"], params_l["b"], thl)
            # rr = params_r["r"]
            # rl = params_l["r"]
            self.params = {
                "right": {"a": params_r["a"], "b": params_r["b"], "r": rr},
                "left": {"a": params_l["a"], "b": params_l["b"], "r": rl}
            }
            self.crds = {
                "right_xy": rect_logspiral(rr, thr, self.ang+(np.pi-self.thmax['right']), "right"), # вставлен костыль, возвращающий ang к значению родителя
                "left_xy": rect_logspiral(rl, thl, self.ang-(np.pi-self.thmax['left']), "left")
            }
        else:
            if b is None:
                raise ValueError("params_r, params_l, b are None. Pass them correctly")
            else:
                a = eval_a_logspiral(self.dst, b)
                r = polar_logspiral(a, b, self.th)
                params = {"a": a, "b": b, "r": r}
                self.params = {
                    "right": params,
                    "left": params
                }
                self.crds = {
                    "right_xy": rect_logspiral(r, self.th, self.ang, "right"),
                    "left_xy": rect_logspiral(r, self.th, self.ang, "left")
                }



    def crop(self, tp, upperlimit_xy=None, lowerlimit_xy=None, inplace=False):
        '''
        Вырезание кривой между точками
        return: params, crds NOT INPLACE ONLY
        '''
        # Проверки и определения
        assert tp in ('right', 'left'), "tp must be assigned"

        if inplace:
            self.tp = tp
            self.upperlimit_xy = self.leaf if upperlimit_xy is None else upperlimit_xy
            self.lowerlimit_xy = self.root if lowerlimit_xy is None else lowerlimit_xy
        thmax = self.thmax[tp]
        # Расчет
        sign = 1 if tp == 'right' else -1

        # upperlimit is a final point for drowing from root to leaf
        if upperlimit_xy is not None:
            uplt_th_ang = np.arctan2(upperlimit_xy[1]-self.root[1], upperlimit_xy[0]-self.root[0])

            # this if statement handles situation, when intersection is above zero and leaf is below zero
            # withput this statemnt ~limit_th calculation is incorrect
            difference = rad_back_magic(sign*(rad_magic(self.ang) - rad_magic(uplt_th_ang)))

            upperlimit_th = thmax - difference
        else:
            upperlimit_th = thmax

        # lowerlimit is an intial point for drawing from root to leaf
        if lowerlimit_xy is not None:
            lwlt_th_ang = np.arctan2(lowerlimit_xy[1]-self.root[1], lowerlimit_xy[0]-self.root[0])

            # this if statement handles situation, when intersection is above zero and leaf is below zero
            # withput this statemnt ~limit_th calculation is incorrect
            difference = rad_back_magic(sign*(rad_magic(self.ang) - rad_magic(lwlt_th_ang)))

            lowerlimit_th = thmax - difference
        else:
            lowerlimit_th = 0

        # Запись результата inplace
        if inplace:
            self.th = np.linspace(lowerlimit_th, upperlimit_th, self.s)

            a = self.params[tp]['a']
            b = self.params[tp]['b']
            r = polar_logspiral(a, b, self.th)
            self.params = {
                self.tp: {"a": a, "b": b, "r": r}
            }
            self.crds = {
                f"{tp}_xy": rect_logspiral(r, self.th, self.ang + (np.pi-self.thmax[tp])*sign, tp)
            }
        else:
            th = np.linspace(lowerlimit_th, upperlimit_th, self.s)
            a = self.params[tp]['a']
            b = self.params[tp]['b']
            r = polar_logspiral(a, b, self.th) # check if self is needed with th
            params = {
                tp: {"a": a, "b": b, "r": r}
            }
            return params, upperlimit_th
        
    
    def plot(self, ax1=None, ax2=None, polar = True, **kwargs):
        # Отрисовка кривой внутри всей области определения
        fig = plt.figure(1,(15,15)) if ax1 is None else None
        if polar:
            ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
        ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
        
        xr,yr = self.crds["right_xy"]
        xl,yl = self.crds["left_xy"]
        
        rr = self.params['right']['r']
        rl = self.params['left']['r']
        
        if polar:
            ax1.plot(self.th, rr, "-c")
            ax1.plot(-self.th, rl, "-m")
        ax2.plot(xr,yr, "-c", **kwargs)
        ax2.plot(xl,yl, "-m", **kwargs)
        ax2.plot(self.leaf[0], self.leaf[1], "og")
        ax2.plot(self.root[0], self.root[1], "sg")
        ax2.set_aspect(1)


    def tplot(self, ax1=None, ax2=None, polar = True, limdraw=False):
        # Отрисовка кривой внутри обрезанной области определения
        fig = plt.figure(1,(15,15)) if ax1 is None else None
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
            ax1.plot(self.th*sign, self.params[self.tp]["r"], f"-{color}")
        
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

    def collapseRegion(self, root, leaf):
        self.tp = "right"
        self.crds["right_xy"] = [(root[0], leaf[0]), (root[1], leaf[1])]


class FlowTreeBuilder():

    def __init__(self, root=(0,0), leaves=[ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20)], b=1.9, vbs=False):
        self.root = root
        self.leaves = leaves
        self.b = b
        self.vbs = vbs
        self.arcs = self.main_exec(self.root, self.leaves, self.b)
        
    
    def main_exec(self, root, leaves, b):
        
        fig = plt.figure(1,(20,10), facecolor='gray')
        spec = gridspec.GridSpec(ncols=3, nrows=1,
                         width_ratios=[1, 2, 2], wspace=0.5,
                         hspace=0.5)

        ax1 = fig.add_subplot(spec[0],polar=True, facecolor='white')
        ax2 = fig.add_subplot(spec[1],polar=False, facecolor='white')
        ax3 = fig.add_subplot(spec[2],polar=False, facecolor='white')

        never_activated = [NodeRegion(b=b, root=root, leaf=leaf) for leaf in leaves]

        draw(never_activated, ax1=ax1, ax2=ax2, polar=False)

        ax3.set_xlim(ax2.get_xlim())
        ax3.set_ylim(ax2.get_ylim())

        active = []
        result_curves = []

        C = max(list(map(lambda x: x.dst, never_activated)))
        C -= 0.01
        while C > 0:
            # creating queue
            active = list(filter(lambda x: x.get_dst2() > C, never_activated))

            # intersecting
            intersections = []
            interm = active.copy()
            for curve in active:
                interm.remove(curve)
                for c in interm:
                    # NOT HANDLES NONE OUTPUT FROM INTERSECT
                    intersections.append(intersect_curves(curve, c, plotting=True, ax=ax2))
            try:
                del c, interm
            except UnboundLocalError:
                del interm

            # filtering intersections
            for join_position in filter(lambda x: x["dst"] > C, intersections):
                print(join_position['dst'])
                # unpacking intersection
                lowerlimit_xy, tp1 = join_position["position_type"]
                tp2 = rl_inverse(tp1)
                curve1, curve2 = join_position["curves"]
                
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
                terminal_from_joinpoint = NodeRegion(root=self.root, 
                leaf=lowerlimit_xy, 
                params_l=params_l['left'], 
                params_r=params_r['right'],
                fake_uplim=fake_uplim)

                # cropping curves
                curve1.crop(tp=tp1, lowerlimit_xy=lowerlimit_xy, inplace=True)
                curve2.crop(tp=tp2, lowerlimit_xy=lowerlimit_xy, inplace=True)
                
                
                
                for i in (curve1, curve2):
                    never_activated.remove(i)
                    result_curves.append(i)
                never_activated.append(terminal_from_joinpoint)
                
            

            C-=0.01
        
        tdraw(result_curves, ax1=ax1, ax2=ax3, polar=False)

        return




if __name__ == "__main__":
    # some tests
    leaves = [ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20), (20, 0), (5, 10), (22, 4), (-30, 5), (-35, -6)]
    leaves = [ (10, 0), (10, 10), (0, 9), (15, 8.2), (10, 3.6)]
    leaves = [ (10, 0), (10, 10), (0, 9), (15, 8.2), (10, 3.6), (17, 4.1)]
    expl = FlowTreeBuilder(b=1.9, leaves=leaves, vbs=False)
    plt.show()



