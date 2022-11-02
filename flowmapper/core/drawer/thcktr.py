import networkx as nx
from flowmapper.core.distributor import local_utils as lu
import numpy as np
import warnings

# шкалирование
def linScale(x, frommin, frommax, tomin, tomax, soft = True):
    if x == 0 and soft:
        return 0
    return (tomax-tomin)*(x-frommin)/(frommax-frommin) + tomin

# расчёт ширин в таблицу атрибутов
def thckTr(T, vol_flds, *scale_args, inplace=True):
    edge_data_new = {}
    for node1, node2, data in T.edges.data():
        values = list(map(lambda x: linScale(data[x], *scale_args), vol_flds))
        data_new = {}
        data_new = {name: value for name, value in zip(vol_flds, values)}
        edge_data_new[(node1, node2)] = data_new
    if inplace:
        T.setSymbolProperty("linewidth", edge_data_new, vol_flds)
        return None
    return edge_data_new


# раздвижение узлов (универсальное)
def nodeOffset(pt, backpt, tp, width_pt, width_back):
    sign = lu.lrsign(tp)
    _, back_bearing = lu.dst_bearing(pt, backpt)
    move_bearing = back_bearing + sign*np.pi/2
    dx, dy = lu.rect_logspiral(width_back/2-width_pt/2, move_bearing)
    ptnx = pt[0] + dx
    ptny = pt[1] + dy
    return ptnx, ptny