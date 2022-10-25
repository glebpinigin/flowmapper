import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import LineString, Point, MultiPoint
import warnings

def polar_logspiral(alpha, dst, ang, th, tp):
    sign = lrsign(tp)
    phi = ang + sign*np.tan(alpha)*th
    r = dst*(np.exp(-th))
    return  phi, r


def lrsign(key):
    assert key in ('right', 'left'), "must be 'right' or 'left'"
    if key =='right':
        return 1
    else:
        return -1


def signlr(sign):
    assert sign in (-1, 1), "must be 1 or -1"
    if sign == -1:
        return "left"
    else:
        return "right"


def rect_logspiral(r, phi):

    x = r*np.cos(phi)
    y = r*np.sin(phi)
    return [x, y]


def calcR(phi, params, tp):
    dst = params[tp]["dst"]
    ang = params[tp]["ang"]
    alpha = params[tp]["alpha"]
    sign = lrsign(tp)
    return dst*np.exp(-(phi-ang) / np.tan(sign*alpha))


def dst_bearing(a, b):
    '''
    Calculates distance and bearing between points.
    params a, b: sequences with shape (1, 2)
    param bearing: bool. If True, bearing will be returned
    '''
    if not (np.array(a).shape == np.array(b).shape and np.array(a).shape == (2,)):
        raise ValueError(f"a, b has to be sequences with shape (1, 2), a: {a} b: {b}")
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dst = np.sqrt(dx**2 + dy**2)
    ang = np.arctan2(dy, dx)
    return dst, ang


def rl_inverse(key):
    '''
    Inverts value of key between left and right
    '''
    assert key in ('right', 'left'), "must be 'right' or 'left'"
    if key =='right':
        return 'left'
    else:
        return 'right'


def intersect_num(ptarray1, ptarray2):
    """
    ptarray format: [ [x1, x2, x3, x4], [y1, y2, y3, y4] ]

    return: tuple with tuples with coords ( (x1, y1), (x2, y2)... )
    """
    pts1 = np.column_stack(ptarray1)
    pts2 = np.column_stack(ptarray2)
    first_line = LineString(pts1)
    second_line = LineString(pts2)
    intersection = first_line.intersection(second_line)
    if type(intersection) == MultiPoint:
        return [(i.coords.xy[0][0], i.coords.xy[1][0]) for i in intersection.geoms]
    elif type(intersection) == Point:
        return ((intersection.coords.xy[0][0], intersection.coords.xy[1][0]),)
    else:
        return ((),)


def intersectLogspirals(dst0, dst1, ang0, ang1, alpha):
    '''
    dst0, ang0: parameters of RIGHT spiral
    dst1, ang1L parameters of LEFT spiral
    '''
    if ang1-ang0 > np.pi:
        ang1 = rad_magic(ang1)
    elif ang0-ang1 > np.pi:
        ang0 = rad_magic(ang0)
    i_phi = (np.log(dst0/dst1)*np.tan(alpha) + ang1 + ang0) / 2
    i_r1 = dst0*np.exp(-(i_phi-ang0) / np.tan(alpha))
    i_r2 = dst1*np.exp(-(i_phi-ang1) / np.tan(-alpha))
    if i_r1 > dst0 or i_r2 > dst1:
        i_phi -= np.pi
        i_r1 = dst0*np.exp(-(i_phi-ang0) / np.tan(alpha))
        i_r2 = dst1*np.exp(-(i_phi-ang1) / np.tan(-alpha))
        i_r2 = min(i_r1, i_r2)

    return (i_phi, i_r2)


def intersect_curves(curve1, curve2):
    '''
    return: {'curves': (curve1, curve2), 'position_type': ((xp, yp), "right"), 'dst': dst0, 'ang': ang0}

    "right"/"left" flag is tp for curve1
    '''
    assert curve1.root == curve2.root, "Roots have to be the same" 
    assert curve1.leaf != curve2.leaf, "Leaves must not be the same (we assume that a, b, th of curves are equal"
    root = curve1.root

    # unpacking params
    rights = (curve1.params["right"], curve2.params["right"])
    lefts = (curve2.params["left"], curve1.params["left"])
    dst = -float("inf")
    ang = 0
    exit_key = False
    # calculating intersections
    for params_r, params_l, tp in zip(rights, lefts, ["right", "left"]):
        intersection = intersectLogspirals(params_r["dst"], params_l["dst"], params_r["ang"], params_l["ang"], params_r["alpha"])
        if any(intersection) is float("nan"): continue
        # check where is intersection
        if intersection[1] < params_r["r_domain"][0] and intersection[1] > params_r["r_domain"][-1]:
            r_out_key = True
        else:
            r_out_key = False

        if intersection[1] < params_l["r_domain"][0] and intersection[1] > params_l["r_domain"][-1]:
            l_out_key = True
        else:
            l_out_key = False

        if r_out_key and l_out_key:
            exit_key = True
            if intersection[1] > dst:
                ang, dst = intersection
                out_tp = tp
    
    if not exit_key:
        raise Warning("Impossible intersection returned")
        return {'curves': (curve1, curve2), 'position_type': ((0,0), "left"), 'dst': 0, 'ang': 0}
    crds = tuple(rect_logspiral(dst, ang))
    ang = rad_back_magic(ang)
    return {'curves': (curve1, curve2), 'position_type': (crds, out_tp), 'dst': dst, 'ang': ang}


def rad_magic(ang):
    """
    Converting from radian to signed radian
    """
    if ang>np.pi:
        return rad_magic(ang - np.pi*2)
    else:
        return ang


def rad_back_magic(ang):
    """
    Converting from signed radian to radian
    """
    if ang<0:
        return rad_back_magic(ang + np.pi*2)
    else:
        return ang

