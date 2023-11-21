import numpy as np
import pandas as pd
import networkx as nx
import igraph as ig
import geopandas as gpd

# angle compute
def anguler(line1,line2):
    """ line1可以是(node1,node2),line2是(node2,node3) """
    node1, node2 = line1
    node3 = line2[1]
    d12 = linedis(node1,node2)
    d23 = linedis(node2,node3)
    d13 = linedis(node1,node3)
    #浮点运算会算出-1.000000000000002，所以控制小数位
    cosangular = round( (d13**2 - d23**2 - d12**2) / (-2 * d12 * d23) ,6)
    angular = np.arccos(cosangular) #弧度制 (0,3.14)
    buangular = np.pi-angular
    std = 2 * buangular / np.pi
    #如果std小于0.15倍的90度，大约为16.7度，默认两条道路没有转角
    if std < 0.15:
        return 0.000
    else:
        return std


# distance compute
def linedis(node1,node2):
    dis = np.sqrt( ( (node1[0]-node2[0])**2 + (node1[1]-node2[1])**2 ) )
    return dis


# dual model
def dual_model(lines):
    # primary model
    G = nx.Graph()
    G.graph['crs'] = lines.crs # 坐标系属性
    for row in lines.itertuples():
        start_node = (row.geometry.coords[0][0], row.geometry.coords[0][1])
        end_node = (row.geometry.coords[-1][0], row.geometry.coords[-1][1])
        length = ((end_node[0]-start_node[0])**2 +(end_node[1]-start_node[1])**2)**0.5
        G.add_edge(start_node, end_node, weight=length, id=row[0])

    # dual model
    g = ig.Graph.from_networkx(G)
    
    edges, weight_length, weight_angle, node_attrs = [], [], [], []
    for i in range(g.ecount()):
        # 邻居探查
        v1, v2 = g.es[i].source, g.es[i].target
        v1neib, v2neib = g.neighborhood(v1, order=1), g.neighborhood(v2, order=1) # 线段端点的一步邻居端点
        v1neib_edgeid = [g.get_eid(v1,n) for n in v1neib if (n != v1 and n != v2)]
        v2neib_edgeid = [g.get_eid(v2,n) for n in v2neib if (n != v1 and n != v2)]
        neib_edgeid = v1neib_edgeid + v2neib_edgeid # 线段的邻接线段id
        link =[[i,j] for j in neib_edgeid] # 线段i 与邻接线段的组合

        # 距离权重
        lengthi_half = linedis( g.vs[v2]['_nx_name'], g.vs[v1]['_nx_name'])/2
        # g.es[i]['weight']/2
        length = [(lengthi_half + g.es[v1_eid]['weight']/2) for v1_eid in v1neib_edgeid] + \
                        [(lengthi_half + g.es[v2_eid]['weight']/2) for v2_eid in v2neib_edgeid]

        # 角度权重
        angle =[anguler((g.vs[v2]['_nx_name'], g.vs[v1]['_nx_name']),(g.vs[v1]['_nx_name'], g.vs[n]['_nx_name']) ) for n in v1neib if (n !=v1 and n!= v2)] + \
                        [anguler((g.vs[v1]['_nx_name'], g.vs[v2]['_nx_name']),(g.vs[v2]['_nx_name'], g.vs[n]['_nx_name']) ) for n in v2neib if (n !=v1 and n!= v2)] 
        
        #线段i 的坐标
        idattr = ((g.vs[v1]['_nx_name'][0]+g.vs[v2]['_nx_name'][0])/2, (g.vs[v1]['_nx_name'][1]+g.vs[v2]['_nx_name'][1])/2)
        
        edges.extend(link)
        weight_length.extend(length)
        weight_angle.extend(angle)
        node_attrs.append(idattr)

    # 赋予边节点
    weight_angle = [ i+0.0000000001 for i in weight_angle]
    g_re = ig.Graph(n=g.ecount(), edges=edges,
                    edge_attrs={'weight':weight_angle, 'length':weight_length},
                    vertex_attrs={'name': node_attrs})
    g_re.simplify(multiple=True, combine_edges="random")
    
    return g,g_re


# radius-limited betweenness
def bet_radius(g_re, r=np.inf):
    bet = []
    for index in range(g_re.vcount()):
        dis = np.array(g_re.distances(source=index, weights='length'))[0]
        indice = np.where( dis < r )[0]
        # 子图
        subgraph = g_re.subgraph(indice)
        start_node = subgraph.vs['name'].index(g_re.vs[index]['name'])
        # 计算bet
        bet_indice = subgraph.betweenness(vertices=start_node, weights ='weight')
        # 列表化
        bet.append(bet_indice)
    return bet

# radius-limited integration
def int_radius(g_re, r=np.inf):
    int= []
    for i in range(g_re.vcount()): 
        dis = np.array(g_re.distances(source=i, weights='length'))[0]
        indice = np.where( dis < r )[0]

        N = len(indice)
        disangular = np.array(g_re.distances(source=i, target=indice, weights='weight') ) 
        disangular[np.isnan(disangular ) | np.isinf(disangular )] =0
        disangular = np.where(disangular < 0.15, 0, disangular)
        Tdepth = np.sum(disangular)
        # 计算int
        integration = N**2/ ( np.inf if Tdepth==0 else Tdepth)
        # 列表化
        int.append(integration)
    return int

