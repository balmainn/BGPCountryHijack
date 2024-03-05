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


#depricated, moved here from v3 

def setupGraph2():
    print("SETTING UP GRAPH!")
    asGraph = networkx.Graph()
    asGraph.add_node(originASOfP,origin='origin',linkLevel=0) 
    print(f"originAS of p x{originASOfP}x")
    lv1Neighbors = getNeighbor(originASOfP,queryTime)

    # print('lv1 neighbors: ',lv1Neighbors[0]['asn'])


    #graph setup stuff        
    for neighbor in lv1Neighbors:
        lv1neighborData = asGraph.nodes.get(neighbor)
        if lv1neighborData == None:
            asGraph.add_node(neighbor,lv1Neighbor='lv1Neighbor',linkLevel=1)
            asGraph.add_edge(neighbor,originASOfP)
            
        else:
            lv1neighborData['lv1Neighbor'] = 'lv1Neighbor'
            asGraph.add_edge(originASOfP,neighbor)
        
        lv2Neighbors = getNeighbor(neighbor,queryTime)
        # lv2Neighbors[neighbor] = nextNeighbors
        count = 0
        #check if lv2neighbors is none, if it is contiue
        if lv2Neighbors == None:
            #continue on bad
            continue
        
            
        for lv2Neighbor in lv2Neighbors:
            print(f"{count} / {len(lv2Neighbors)} lv2 neighbors")
            lv2neighborData = asGraph.nodes.get(lv2Neighbor)
            if lv2neighborData == None:
                asGraph.add_node(lv2Neighbor,lv2Neighbor='lv2Neighbor',linkLevel=2)
                asGraph.add_edge(lv2Neighbor,neighbor)
            else:
                # print("data exists in graph")
                
                lv2neighborData['lv2Neighbor'] = 'lv2Neighbor'
                asGraph.add_edge(lv2Neighbor,neighbor)
            lv3Neighbors = getNeighbor(lv2Neighbor,queryTime)
            count2 = 0
            if lv3Neighbors == None:
                #continue on bad
                continue
            for lv3neighbor in lv3Neighbors:
                # print(f"{count2} / {len(lv3Neighbors)} lv3 neighbors")
                #see if data exists, 
                lv3neighborData = asGraph.nodes.get(lv3neighbor)
                if lv3neighborData == None:
                    asGraph.add_node(lv3neighbor,lv3Neighbor='lv3Neighbor',linkLevel=3)
                    asGraph.add_edge(lv3neighbor,lv2Neighbor)
                else:
                    # print("data exists in graph")
                    # print(lv3neighborData)
                    lv3neighborData['lv3Neighbor'] = 'lv3Neighbor'
                    asGraph.add_edge(lv3neighbor,lv2Neighbor)
                count2+=1

            print("lv3 neighbors done!")

            count +=1
        print("lv2 neighbor done")
        # if count < 2:
    pickle.dump(asGraph,open("pickles/asGraph.pickle",'wb'))
    print("DONE!")
 + 50 + 0 
        # weightSum = 150
        # average =  (100*fullyHijackableCounter + 50*partiallyHijackableCounter)/150
    return asGraph
        # count+=1