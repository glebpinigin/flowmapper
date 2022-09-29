import networkx as nx
from flow_mapper.core.distributor import local_utils as lu
import numpy as np

# шкалирование
def linScale(x, frommin, frommax, tomin, tomax):
    return (tomax-tomin)*(x-frommin)/(frommax-frommin) + tomin

# расчёт ширин в таблицу атрибутов
def thckTr(T, vol_flds, *scale_args):
    edge_data_new = {}
    for node1, node2, data in T.edges.data():
        print(data)
        values = list(map(lambda x: linScale(data[x], *scale_args), vol_flds))
        data_new = {}
        data_new = {name + "_width": value for name, value in zip(vol_flds, values)}
        edge_data_new[(node1, node2)] = data_new
    nx.set_edge_attributes(T, edge_data_new)
        
# раздвижение узлов (универсальное)
def moveLastNode(pt, backpt, tp, width):
    sign = lu.lrsign(tp)
    _, back_bearing = lu.dst_bearing(pt, backpt)
    move_bearing = back_bearing + sign*np.pi/2
    dx, dy = lu.rect_logspiral(width/2, move_bearing)
    ptnx = pt[0] + dx
    ptny = pt[1] + dy
    return ptnx, ptny