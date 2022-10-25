import matplotlib.pyplot as plt
import numpy as np
from shapely import wkt


def plot(crds, leaf=None, root=None, ax1=None, ax2=None, polar = True, **kwargs):
    # Отрисовка кривой внутри всей области определения
    fig = plt.figure(1,(8,4)) if ax1 is None and ax2 is None else None
    if polar:
        ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
    
    xr,yr = crds["right_xy"]
    xl,yl = crds["left_xy"]
    
    rr = crds['right']['r']
    phir = crds['right']['phi']
    rl = crds['left']['r']
    phil = crds['left']['phi']

    if polar:
        ax1.plot(phir, rr, "-c")
        ax1.plot(phil, rl, "-m")
    ax2.plot(xr,yr, "-c", **kwargs)
    ax2.plot(xl,yl, "-m", **kwargs)
    if leaf is not None:
        ax2.plot(*leaf, "og")
    if root is None:
        ax2.plot(*root, "sg")
    ax2.set_aspect(1)
    return ax1, ax2


def tplot(crds, leaf=None, root=None, tp=None, ax1=None, ax2=None, polar = True, limdraw=False):
    # Отрисовка кривой внутри обрезанной области определения
    fig = plt.figure(1,(8,4)) if ax1 is None and ax2 is None else None
    if polar:
        ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2

    x,y = crds["xy"]
    
    if tp == 'right':
        color = 'c'
    else:
        color = 'm'

    if polar:
        ax1.plot(crds["phi"], crds["r"], f"-{color}")
    
    ax2.plot(x,y, f"-{color}")

    if leaf is not None:
        ax2.plot(*leaf, "og")
    if root is None:
        ax2.plot(*root, "sg")
    ax2.set_aspect(1)
    return ax1, ax2


def drawTree(T, ax=None, geom_field="raw_geom", display_nodes=True, nodes_fmt='go', nodes_kwargs=None):
    if ax is None:
        fig = plt.figure(1, (8, 5))
        ax = fig.add_subplot()
    for node1, node2, geom in T.edges.data(geom_field):
        ax.plot(*np.array(list(geom.coords)).T)
    if display_nodes:
        for node1, node2, geom in T.edges.data(geom_field):
            nodes_kwargs = {} if nodes_kwargs is None else nodes_kwargs
            ax.plot(*node2, nodes_fmt, **nodes_kwargs)
    ax.set_aspect(1)
    return ax


def drawCurves(curves, ax1=None, ax2=None, polar=True):
    """Plotting set of curves"""
    fig = plt.figure(1,(8,4)) if ax1 is None else None
    ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
    
    for curve in curves:
        curve.plot(ax1=ax1, ax2=ax2, polar=polar)
    return ax1, ax2


def tdrawCurves(curves, ax1=None, ax2=None, polar=True):
    """Plotting set of curves"""
    fig = plt.figure(1,(8,4)) if ax1 is None else None
    ax1 = fig.add_subplot(121,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(122,polar=False) if ax2 is None else ax2
    ax2.set_aspect(1)
    for curve in curves:
        try:
            curve.tplot(ax1=ax1, ax2=ax2, polar=polar)
        except AttributeError:
            curve.plot(ax1=ax1, ax2=ax2, polar=polar)
    return ax1, ax2