import warnings
import numpy as np
from .local_utils import dst_bearing, polar_logspiral, lrsign, rad_back_magic, rad_magic



class NodeRegion():


    def __init__(self, root=None, leaf=None, fake_params=None, alpha=None, volumes=None):
        """Base class for modelling spiral regions"""
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
            #self.th = np.linspace(0, np.pi*(1/np.tan(self.alpha)), self.s)
            self._build_raw()
        
        self.volumes = np.array([1]) if volumes is None else np.array(volumes)


    def cropUpperPart(self, tp, lowerlimit_phi):
        '''
        Crop curve between leaf and intersection point
        '''
        sign = lrsign(tp)
        self.tp = tp
        alpha = self.params[tp]["alpha"]
        th_domain = self.params[tp]["th_domain"]
        dst = self.dst
        ang = self.ang

        if lowerlimit_phi-ang > np.pi:
            lowerlimit_phi = rad_magic(lowerlimit_phi)
        elif ang-lowerlimit_phi > np.pi:
            ang = rad_magic(ang)
        thmin = (lowerlimit_phi - ang) / np.tan(sign*alpha)
        th_domain = np.array([0, thmin])
        phi_domain, r_domain = polar_logspiral(alpha, dst, self.ang, th_domain, tp) # SELF.ANG IS CRITICAL!!!
        self.params = {
            self.tp: {"alpha": alpha, 
                    "dst": dst, 
                    "ang": self.ang,
                    "th_domain": th_domain,
                    "phi_domain": phi_domain,
                    "r_domain": r_domain}
        }
    

    def cropLowerPart(self, tp, upperlimit_phi):
        '''
        Get curve between intersection point and root
        return: params, crds
        '''
        sign = lrsign(tp)
        alpha = self.params[tp]["alpha"]
        th_domain = self.params[tp]["th_domain"]
        ang = self.ang
        dst = self.dst
        
        if upperlimit_phi-self.ang > np.pi:
            upperlimit_phi = rad_magic(upperlimit_phi)
        elif self.ang-upperlimit_phi > np.pi:
            ang = rad_magic(self.ang)
        thmax = (upperlimit_phi - ang) / np.tan(sign*alpha)
        th_domain = np.array((thmax, np.pi*(1/np.tan(alpha))))
        phi_domain, r_domain = polar_logspiral(alpha, dst, self.ang, th_domain, tp) # SELF.ANG IS CRITICAL!!!
        tp_params = {"alpha": alpha, 
                    "dst": dst, 
                    "ang": self.ang,
                    "th_domain": th_domain,
                    "phi_domain": phi_domain,
                    "r_domain": r_domain
                    }
        return tp_params


    def get_dst2(self):
        '''NB! Read comments inside! still counts dst between lowerlimit and upperlimit'''
        warnings.warn("get_dst2 still counts dst between lowerlimit and upperlimit") # NB!!!
        try:
            return np.sqrt((self.upperlimit_xy[0]-self.lowerlimit_xy[0])**2 + (self.upperlimit_xy[1]-self.lowerlimit_xy[1])**2)
        except AttributeError:
            return self.dst


    def collapseRegion(self, ntp, inter_crds, leaf, addtn):
        self.tp = ntp
        x = []
        y = []
        for pt in (inter_crds, leaf, addtn, self.leaf):
            x.append(pt[0])
            y.append(pt[1])
        self.params[self.tp] = {}
        self.crds = [x, y]


    def _build_with_params(self, fake_params):
        self.params = fake_params


    def _build_raw(self):
        self.params = {}
        alpha = np.radians(self.deg_alpha)
        th_domain = np.array((0, np.pi*(1/np.tan(alpha))))
        phi_domain, r_domain = polar_logspiral(alpha, self.dst, self.ang, th_domain, "right")
        params_r = {"alpha": alpha, "dst": self.dst, "ang": self.ang, "th_domain": th_domain, "phi_domain": phi_domain, "r_domain": r_domain}
        self.params["right"] = params_r
        phi_domain, r_domain = polar_logspiral(alpha, self.dst, self.ang, th_domain, "left")
        params_l = {"alpha": alpha, "dst": self.dst, "ang": self.ang, "th_domain": th_domain, "phi_domain": phi_domain, "r_domain": r_domain}
        self.params["left"] = params_l
