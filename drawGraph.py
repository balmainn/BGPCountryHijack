print("hello world!")
import networkx
import matplotlib.pyplot as plt
# def drawGraph(graph:networkx.Graph):

# Set background color
# fig, ax = plt.subplots(nrows=1, ncols=1)


# # ax.figure.figs?(figsize=(12, 8))

# ax.axis('off')
# ax.set_facecolor('blue')
# ax.gca().set_facecolor('blue')




# layout type
import pickle

import os 
def drawGraph(graph:networkx.Graph,asn):
    print("drawing graph!")
    fig, ax = plt.subplots(figsize=(8, 6))
    

    ax.axis('off')

    fig.set_facecolor('#ADD8E6')  # Light blue
    picklefile = f'pickles/graphs/{asn}-pos-test.pickle'
    if os.path.exists(picklefile):
        print("path exists, loading...")
        pos = pickle.load(open(picklefile,'rb'))
        print("loading done!")
    # Separate edges based on whether they are connected to the origin AS
    else:
        print("starting spring layout")
        # pos = networkx.spring_layout(graph)
        # pos = networkx.planar_layout(graph)
        pos=networkx.draw(graph)
        print("layout done!")
        pickle.dump(pos,open(picklefile,'wb'))
        print("dump done!")
    
    # Separate edges based on whether they are connected to the origin AS
    
    # origin_edges = [(u, v) for u, v in graph.edges if graph.nodes[u].get('linkLevel') == 0 or graph.nodes[v].get('linkLevel') == 0]

    # other_edges = [(u, v) for u, v in graph.edges if u not in origin_edges and v not in origin_edges]



    #edges with higher transparency (grey ones)

    # networkx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.2, edge_color='#B6B2B5') #light grey

    #edges connected to the origin AS without transparency (yellows)

    # networkx.draw_networkx_edges(graph, pos, edgelist=origin_edges, alpha=1, edge_color='#FCFC05') #yellow



    # Level 1 and 2 Neighbors

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#8A8A8A', node_size=500, alpha=0.9) #darker grey

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#B6B2B5', node_size=600, alpha=0.9) #light grey

    

    # Level 3 Neighbors with light grey outline

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#FFFFFF', node_size=300, alpha=0.5, edgecolors='#B6B2B5', linewidths=1)



    # Origin AS node last to ensure it's on top

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='#FCFC05', node_size=1500)



    # label

    origin_as_label = {n: n for n, attr in graph.nodes(data=True) if attr.get('origin') == 'origin'}

    # networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='#000000') #black


    plt.savefig(f"graphs/as-{asn}-graph3.png")
    plt.show()


#asn = 174
# asn = 198949
# asn = 264645
asn = 3582
graph = pickle.load(open(f'pickles/asGraph-{asn}.pickle','rb'))
# networkx.reverse(graph,copy=False)
# pos = networkx.multipartite_layout(graph, subset_key="link_level")

# networkx.draw(graph, pos, with_labels=True)
# exit(0)
# graph = networkx.relabel_nodes(graph2,mapping={asn:str(asn)})
print('graph loaded')
# drawGraph(graph,asn)
origin_as_label = {asn:asn}
# pos = networkx.shell_layout(graph)
fig, ax = plt.subplots(figsize=(8, 6))
    

ax.axis('off')


# graph = networkx.Graph()
colors = []
sizes = []
for node in graph.nodes:
    
    data = graph.nodes.get(node)
    
    if data['linkLevel'] == 1: 
        colors.append('#8A8A8A') #darker grey
        data['node_color'] = '#8A8A8A'
        sizes.append(225)
    if data['linkLevel'] == 2: 
        colors.append('#B6B2B5') #grey
        data['node_color'] = '#B6B2B5'
        sizes.append(150)
    if data['linkLevel'] == 3: 
        data['node_color'] = '#f1f1f1'
        colors.append('#f1f1f1') #very light grey
        sizes.append(2.5)
    if data['linkLevel'] == 0: 
        data['node_color'] = '#0000ff'
        colors.append('#0000ff') #default color #1f78b4
        print("appending orign")
        sizes.append(300)

    try:
        print(data['origin'])
        # data['pos']=(0,0)
        # data['node_color'] = '#0000ff'
        print(data)
        print(node)
        # sizes.append(300)
    except:
        pass
print("colors done")
# graph = networkx.Graph()
# graph.nodes.get(node)['node_color']
# print(lambda node: for graph.nodes.get(node)['node_color'])
# x = lambda n: ( n,attr for n,attr in graph.nodes(data=True))#return attr['node_color'])
# print(x)
networkx.draw(graph,labels=origin_as_label,font_color='#000000',node_color=colors,font_weight='bold', node_size=sizes)
# networkx.draw_networkx_nodes(graph,pos={str(asn):(0,0)})
# origin_edges = [(u, v) for u, v in graph.edges if graph.nodes[u].get('linkLevel') == 0 or graph.nodes[v].get('linkLevel') == 0]

# other_edges = [(u, v) for u, v in graph.edges if u not in origin_edges and v not in origin_edges]

# # networkx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.2, edge_color='#B6B2B5') #light grey

# #edges connected to the origin AS without transparency (yellows)

# networkx.draw_networkx_edges(graph, pos, edgelist=origin_edges, alpha=1, edge_color='#FCFC05') #yellow



# # Level 1 and 2 Neighbors

# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#8A8A8A', node_size=500, alpha=0.9) #darker grey

# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#B6B2B5', node_size=600, alpha=0.9) #light grey



# # Level 3 Neighbors with light grey outline

# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#FFFFFF', node_size=300, alpha=0.5, edgecolors='#B6B2B5', linewidths=1)



# # Origin AS node last to ensure it's on top

# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='#FCFC05', node_size=1500)


# networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='#000000') #black
# plt.subplot_tool()   
fig.set_facecolor('#ADD8E6')  # Light blue
plt.savefig(f"graphs/{asn}-default-2.png")
plt.show()

