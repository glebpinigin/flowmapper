import networkx as nx
import numpy as np
from scipy import optimize, interpolate
import matplotlib.pyplot as plt
import numpy as np
from ..distributor import local_utils as lu
from ..distributor.spirals import NodeRegion
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


def ppTr(T: nx.DiGraph, ptnum):
    """Populate tree with points using scipy.optimize.minimize"""
    for node1, node2, data in T.edges.data():
        if data["type"] == "root-connection":
            node1_crds = np.array(node1)
            leaf = np.array(node2)
            crds = (node1_crds, leaf)
            line = LineString(crds)
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")
        elif data["type"] == "st-connection":
            R = T.nodes[node2]["R"]
            tp = R.tp
            # get points in polar coordinates
            sign = lu.lrsign(tp)
            ang = R.ang
            dst = R.dst
            alpha = R.params[tp]["alpha"]
            phimn, phimx = R.params[tp]["phi_domain"]
            phi = np.linspace(phimx, phimn, ptnum)
            phi = np.append(phi, (sign, alpha, dst, ang))
            bounds = computeBounds(phi)
            # optimizing
            res = optimize.minimize(dstSd, phi, bounds=bounds)
            phi2 = res.x[:-4]
            r2 = lu.calcR(phi2, R.params, tp)
            # transfer to rectangular
            crds = lu.rect_logspiral(r2, phi2)
            crds = np.column_stack(crds)
            crds = crds + T.bias
            line = LineString(crds)
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")
        elif data["type"] == "false-connection":
            R = T.nodes[node2]["R"]
            crds = R.crds
            crds = np.column_stack(crds)
            crds = crds + T.bias
            line = LineString(crds)
            wkt = line.wkt
            nx.set_edge_attributes(T, {(node1, node2): wkt}, name="Wkt")

