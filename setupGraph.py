import networkx
import os 
import pickle 
import requests

def setupGraph(originASOfP):
    """Creates a graph with the origin AS as the start node
    params:
        originASOfP: an ASN we want to get the lv1,2, and 3 neighbors for and produce a graph of
    returns: 
        asGraph: a networkx (unweighted undirected) graph 
        """
    print("SETTING UP GRAPH!")
    asGraph = networkx.Graph()
    asGraph.add_node(originASOfP,origin='origin',linkLevel=0) 
    print(f"originAS of p x{originASOfP}x")
    masterNeighbors = pickle.load(open('pickles/masterNeighborTable.pickle','rb'))
    lv1Neighbors = masterNeighbors[originASOfP]
    #add level 1 neighbors to graph
    addToGraph(lv1Neighbors,asGraph,originASOfP,1)
    nc = 0
    #add lv 2 neighbors to the graph
    for neighbor in lv1Neighbors:
        print('lv1 ',nc ,"/", len(lv1Neighbors))
        nc+=1
        try:
            lv2Neighbors = masterNeighbors[str(neighbor)]
        except Exception as e:
            print("error adding lv2 neighbors for ",neighbor)
            continue
        
        isNone = addToGraph(lv2Neighbors,asGraph,neighbor,2)
        if isNone==None:
            continue
        nc2 = 0
        #add lv 3 neighbors to graph
        for neigh in lv2Neighbors:
            print('lv1 ',nc ,"/", len(lv1Neighbors), 'lv2 ',nc2 ,"/", len(lv2Neighbors))
            try:
                lv3Neighbors = masterNeighbors[str(neigh)]
                addToGraph(lv3Neighbors,asGraph,neigh,3)
            except Exception as e:
                print("errror adding lv3 neighbor", e)
                
            
            nc2+=1
    #save the file when complete so we dont have to do this again
    # pickle.dump(asGraph,open(f"pickles/asGraph-{originASOfP}.pickle",'wb'))
    print("DONE!")
    return asGraph
       # print('no')
def getNeighbor(asn):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    """
    query_time= "2024-03-01T09:00:00"
    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    
    print("getting neighbor for: ",asn)
    neighbors = set()
    url = f"https://stat.ripe.net/data/asn-neighbours/data.json?resource={asn}&query_time={query_time}&lod=1"
    print("getting neighbors for AS",asn, type(asn))
    res = requests.get(url)
    try:
        json = res.json()
        allneighbors = json["data"]["neighbours"]
        print('all neighbors: ', allneighbors)
    except:
        print("error getting neighbors for ", asn)
        return
    # print(json)
    
    
    for neighbor in allneighbors:
        neighbors.add(neighbor['asn'])
    # if len(neighbors) !=0: 
    print(neighbors) 
        


def addToGraph(neighbors,asGraph:networkx.Graph,someAS,linkLevel):
    """Adds nodes and edges to a graph
    params: 
        neighbors: a set/list of neighbors
        asGraph: a networkx graph we want to add nodes/edges to.
        someAS: the AS we are linking to in the edge
        linkLevel: the link level of the neighbor (0,1,2,3)
    returns:
        None: on error (neighbors is empty)
        1: on success"""
    # print("adding, neighbors to graph for",someAS)
    if neighbors == None or len(neighbors) == 0:
        print("no neighbors to add!")
        return None
    for neighbor in neighbors:
        neighborData = asGraph.nodes.get(neighbor)
        if neighborData == None:
            asGraph.add_node(neighbor,linkLevel=linkLevel)
            asGraph.add_edge(neighbor,someAS)
        else:
            asGraph.add_edge(neighbor,someAS)
    return 1
def loadPrefixes():
    """loads prefixes for testing stored in prefixTestSet.txt
    params: 
        nothing
    returns:
        lines: a list of prefixes
    """
    lines = []
    with open("prefixTestSet.txt",'r') as f:
        for line in f.readlines():    
            if not line.startswith("#"):
                lines.append(line.strip())
    return lines

def getWhoIsData(prefix:str) -> str:
    """find the origin AS for a given IP Prefix
    params: prefix -> an ip prefix
    returns: originAS -> the origin AS for the specified IP prefix
             True/False -> is the prefix is multihomed or not"""
    print("getting whois for: ",prefix)
    url=f"https://stat.ripe.net/data/whois/data.json?resource={prefix}"
    res = requests.get(url)
    json = res.json()
    records = json["data"]["irr_records"]
    origins=[]
    allOrigins=[]
    modified=[]
    
    for rec in records:
        
        keyed = False
        for r in rec:
            # print(r)
            if r['key'] == 'route' and r['value'] == prefix: #exact match
                # print(r['value'], "MATches")
                keyed = True
            if r['key']=='origin':
                allOrigins.append(r['value'])
            if(r['key']=='origin' and keyed):
                origins.append(r['value'])
            if(r['key']=='last-modified' and keyed):
                modified.append(r['value'])
    print(records)
    if len(origins) ==0:
        origins = allOrigins
        
    print(origins, modified)
    if (len(set(origins))>1):
        print("more than 1 origin as, that seems like a problem batman")
        print("this is probably multihomed which is not supported yet")
        
        # exit(1)
        return origins, True
    else:
        origin= origins[0]
        return origin, False
prefixes = loadPrefixes() 
        #vatican ASNs '8978', '61160', '202865'

setupGraph('174')

# for prefix_p in prefixes:
    
#     originsASOfPStart, isMultihomed = getWhoIsData(prefix_p)

#     if isMultihomed:
#         for originP in originsASOfPStart:
#             asGraph = setupGraph(originP)
#     else:
#         asGraph = setupGraph(originP)