import networkx as nx
import numpy as np
from scipy import optimize, interpolate
import matplotlib.pyplot as plt
import numpy as np
from flowmapper.core.distributor import local_utils as lu
from shapely.geometry import LineString


def integral(phi, r, alpha, phi0, tp):
    sign = lu.lrsign(tp)
    return np.tan(alpha) * ( -sign*np.sqrt(r**2 * (1/np.sin(alpha)**2) * np.exp((-sign*2/np.tan(alpha))*(phi-phi0)) ) )


def arcLength(params, lbp, ubp, tp):
    return integral(lbp, params[tp]["dst"], params[tp]["alpha"], params[tp]["ang"], tp) - integral(ubp, params[tp]["dst"], params[tp]["alpha"], params[tp]["ang"], tp)


def dstSd(arr):
    sign, alpha, dst, ang = arr[-4:]
    tp = lu.signlr(sign)
    params = {tp: {"dst": dst, "alpha": alpha, "ang": ang}}
    ubp = arr[:-4]
    lbp = np.roll(ubp, -1)[:-1]
    ubp = ubp[:-1]
    return arcLength(params, lbp, ubp, tp).std()


def computeBounds(pts):
    lb = np.full(pts.shape, fill_value=float("-inf"))
    lb[:1] = pts[:1]
    lb[-5:] = pts[-5:]
    ub = np.full(pts.shape, fill_value=float("inf"))
    ub[:1] = pts[:1]
    ub[-5:] = pts[-5:]
    bounds = np.column_stack((lb, ub))
    return bounds


def ppTr(T: nx.DiGraph, ptnum=4, method="unif"):
    """Populate tree with points using scipy.optimize.minimize"""
    assert method in ("unif", "log"), "Only 'unif' and 'log' methods available"
    for node1, node2, data in T.edges.data():
        if data["type"] == "root-connection":
            node1_crds = np.array(node1)
            leaf = np.array(node2)
            crds = (node1_crds, leaf)
            line = LineString(crds)
            nx.set_edge_attributes(T, {(node1, node2): line}, name="raw_geom")
        elif data["type"] in ("st-connection-right", "st-connection-left"):
            R = T.nodes[node2]["R"]
            tp = R.tp
            # get points in polar coordinates
            sign = lu.lrsign(tp)
            ang = R.ang
            dst = R.dst
            alpha = R.params[tp]["alpha"]
            phimn, phimx = R.params[tp]["phi_domain"]
            phi = np.linspace(phimx, phimn, ptnum)
            if method == "unif":
                phi = np.append(phi, (sign, alpha, dst, ang))
                bounds = computeBounds(phi)
                # optimizing
                res = optimize.minimize(dstSd, phi, bounds=bounds)
                phi2 = res.x[:-4]
            elif method == "log":
                phi2 = phi
            r2 = lu.calcR(phi2, R.params, tp)
            # transfer to rectangular
            crds = lu.rect_logspiral(r2, phi2)
            crds = np.column_stack(crds)
            crds = crds + T.bias
            line = LineString(crds)
            nx.set_edge_attributes(T, {(node1, node2): line}, name="raw_geom")
        elif data["type"] in ("false-connection-right", "false-connection-left"):
            R = T.nodes[node2]["R"]
            crds = R.crds
            crds = np.column_stack(crds)
            crds = crds + T.bias
            line = LineString(crds)
            nx.set_edge_attributes(T, {(node1, node2): line}, name="raw_geom")


def ptsToSpline(pts, ptnum=20, kind="cubic"):
    """
    Return spline interpolated array of points
    pts: [x, y]
    """
    if len(pts) == 2:
        return pts
    
    # Linear length along the line:
    distance = np.cumsum( np.sqrt(np.sum( np.diff(pts, axis=0)**2, axis=1 )) )
    distance = np.insert(distance, 0, 0)/distance[-1]

    alpha = np.linspace(0, 1, ptnum)
    interpolator =  interpolate.interp1d(distance, pts, kind=kind, axis=0)
    return interpolator(alpha)


def smoothTr(T: nx.DiGraph, ptnum=21, kind="cubic", inplace = True, geom_field="raw_geom"):
    gs = list(map(lambda x: LineString(ptsToSpline(
                    np.array(x[2][geom_field].coords), ptnum, kind)),
                    T.edges.data()))
    vals = dict(zip(T.edges, gs))
    if inplace:
        nx.set_edge_attributes(T, vals, name="spline_geom")
        return None
    return vals