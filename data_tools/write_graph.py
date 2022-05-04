import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from cal_distance import *

# points=pd.read_csv('./input/nodes_inform.csv')
points=pd.read_excel('./input/nodes_inform.xlsx')

G=nx.Graph()
pos=dict()
for i in range(len(points)):
    x,y=points.iloc[i]['Lon_Lat'].split(',', 2 )
    loc=(float(x[1:]),float(y[:-1]))
    # print(loc,type(loc))
    G.add_node(points.iloc[i]['index'], Lon_Lat=loc, name=points.iloc[i]['name'], node_type=points.iloc[i]['node_type'],standpoint=int(points.iloc[i]['standpoint']),warning_dis=float(points.iloc[i]['warning_dis']))
    pos[i]=loc

# 暂时用全连接直线距离描述距离
node_list=list(G.nodes.data())
# print(node_list,type(node_list))
for i in range(len(node_list)):
    for j in range(i+1,len(node_list)):
        # print(node_list[i][1]['Lon_Lat'])
        G.add_edge(i,j,length=cal_distance(node_list[i][1]['Lon_Lat'],node_list[j][1]['Lon_Lat']))

nx.write_gpickle(G, "./input/Dongsha_withstandpoint.gpickle")

# 可视化显示G的实际结构
# plt.rcParams['figure.figsize']= (50, 25)
# nx.draw_networkx_nodes(G, pos)
# node_labels = nx.get_node_attributes(G, 'name')
# nx.draw_networkx_labels(G, pos, labels=node_labels)
# nx.draw_networkx_edges(G,pos,edge_color='grey')
# plt.show()