import requests
import networkx
import pickle
import matplotlib.pyplot as plt #so we can see draw the graph
import os 
PREFIX_P = "185.17.22.0/22"
queryTime = "2024-02-08T09:00:00"

def getWhoIsData(prefix:str) -> str:
    """find the origin AS for a given IP Prefix
    input: prefix -> an ip prefix
    returns: originAS -> the origin AS for the specified IP prefix
             True/False -> is the prefix is multihomed or not"""
    
    url=f"https://stat.ripe.net/data/whois/data.json?resource={prefix}"
    res = requests.get(url)
    json = res.json()
    records = json["data"]["irr_records"]
    tmpTime=""
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


def getNeighbor(asn,query_time):
    """find the neighbors of a given ASN
    returns a set to remove duplicates"""
    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    if os.path.exists(f'pickles/neighbors/{asn}-{safeTime}'):
        neighbors = pickle.load(open(f'pickles/neighbors/{asn}-{safeTime}','rb'))
        return neighbors
    # print("getting neighbor for: ",asn)
    neighbors = set()
    url = f"https://stat.ripe.net/data/asn-neighbours/data.json?resource={asn}&query_time={query_time}&lod=1"
    print("getting neighbors for AS",asn, type(asn))
    res = requests.get(url)
    try:
        json = res.json()
        allneighbors = json["data"]["neighbours"]
    except:
        print("error getting neighbors for ", asn)
        return None
    # print(json)
    
    
    for neighbor in allneighbors:
        neighbors.add(neighbor['asn'])
    pickle.dump(neighbors,open(f'pickles/neighbors/{asn}-{safeTime}','wb'))
    return neighbors
    
def drawGraph(graph:networkx.Graph):
    networkx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()



#~~~~main~~~~#
# asGraph = networkx.DiGraph()
asGraph = networkx.Graph()

originASOfP, isMultihomed = getWhoIsData(PREFIX_P)

asGraph.add_node(originASOfP,linkLevel=0) 
print(f"originAS of p x{originASOfP}x")
lv1Neighbors = getNeighbor(originASOfP,queryTime)
lv2Neighbors = {}
# print('lv1 neighbors: ',lv1Neighbors[0]['asn'])


#graph setup stuff        
for neighbor in lv1Neighbors:
    
    asGraph.add_node(neighbor,linkLevel=1)
    asGraph.add_edge(neighbor,originASOfP)
    lv2Neighbors = getNeighbor(neighbor,queryTime)
    # lv2Neighbors[neighbor] = nextNeighbors
    count = 0
    for lv2Neighbor in lv2Neighbors:
        asGraph.add_node(lv2Neighbor,linkLevel=2)
        asGraph.add_edge(lv2Neighbor,neighbor)

        lv3Neighbors = getNeighbor(lv2Neighbor)
        for lv3neighbor in lv3Neighbors:
            asGraph.add_node(lv3neighbor,linkLevel=3)
            asGraph.add_edge(lv3neighbor,lv2Neighbor)
        # if count < 2:
            
        # count+=1

# drawGraph(asGraph)
        # networkx.shortest_path()

#actually run H on N             
shortestPathsToP = networkx.shortest_path(asGraph,target=originASOfP)


#origin ASN hijacking
for hijackerASN in asGraph.nodes():
    #we dont hijack lv 3 just continue 
    #double check and figure out how to pull data from node
    if hijackerASN[linkLevel] >=3:
        continue
    # if hijackerASN in allLv3Neighbors:
    #     continue
    if hijackerASN == originASOfP:
        print("node is ASNP!")
        score=100 
        # print(shortestPathsToP,type(shortestPathsToP))
        continue
    for potentialVictimASN in asGraph.nodes():

        if potentialVictimASN == originASOfP:
            continue
        #double check how to pull data from node
        if potentialVictimASN[linkLevel] >=3:
            continue

        potentialVictimPathToP = shortestPathsToP[potentialVictimASN]
        victimPathToHijacker = networkx.shortest_path(asGraph,source=potentialVictimASN, target=hijackerASN)
        
        lenVicToP = len(potentialVictimPathToP)
        lenVicToHij = len(victimPathToHijacker)
        if lenVicToHij < lenVicToP:
            score = 100
        if lenVicToHij > lenVicToP:
            score = 0
        if lenVicToHij == lenVicToP:
            score = 50
        #do something with the scores and continue loop. 
        
        
    
    # pathsToHijackerASN = networkx.shortest_path(asGraph,target=node)
    # nodesPathToHijackerASN = pathsToHijackerASN[node]
    # print(nodesPathToHijackerASN)
    # print("node",node," path to p: ",pathToP, 'path to hijacker:',nodesPathToHijackerASN)
    # print(len(pathToP),len(nodesPathToHijackerASN))


    # for path in shortestPaths:
    #     print("path: ",path,type(path))
