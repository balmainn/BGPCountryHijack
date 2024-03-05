import networkx
import os
import pickle 
import matplotlib.pyplot as plt

asGraph=pickle.load(open("pickles/asGraph-3582.pickle",'rb'))

def drawGraph2(graph:networkx.Graph):
    networkx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()
def drawGraph(graph:networkx.Graph,colors):
    networkx.draw(graph, node_color=colors, with_labels=True, font_weight='bold')
    # plt.title("Sample Hijacking Graph")
    # plt.legend()
    plt.show()



def getLevels(asGraph):
    lv1 = []
    lv2 =[]
    lv3 = []
    for node in asGraph.nodes:
        nodeData = asGraph.nodes.get(node)
        if nodeData['linkLevel'] ==1:
            lv1.append(node)
        if nodeData['linkLevel'] ==2:
            lv2.append(node)
        if nodeData['linkLevel'] ==3:
            lv3.append(node)
    return lv1, lv2, lv3


def countLevels(asGraph):
    lv1 = 0
    lv2 =0
    lv3 = 0
    for node in asGraph.nodes:
        nodeData = asGraph.nodes.get(node)
        if nodeData['linkLevel'] ==1:
            lv1+=1    
        if nodeData['linkLevel'] ==2:
            lv2+=1
        if nodeData['linkLevel'] ==3:
            lv3+=1
    return lv1, lv2, lv3


# drawGraph(asGraph)
a, b, c = countLevels(asGraph)
print(a,b,c)
dg = networkx.Graph()
count = 0
maxLv3 =2
colors = []
asGraph.remove_node(3582)

lv1, lv2, lv3 = getLevels(asGraph)

# for e in edges:
#     print(e[0])
# # asGraph.edges()
# exit(0)

        
            
            
# edges = list(networkx.edges(asGraph,asGraph.nodes))
removed = []
print(lv1)
print("~~~~~~~~~")
print(lv2)
g = networkx.Graph()
e = asGraph.edges.get((4600,1798))
e = asGraph.edges((4600))
print(e)
# remove = [node for node, degree in asGraph.degree() if degree > 2]
# asGraph.remove_nodes_from(remove)
remove = []
# for node, degree in asGraph.degree():
#     data = asGraph.nodes.get(node)
#     print(node,data,degree)
#     if data['linkLevel']>=3:
#         remove.append(node)



# for two in lv2:
        
for three in lv3:
        count = 0
        try:
            edges = list(asGraph.edges((three)))
            for e in edges:
                count+=1
                if count >=3:                        
                    try:
                        print("removing",e[1])
                        remove.append(e[1])
                        # colors.remove('red')
                    except:
                        pass
                    
        except:
            pass
print('removed: ',len(remove))
asGraph.remove_nodes_from(remove)
colors = []
for node in list(asGraph.nodes):
    data = asGraph.nodes.get(node)
    
    if data['linkLevel']==0:
        print('is 3582')
        print(data)
        colors.append('blue')
        continue
    if data['linkLevel']==2:
        colors.append('purple')
        continue
    if data['linkLevel']==1:
        colors.append('green')
        continue
    if data['linkLevel']>=3:
        colors.append('red')
        continue
            
            # print(e)
# print("~~~~~~~~~")
# print(lv3)
# for e in lv3:
#     edges = networkx.edges(asGraph,node)
#     print(edges)
#     print("~~~~~~~~~")
    # try:
        
    # except:
    #     continue
    # print(edges)
    # count=0
    # for e in edges:
    # count +=1
    # if count <= 3:
    #     pass
        
    # else:
    #     # if e[1] not in removed:
    #     try:
    #         asGraph.remove_node(e[0])
    #     except:
    #         pass
            # removed.append(e[1])
            # print(node,e)
            # colors.remove('red')
    # for three in lv3:
    #     edge = asGraph.edges.get(two,three)
    #     print(edge)
        # edges = networkx.edges(asGraph,node)
        # count = 0
        # removed = []
        # for e in edges:
        #     count +=1
            
        #     if count <= 3:
        #         pass
                
        #     else:
        #         if node not in removed:
        #             asGraph.remove_node(node)
        #             removed.append(node)
        #             print(node,e)
        #             colors.remove('red')
                
print(len(asGraph.nodes))
    #     continue
    # dg.add_node(node)

    # edges = networkx.edges(asGraph, [node])
    # for e in edges:
    #     dg.add_edge(e[0],e[1])

# for i in range(3):
    # drawGraph(asGraph,colors)
drawGraph(asGraph,colors)
# drawGraph2(asGraph)
# file = "hijackingScores-198949.csv"
        
# va = pickle.load(open('pickles/countries/VA-info.pickle','rb'))

# print(va)

