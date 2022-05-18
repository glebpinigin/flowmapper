import matplotlib.pyplot as plt


def plot(curve, ax1=None, ax2=None, polar = True, **kwargs):
    # Отрисовка кривой внутри всей области определения
    fig = plt.figure(1,(8,4)) if ax1 is None else None
    if polar:
        ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
    
    xr,yr = curve.crds["right_xy"]
    xl,yl = curve.crds["left_xy"]
    
    rr = curve.params['right']['r']
    phir = curve.params['right']['phi']
    rl = curve.params['left']['r']
    phil = curve.params['left']['phi']

    if polar:
        ax1.plot(phir, rr, "-c")
        ax1.plot(phil, rl, "-m")
    ax2.plot(xr,yr, "-c", **kwargs)
    ax2.plot(xl,yl, "-m", **kwargs)
    ax2.plot(curve.leaf[0], curve.leaf[1], "og")
    ax2.plot(curve.root[0], curve.root[1], "sg")
    ax2.set_aspect(1)


def tplot(curve, ax1=None, ax2=None, polar = True, limdraw=False):
    # Отрисовка кривой внутри обрезанной области определения
    fig = plt.figure(1,(8,4)) if ax1 is None else None
    if polar:
        ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2

    x,y = curve.crds[f"{curve.tp}_xy"]
    
    if curve.tp == 'right':
        sign = -1
        color = 'c'
    else:
        sign =1
        color = 'm'

    if polar:
        ax1.plot(curve.params[curve.tp]["phi"], curve.params[curve.tp]["r"], f"-{color}")
    
    ax2.plot(x,y, f"-{color}")

    if limdraw:
        ax2.plot(curve.lowerlimit_xy[0], curve.lowerlimit_xy[1], "^k")
        ax2.plot(curve.upperlimit_xy[0], curve.upperlimit_xy[1], "vk")

    ax2.plot(curve.leaf[0], curve.leaf[1], "og")
    ax2.plot(curve.root[0], curve.root[1], "sg")
    ax2.set_aspect(1)


def draw(curves, ax1=None, ax2=None, polar=True):
    """Plotting set of curves"""
    fig = plt.figure(1,(8,4)) if ax1 is None else None
    ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
    
    for curve in curves:

        curve.plot(ax1=ax1, ax2=ax2, polar=polar)
    return ax1, ax2


def tdraw(curves, ax1=None, ax2=None, polar=True):
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