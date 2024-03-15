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
    picklefile = f'pickles/graphs/{asn}-pos.pickle'
    if os.path.exists(picklefile):
        print("path exists, loading...")
        pos = pickle.load(open(picklefile,'rb'))
        print("loading done!")
    # Separate edges based on whether they are connected to the origin AS
    else:
        print("starting spring layout")
        pos = networkx.spring_layout(graph)
        print("layout done!")
        pickle.dump(pos,open(picklefile,'wb'))
        print("dump done!")
    
    # Separate edges based on whether they are connected to the origin AS

    origin_edges = [(u, v) for u, v in graph.edges if graph.nodes[u].get('linkLevel') == 0 or graph.nodes[v].get('linkLevel') == 0]

    other_edges = [(u, v) for u, v in graph.edges if u not in origin_edges and v not in origin_edges]



    #edges with higher transparency (grey ones)

    networkx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.2, edge_color='#B6B2B5') #light grey

    #edges connected to the origin AS without transparency (yellows)

    networkx.draw_networkx_edges(graph, pos, edgelist=origin_edges, alpha=1, edge_color='#FCFC05') #yellow



    # Level 1 and 2 Neighbors

    networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#8A8A8A', node_size=500, alpha=0.9) #darker grey

    networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#B6B2B5', node_size=600, alpha=0.9) #light grey

    

    # Level 3 Neighbors with light grey outline

    networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#FFFFFF', node_size=300, alpha=0.5, edgecolors='#B6B2B5', linewidths=1)



    # Origin AS node last to ensure it's on top

    networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='#FCFC05', node_size=1500)



    # label

    origin_as_label = {n: n for n, attr in graph.nodes(data=True) if attr.get('origin') == 'origin'}

    networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='#000000') #black


    plt.savefig(f"graphs/as-{asn}-graph2.png")
    plt.show()


    # origin_edges = [(u, v) for u, v in graph.edges if graph.nodes[u].get('linkLevel') == 0 or graph.nodes[v].get('linkLevel') == 0]

    # other_edges = [(u, v) for u, v in graph.edges if u not in origin_edges and v not in origin_edges]



    # #edges with higher transparency (grey ones)

    # networkx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.2, edge_color='#B6B2B5') #light grey

    # #edges connected to the origin AS without transparency (yellows)

    # networkx.draw_networkx_edges(graph, pos, edgelist=origin_edges, alpha=1, edge_color='#FCFC05') #yellow



    # # Level 1 and 2 Neighbors

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#8A8A8A', node_size=500, alpha=0.9) #darker grey

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#B6B2B5', node_size=600, alpha=0.9) #light grey

    

    # # Level 3 Neighbors with light grey outline

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#FFFFFF', node_size=300, alpha=0.5, edgecolors='#FCFC05', linewidths=1)



    # # Origin AS node last to ensure it's on top

    # networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='#FCFC05', node_size=1500)



    # # label

    # origin_as_label = {n: n for n, attr in graph.nodes(data=True) if attr.get('origin') == 'origin'}

    # networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='#000000') #black


    # plt.savefig(f"graphs/as-{asn}-graph.png")
    # plt.show()



# def plotshow():
#     plt.show()

# def drawGraph(graph:networkx.Graph):

#     fig, ax = plt.subplots(figsize=(8, 6))

#     ax.axis('off')

#     fig.set_facecolor('#ADD8E6')  # Light blue


#     print('starting spring layout')
#     pos = networkx.draw(graph)
#     # pos = networkx.spring_layout(graph)
#     print('spring done')


#     # Separate edges based on whether they are connected to the origin AS

#     origin_edges = [(u, v) for u, v in graph.edges if graph.nodes[u].get('linkLevel') == 0 or graph.nodes[v].get('linkLevel') == 0]

#     other_edges = [(u, v) for u, v in graph.edges if u not in origin_edges and v not in origin_edges]



#     #edges with higher transparency (grey ones)
#     try:
#         networkx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.2, edge_color='#B6B2B5') #light grey
#     except:
#         pass
#     #edges connected to the origin AS without transparency (yellows)
#     try:
#         networkx.draw_networkx_edges(graph, pos, edgelist=origin_edges, alpha=1, edge_color='#FCFC05') #yellow
#     except:
#         pass



#     # Level 1 and 2 Neighbors
#     try:
#         networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#8A8A8A', node_size=500, alpha=0.9) #darker grey
#     except:
#         pass
#     try:
#         networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#B6B2B5', node_size=600, alpha=0.9) #light grey
#     except:
#         pass

    

#     # Level 3 Neighbors with light grey outline
#     try:
#         networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#FFFFFF', node_size=300, alpha=0.5, edgecolors='#FCFC05', linewidths=1)
#     except:
#         pass


#     # Origin AS node last to ensure it's on top
#     try:
#         networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='#FCFC05', node_size=1500)
#     except:
#         pass



#     # label
#     try:
#         origin_as_label = {n: n for n, attr in graph.nodes(data=True) if attr.get('origin') == 'origin'}
#     except:
#         pass
#     try:
#         networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='#000000') #black
#     except:
#         pass

#     # for i in range(3):
#     #     plotshow()
#     plt.show()

# asn = 264645
# asn = 8978
asn = 174
graph = pickle.load(open(f'pickles/asGraph-{asn}.pickle','rb'))
print('graph loaded')
drawGraph(graph,asn)
# files = os.listdir('pickles/')
# datafiles = []
# for file in files:
#     if file.startswith('asGraph-') and file.endswith('.pickle'):
#         print(file)
#         datafiles.append('pickles/'+file)
# graphs = []
# for file in datafiles:
#     graph = pickle.load(open(file,'rb'))
#     graphs.append(graph)
#     print(file, "has ", len(graph.nodes), "nodes")





# asn = 3582

# print("graph loaded")
# # exit(1)
# print(len(graph.nodes), "nodes in graph")
# pos = networkx.spring_layout(graph)

# print("spring layout")

# # Draw nodes with different styles for each neighbor level

# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='yellow', label='Origin AS', node_size=700)
# print('origin AS drawn')
# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#757575', label='Level 1 Neighbors', node_size=500)
# print('lv1 drawn')
# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#bababa', label='Level 2 Neighbors', node_size=300)
# print('lv2 drawn')
# networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#f6f3f3', label='Level 3 Neighbors', node_size=100)
# print('lv3 drawn')


# # # edges with different styles

# edge_colors = []
# # for node in graph.nodes:
# for data in graph.edges(data=True):
    
#     if graph.nodes[data[0]].get('linkLevel') == 0:
#         edge_colors.append('yellow')
#     else:
#         edge_colors.append('white')
# # 'yellow' else '#ffffff' for data in graph.edges(data=True)
# print("for edges done")
# networkx.draw_networkx_edges(graph, pos, edge_color=edge_colors)
# print('edges done')


# # labels for the origin AS node only

# origin_as_label = {n: n for n, attr in graph.nodes(data=True) if attr.get('origin') == 'origin'}

# networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='black')
# print('network labels')

# plt.show()