import requests 
import pickle 
import os 

#for a prefix p i need to ask, what happens to this prefix when an as happens to go rogue that is an n2 neighbor?
#if the as is the origin as, hijackability score is 100 (owners can do what they want)
#if its a direct neighbor, how would this AS going rogue affect its neighbors, etc. 
#optional query RPKI to see if its used

#based on testing we can assume that the n1 neighbors 
#will be the the the second to last hop in a given path 
#(with duplicates removed)


# url ='https://stat.ripe.net/data/bgp-state/data.json?resource=61160'
# resp = requests.get(url)
# json = resp.json()
# routes = json["data"]["bgp_state"]
# for route in routes:
#     path = route['path']
#     # print(type(path),type(path[0]))
#     if 61160 not in path or 174 not in path:
#         print("something not in path",path)


originCountryCode = "VA"
import networkx
asns = ['8978', '61160', '202865']
prefixGraph = networkx.Graph()

prefixGraph.add_node(0,code=originCountryCode)
for i in range(len(asns)):
    asn = int(asns[i])
    prefixGraph.add_node(asn,asn=asn)
    prefixGraph.add_edge(0,asn)

import matplotlib.pyplot as plt
import networkx as nx
nodes = prefixGraph.nodes
print(nodes.data())

prefixGraph.add_node('a')
prefixGraph.add_node('b')
# prefixGraph.add_edge(1,1)
# prefixGraph.add_edge(1,1)
print(prefixGraph.nodes)
def drawGraph(graph):
    prefixGraph = graph

    networkx.draw(prefixGraph, with_labels=True, font_weight='bold')

#networkx.draw_shell(prefixGraph, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
#networkx.draw_shell(prefixGraph, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
    plt.show()

drawGraph(prefixGraph)