import requests
import networkx
import pickle
import matplotlib.pyplot as plt #so we can see draw the graph
import os 
#TODO FIND UOREGON'S IP BLOCK AND USE THAT FOR PREFIX_P FOR FUNSIES!
PREFIX_P = "185.17.22.0/22"
queryTime = "2024-02-08T09:00:00"
#global flag to get data or reuse the saved graph
GET_DATA = False

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

def asnsHung():
    """asns that have a problem returning data from RIPE
    will be used eventually"""
    
    return [1299,2914,3356,6762]


def getNeighbor(asn,query_time):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    """

    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    if os.path.exists(f'pickles/neighbors/{asn}-{safeTime}'):
        neighbors = pickle.load(open(f'pickles/neighbors/{asn}-{safeTime}','rb'))
        return neighbors
    if asn in asnsHung():
        #dont bother with ASNs that just hang
        return None
    print("getting neighbor for: ",asn)
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

def updateNode(node,key,value):
    """updates a given node"""
    node[key]=value


def setupGraph():
    print("SETTING UP GRAPH!")
    asGraph = networkx.Graph()
    asGraph.add_node(originASOfP,origin='origin',linkLevel=0) 
    print(f"originAS of p x{originASOfP}x")
    lv1Neighbors = getNeighbor(originASOfP,queryTime)

    # print('lv1 neighbors: ',lv1Neighbors[0]['asn'])


    #graph setup stuff        
    for neighbor in lv1Neighbors:
        
        asGraph.add_node(neighbor,lv1Neighbor='lv1Neighbor',linkLevel=1)
        asGraph.add_edge(neighbor,originASOfP)
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

    return asGraph
        # count+=1

def searchPotentialVictims(asGraph,originASOfP,shortestPathsToP,hijackerASN):
    #victims can be both a lv2 node and a lv3 node. 
    #this is not a problem as the link level determines what 'neighbor level' it is wrt ASN0
    print("searching potential victms")
    fullyHijackableCounter = 0
    partiallyHijackableCounter = 0
    notHijackableCounter = 0
    count = 0
    for potentialVictimASN in asGraph.nodes:
        potentialVictimASNData = asGraph.nodes.get(potentialVictimASN)
        count +=1
        # if count >=MAXNODES:
        #     break
        #how do we handle this case? 
        if potentialVictimASN == hijackerASN:
            fullyHijackableCounter+=1
            score = 100
            continue
            
        if potentialVictimASN == originASOfP:
            continue
        
        if potentialVictimASNData['linkLevel'] >=3:
            continue
        
        # print('victim', potentialVictimASNData)
        potentialVictimPathToP = shortestPathsToP[potentialVictimASN]
        victimPathToHijacker = networkx.shortest_path(asGraph,source=potentialVictimASN, target=hijackerASN)
        
        lenVicToP = len(potentialVictimPathToP)
        lenVicToHij = len(victimPathToHijacker)
        if lenVicToHij < lenVicToP:
            score = 100
            fullyHijackableCounter+=1

        if lenVicToHij > lenVicToP:
            notHijackableCounter+=1
            score = 0
            
        if lenVicToHij == lenVicToP:
            partiallyHijackableCounter+=1
            score = 50
        # print("SCORE IS: ",score)
        #do something with the scores and continue loop. 
    print(count)
    print("fully: ",fullyHijackableCounter, "partial", partiallyHijackableCounter,"not", notHijackableCounter)

#~~~~main~~~~#
originASOfP, isMultihomed = getWhoIsData(PREFIX_P)

if GET_DATA:

    asGraph = setupGraph()
    
else:
    print("loading as grpah from file")
    asGraph = pickle.load(open("pickles/asGraph.pickle",'rb'))

# drawGraph(asGraph)
        # networkx.shortest_path()
# print(len(asGraph))
#actually run H on N             
shortestPathsToP = networkx.shortest_path(asGraph,target=originASOfP)

#for testing limit hijacker asn and victims to 5 each
# MAXNODES = 1000

#origin ASN hijacking
counter = 0
for hijackerASN in asGraph.nodes:
    print("examining hijacker", hijackerASN)
    # print(count, len(asGraph.nodes))
    hijackerASNData = asGraph.nodes.get(hijackerASN)
    #we dont hijack lv 3 just continue 
    # if counter >=MAXNODES:
    #     break
    if hijackerASNData['linkLevel'] >=3:
        print("break lv 3")
        continue
    
    # print("hijacker", hijackerASN,hijackerASNData)
    
    
    # print(type(hijackerASNData['linkLevel']))
    # break
    
    # if hijackerASN in allLv3Neighbors:
    #     continue
    if hijackerASN == originASOfP:
        print("node is ASNP!")
        score=100 
        # print(shortestPathsToP,type(shortestPathsToP))
        continue
    searchPotentialVictims(asGraph,originASOfP,shortestPathsToP,hijackerASN)
    counter +=1
print("ran search on ",counter," candidates")        

    
    # pathsToHijackerASN = networkx.shortest_path(asGraph,target=node)
    # nodesPathToHijackerASN = pathsToHijackerASN[node]
    # print(nodesPathToHijackerASN)
    # print("node",node," path to p: ",pathToP, 'path to hijacker:',nodesPathToHijackerASN)
    # print(len(pathToP),len(nodesPathToHijackerASN))


    # for path in shortestPaths:
    #     print("path: ",path,type(path))
# print(asGraph.number_of_nodes())