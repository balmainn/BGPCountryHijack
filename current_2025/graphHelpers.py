import networkx
import helpers
import os 
from matplotlib import pyplot 
def construct_digraph(local_preference_results):
    dgraph = networkx.DiGraph() 
    for result in local_preference_results:
        a = result[0]
        op = result[1]
        b = result[2]
        if a not in dgraph.nodes():
            dgraph.add_node(a)
        if b not in dgraph.nodes():
            dgraph.add_node(b)
        if op == '=':
            dgraph.add_edge(a,b)
            dgraph.add_edge(b,a)
        if op  =='>':
            dgraph.add_edge(a,b)
    return dgraph
def add_inequality(graph:networkx.DiGraph, a, relation, b):
    if relation == '>=':
        graph.add_edge(a, b, weight=-1)
        graph.add_edge(b, a, weight=-1)
    elif relation == '=':
        graph.add_edge(a, b, weight=0)
        graph.add_edge(b, a, weight=0)
    elif relation == '>':
        graph.add_edge(a, b, weight=1)
    else:
        raise ValueError(f"Unsupported relation: {relation}")
def extendWithGraphs(inequalities,useShortestPath=True):
    print('extending with graphs! from graph helpers')
    
    if inequalities  == None:
        return inequalities, False
    G = networkx.DiGraph()    
    # Add inequalities to the graph
    shouldContinue = True
    for x, relation, y in inequalities:
        add_inequality(G, x, relation, y)
    #no reason to extend if we're done.
    # basically if we have a >= then we can extend, if we dont then we shouldnt.         
        if relation == '>=':
            #print('did i find >=?')
            return inequalities, False
    # print(shouldContinue, 'should?', not shouldContinue)         
    # if not shouldContinue:
    #     print('should not continue')
    #     return inequalities, False
    found = []
    for node_A in G.nodes():
        for node_B in G.nodes():
            if node_A == node_B:
                continue
            if networkx.has_path(G,node_A,node_B):
                if useShortestPath:
                    paths = networkx.all_shortest_paths(G,node_A,node_B)
                else:
                    paths = networkx.all_simple_paths(G,node_A,node_B)
                for path in paths:
                    if len(path)<=2:
                        continue
                    isZeroPath = False
                    pathWeights = []
                    for i in range(len(path)):
                        u = path[i]
                        try:
                            v = path[i+1]
                        except:
                            break
                        data = G.get_edge_data(u,v)
                        weight = data['weight']
                        pathWeights.append(weight)
                    if all (w==0 for w in pathWeights):
                        if (node_A,'=',node_B) not in found:
                            found.append((node_A,'=',node_B))
                            found.append((node_B,'=',node_A))
                        break
                    if 1 in pathWeights:

                        if (node_A,'>',node_B) not in found:
                            found.append((node_A,'>',node_B))
                   
    newResults = []
    for f in found:
        if f not in inequalities:
            newResults.append(f)
    print('discarding results')                
    newRes = helpers.discardKnownResults(inequalities,newResults)
    haveNewRes = False
    oldInequalities = inequalities
    #print(inequalities)
    newrcnt = 0
    for newR in newRes:
        newrcnt+=1
        inequalities,isNewRes = helpers.addPreferenceToResults_new(inequalities,newR)
        madeCycle, cycles = helpers.detectCycles_ignore_eq(inequalities)
        if madeCycle:
            print('made a cycle! oops on ',newrcnt, 'of ', len(cycles))
            if newR in inequalities:
                inequalities.remove(newR)
        #inequalities = helpers.removeInferiorResults(inequalities)
        #print(inequalities)
        helpers.detectBadChange(inequalities,'inner extend graphs')
        if isNewRes:
            haveNewRes = True
    if haveNewRes:
        pass
        # print('before')
        # print(oldInequalities)
        # print("adding",newRes) 
        # print('after')
        # print(inequalities)
    return inequalities, haveNewRes
def show_graph(dgraph,show,save):

    plt = pyplot
    #pos = networkx.spring_layout(dgraph)
    pos = networkx.circular_layout(dgraph)
    networkx.draw(dgraph,pos,with_labels=True,arrows=True)
    edge_labels = networkx.get_edge_attributes(dgraph, 'weight')

    # Draw the edge labels
    networkx.draw_networkx_edge_labels(dgraph, pos, edge_labels=edge_labels)
    if save:
        print('saving graph')
        watGraphs = os.listdir('watGraphs')
        numGraphs = len(watGraphs)
        plt.savefig(f'watGraphs/{numGraphs}.png')
    if show:
        plt.show() 











        