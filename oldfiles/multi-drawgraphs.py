import pickle

import os 

from matplotlib import pyplot 
import networkx

def drawGraph(graph:networkx.Graph,asn):
    plt = pyplot
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.axis('off')

    fig.set_facecolor('#ADD8E6')  # Light blue


    print('starting spring layout')
    pos = networkx.draw(graph)
    # pos = networkx.spring_layout(graph)
    print('spring done')


    # Separate edges based on whether they are connected to the origin AS

    origin_edges = [(u, v) for u, v in graph.edges if graph.nodes[u].get('linkLevel') == 0 or graph.nodes[v].get('linkLevel') == 0]

    other_edges = [(u, v) for u, v in graph.edges if u not in origin_edges and v not in origin_edges]



    #edges with higher transparency (grey ones)
    try:
        networkx.draw_networkx_edges(graph, pos, edgelist=other_edges, alpha=0.2, edge_color='#B6B2B5') #light grey
    except:
        pass

    #edges connected to the origin AS without transparency (yellows)
    try:
        networkx.draw_networkx_edges(graph, pos, edgelist=origin_edges, alpha=1, edge_color='#FCFC05') #yellow
    except:
        pass



    # Level 1 and 2 Neighbors
    try:
        #lv1 -> dark grey
        networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 1], node_color='#8A8A8A', node_size=500, alpha=0.9) #darker grey
    except:
        pass

    try:
        #lv2 -> light grey
        networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 2], node_color='#B6B2B5', node_size=600, alpha=0.9) #light grey
    except:
        pass

    

    # Level 3 Neighbors with light grey outline
    #lv3 -> white with grey edges 
    try:
        networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 3], node_color='#FFFFFF', node_size=300, alpha=0.5, edgecolors='#FCFC05', linewidths=1)
    except:
        pass



    # Origin AS node last to ensure it's on top
    try:
        networkx.draw_networkx_nodes(graph, pos, nodelist=[n for n, attr in graph.nodes(data=True) if attr.get('linkLevel') == 0], node_color='#FCFC05', node_size=1500)
    except:
        pass



    # label

    origin_as_label = {n: n for n, attr in graph.nodes(data=True) if attr.get('origin') == 'origin'}
    try:
        networkx.draw_networkx_labels(graph, pos, labels=origin_as_label, font_color='#000000') #black
    except:
        pass

    # for i in range(3):
    #     plotshow()
    plt.savefig(f'graphs/{asn}-graph.png')
    plt.clf()

files = os.listdir('pickles/')
datafiles = []
for file in files:
    if file.startswith('asGraph-') and file.endswith('.pickle'):
        print(file)
        datafiles.append('pickles/'+file)
graphs = []

count = 1
for file in datafiles[:2]:
    a = file.find('-')
    b = file.find('.')
    # asn = file[a+1:b]
    asn = 264645
    if asn == '3582':
        continue
    graph = networkx.Graph()
    graph = pickle.load(open(f'pickles/asGraph-{asn}.pickle','rb'))     
    # graph = pickle.load(open(file,'rb'))
    # graphs.append((graph,str(asn)+f'-{count}'))
    print(file, "has ", len(graph.nodes), "nodes")
    drawGraph(graph, str(asn)+f'-{count}')
    print(f"{count} / {len(datafiles)} done")


