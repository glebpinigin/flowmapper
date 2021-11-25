import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import LineString




def euclidian_dst(a, b):
    '''
    Вычисляет евклидово расстояние между двумя точками.
    params a, b: sequence with shape (1, 2)
    '''
    if not (type(a) == type(b) and np.array(a).shape == np.array(b).shape and np.array(a).shape == (2,)):
        raise ValueError("a, b has to be sequences with shape (1, 2)")
    
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)




def rl_inverse(key):
    '''
    Inverts value of key between left and right
    '''
    assert key in ('right', 'left'), "must be 'right' or 'left'"
    if key =='right':
        return 'left'
    else:
        return 'right'




def draw(curves, ax1=None, ax2=None):
        '''
        аналог ShiftedLogCurve.draw(). Не аналогична LimitedSLC.draw()
        Требует массива объектов.

        В текущем виде бесполезна после появления batch_draw

        curves: массив кривых, инициализированных при run=True
        '''
        if ax1 is None and ax2 is None:
            fig = plt.figure(1,(15,15))
            ax1 = fig.add_subplot(221,polar=True) # раскомментировать эту строку и "222" для отображения в полярных координатах
            ax2 = fig.add_subplot(
            222,
            polar=False)
        
        for curve in curves:

            xr,yr = curve.proj_rect()["right_xy"]
            xl,yl = curve.proj_rect()["left_xy"]

            try:
                ax1.plot(curve.th, curve.r, "-c")
                ax1.plot(-curve.th, curve.r, "-m")
            except AttributeError:
                pass
            try:
                ax2.plot(xr,yr, "-c")
                ax2.plot(xl,yl, "-m")
                ax2.plot(curve.leaf[0], curve.leaf[1], "sg")
                ax2.set_aspect(1)
            except AttributeError:
                pass




def intersect(curve1, curve2, plotting=False):
    '''Формат возвращаемого словаря: {'curves': (curve1, curve2), 'position_type': ((xp, yp), "right"), 'dst': dst0}

    флаг положения кривой "right"/"left" возвращается для curve1
    
    Эта функция представляет собой костыль, состоящий из костылей. это всё, что о ней надо знать.
    Она возвращает координату самого удалённого от корня пересечения границ двух спиральных областей.
    Иногда возвращает None. В каких именно случаях, неясно
    '''
    assert curve1.root == curve2.root, "Roots have to be the same" 
    assert curve1.leaf != curve2.leaf, "Leaves must not be the same (we assume that a, b, th of curves are equal"
    # print("first pair")
    first_line = LineString(np.column_stack((curve1.crds["right_xy"][0], curve1.crds["right_xy"][1])))
    second_line = LineString(np.column_stack((curve2.crds["left_xy"][0], curve2.crds["left_xy"][1])))
    intersection = first_line.intersection(second_line)
    # print(intersection.geom_type)
    try:
        inter_crds0 = np.array(LineString(intersection).coords.xy)
        inter_crds0 = inter_crds0[inter_crds0 != curve1.root]
        # print(inter_crds0.shape, "\n", inter_crds0)
        # inter_crds = inter_crds[inter_crds != 0]
    
        dst0 = np.sqrt((inter_crds0[0]-curve1.root[0])**2 + (inter_crds0[1]-curve1.root[1])**2)

        # plt.plot(inter_crds0[0], inter_crds0[1], 'or')
    except AssertionError:
        inter_crds0 = (None,None)
        dst0 = float('inf')

    # print("second pair")
    first_line = LineString(np.column_stack((curve1.crds["left_xy"][0], curve1.crds["left_xy"][1])))
    second_line = LineString(np.column_stack((curve2.crds["right_xy"][0], curve2.crds["right_xy"][1])))
    intersection = first_line.intersection(second_line)
    # print(intersection.geom_type)
    try:
        inter_crds1 = np.array(LineString(intersection).coords.xy)
        inter_crds1 = inter_crds1[inter_crds1 != curve1.root]
        # print(inter_crds1.shape, "\n", inter_crds1)

        dst1 = np.sqrt((inter_crds1[0]-curve1.root[0])**2 + (inter_crds1[1]-curve1.root[1])**2)

        # plt.plot(inter_crds0[0], inter_crds0[1], 'or') 
    except AssertionError:
        inter_crds1 = (None,None)
        dst1 = float('inf')
    
    if (dst0 >= dst1) and dst0 != float('inf'):
        if plotting: plt.plot(inter_crds0[0], inter_crds0[1], 'or')
        return {'curves': (curve1, curve2), 'position_type': (inter_crds0, "right"), 'dst': dst0}
    elif (dst1 >= dst0) and dst1 != float('inf'):
        if plotting: plt.plot(inter_crds1[0], inter_crds1[1], 'or')
        return {'curves': (curve1, curve2), 'position_type': (inter_crds1, "left"), 'dst': dst1}

    if all(inter_crds0) == None:
        if all(inter_crds1.all) == None:
            return None
        else:
            return {'curves': (curve1, curve2), 'position_type': (inter_crds1, "left"), 'dst': dst1}
    else:
        return {'curves': (curve1, curve2), 'position_type': (inter_crds0, "right"), 'dst': dst0}