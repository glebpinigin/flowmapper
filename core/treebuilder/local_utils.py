import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import LineString, Point, MultiPoint
import warnings

def polar_logspiral(a, b, th):
    '''
    ОПРЕДЕЛЕНИЕ ЗНАЧЕНИЙ РАДИУСА ДЛЯ ОБЛАСТИ ОПРЕДЕЛЕНИЙ (углов)
    Экспонента сдвинута на -1.
    Таким образом область значений сдвигается на -self.a относительно лог. спирали по определению
    Это необходио, чтобы область значений начиналась от 0
    th: np.array область определения (массив углов для котрых требуется рассчитать радиус)
    '''
    return a*(np.exp(b*th)-1)


def rect_logspiral(r, th, ang, tp):
    '''
    bestway to call: crds[f'{tp}_xy'] = rect_logspiral(r, th, ang, tp)
    ПЕРЕВОД В ПРЯМОУГОЛЬНЫЕ КООРДИНАТЫ
    Функция переводит кривую в полярных координатах (массив R(th) для массива th) в прямоугольные (массив x и массив y)
    Результат: редактирование атрибута self.crds

    input: обязательных аргументов нет
    R: массив R(th). Если None, то используется self.R

    return: self.crds (на всякий случай)
    '''
    sign = 1 if tp == 'right' else -1
    thc = sign*th + ang + np.pi
    x = r*np.cos(thc)
    y = r*np.sin(thc)
    return [x, y]


def eval_a_logspiral(dst, b):
    '''
    РАСЧЁТ self.a
    Рассчитывает параметр a, который нужно использовать, чтобы "вписать" кривую с заданным b
    между корнем и листом
    Экспонента сдвинута на -1
    
    Входных параметров и return не предусмотрено
    '''
    return dst/(np.exp(b*np.pi)-1)


def dst_bearing(a, b, bearing=False):
    '''
    Calculates distance and bearing between points.
    params a, b: sequences with shape (1, 2)
    param bearing: bool. If True, bearing will be returned
    '''
    if not (np.array(a).shape == np.array(b).shape and np.array(a).shape == (2,)):
        raise ValueError("a, b has to be sequences with shape (1, 2)")
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




def draw(curves, ax1=None, ax2=None, polar=True):
    """Plotting set of curves"""
    fig = plt.figure(1,(15,15)) if ax1 is None else None
    ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
    
    for curve in curves:

        curve.plot(ax1=ax1, ax2=ax2, polar=polar)


def tdraw(curves, ax1=None, ax2=None, polar=True):
    """Plotting set of curves"""
    fig = plt.figure(1,(15,15)) if ax1 is None else None
    ax1 = fig.add_subplot(221,polar=True) if ax1 is None else ax1
    ax2 = fig.add_subplot(222,polar=False) if ax2 is None else ax2
    
    for curve in curves:

        curve.tplot(ax1=ax1, ax2=ax2, polar=polar)


def intersect(ptarray1, ptarray2):
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
        return (intersection.coords.xy[0][0], intersection.coords.xy[1][0])
    else:
        return ((),)


def intersect_curves(curve1, curve2, plotting=False, ax=None):
    '''Формат возвращаемого словаря: {'curves': (curve1, curve2), 'position_type': ((xp, yp), "right"), 'dst': dst0}

    флаг положения кривой "right"/"left" возвращается для curve1
    
    Эта функция представляет собой костыль, состоящий из костылей. это всё, что о ней надо знать.
    Она возвращает координату самого удалённого от корня пересечения границ двух спиральных областей.
    Иногда возвращает None. В каких именно случаях, неясно
    '''
    assert curve1.root == curve2.root, "Roots have to be the same" 
    assert curve1.leaf != curve2.leaf, "Leaves must not be the same (we assume that a, b, th of curves are equal"
    root = curve1.root
    # print("first pair")
    intersection = intersect(curve1.crds["right_xy"], curve2.crds["left_xy"])
    if len(intersection) == 2:
        inter_crds0 = intersection[intersection != curve1.root]
        dst0, ang0 = dst_bearing(root, inter_crds0, True)
    else:
        inter_crds0 = np.array((None,None))
        dst0 = float('inf')


    # print("second pair")
    intersection = intersect(curve1.crds["left_xy"], curve2.crds["right_xy"])

    if len(intersection) == 2:
        inter_crds1 = intersection[intersection != curve1.root]
        dst1, ang1 = dst_bearing(root, inter_crds1, True)
    else:
        inter_crds1 = np.array((None,None))
        dst1 = float('inf')
    
    if (dst0 >= dst1) and dst0 != float('inf'):
        try:
            if plotting: ax.plot(inter_crds0[0], inter_crds0[1], 'or')
        except AttributeError:
            plt.plot(inter_crds0[0], inter_crds0[1], 'or')
        return {'curves': (curve1, curve2), 'position_type': (inter_crds0, "right"), 'dst': dst0, 'ang': ang0}
    elif (dst1 >= dst0) and dst1 != float('inf'):
        try:
            if plotting: ax.plot(inter_crds1[0], inter_crds1[1], 'or')
        except AttributeError:
            plt.plot(inter_crds1[0], inter_crds1[1], 'or')
        return {'curves': (curve1, curve2), 'position_type': (inter_crds1, "left"), 'dst': dst1, 'ang': ang1}

    if inter_crds0.any() == None:
        if inter_crds1.any() == None:
            warnings.warn(f"None interscetion returned for curves with leaves {curve1.leaf}, {curve2.leaf}")
            return {'curves': (curve1, curve2), 'position_type': ((0,0), "left"), 'dst': 0, 'ang': 0}
        else:
            return {'curves': (curve1, curve2), 'position_type': (inter_crds1, "left"), 'dst': dst1, 'ang': ang1}
    else:
        return {'curves': (curve1, curve2), 'position_type': (inter_crds0, "right"), 'dst': dst0, 'ang': ang0}


def rad_magic(ang):
    """
    Converting from radian to signed radian
    """
    if ang>np.pi:
        return -(ang - np.pi)
    else:
        return ang

def rad_back_magic(ang):
    """
    Converting from signed radian to radian
    """
    if ang<0:
        return ang + np.pi*2
    else:
        return ang

