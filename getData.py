import networkx
import requests
import os
# asGraph = networkx.Graph()

# for i in range(4):
#     asGraph.add_node(i,linkNum=i)
# asGraph.nodes[0]['origin']='origin'
# asGraph.nodes[1]['second']='second'
# asGraph.nodes[2]['second']='second'
# asGraph.nodes[3]['third']='third'
# for i in range(4):
#     try:
#         asGraph.add_edge(i,i+1)    
#     except:
#         pass

# secondNodes = asGraph.nodes('second')
# thirdNodes = asGraph.nodes('third')
# nodes = asGraph.nodes
# print("nodes",nodes, len(nodes))

# # print(type(secondNodes))
# # nodes = networkx.union
# # print('node',nodes)
# print(asGraph.nodes.data())
# node = asGraph.nodes.get(1)
# node['a'] = 'a'
# print(node)
# print(asGraph.nodes.data())
# for node in asGraph.nodes:
#     nodeWithData = asGraph.nodes.get(node)
#     # data = 
#     print(node)
#     print(nodeWithData)
    

# print(asGraph.nodes.data())
import pickle
asGraph2 = networkx.Graph()

# asGraph2 = pickle.load(open("pickles/asGraph.pickle",'rb'))
# # print('graph2',asGraph2.nodes.data())
# for data in asGraph2.nodes.data():
#     print(data)
# nodeList = list(asGraph.nodes)
# sort = sorted(int(x) for x in nodeList)
# print(sort)
# secondNodes = asGraph.nodes('lv1Neighbor')
# # print(secondNodes)
# nodeslist = [] 
# for node in secondNodes:
#     if node[1] !=None:
#         nodeslist.append(node)
# print(len(nodeslist))


# asGraph2.add_node(1,a=1)
# asGraph2.add_node(2,a=2)
# node = asGraph2.nodes.get(23)
# if node == None:
#     print("DNE")
# # node['b'] = 2
# # asGraph2.add_node(2,a=3)
# print(len(asGraph2.nodes))

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

# file = "pickles/asGraph-199362.pickle"
# asGraph = pickle.load(file,'rb')
def loadPrefixes():
    lines = []
    with open("prefixTestSet.txt",'r') as f:
        for line in f.readlines():    
            if not line.startswith("#"):
                lines.append(line.strip())
    return lines

# prefixes = loadPrefixes()
# # print(prefixes)
# info = pickle.load(open("pickles/countries/AW-info.pickle","rb"))
# print(info)
# asGraph=networkx.Graph()

# asGraph = pickle.load(open("pickles/asGraph-11816.pickle",'rb'))
# for node in asGraph.nodes():
    
#     data = asGraph.nodes.get(node)
#     edges = networkx.edges(asGraph, [node])
#     print(node, "has ",len(edges), "neighbors")
#     print(node)
#     print(edges)
#     break

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
        print(asn," neighbors returned from file")
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
    #uncomment on go <TODO>
    pickle.dump(neighbors,open(f'pickles/neighbors/{asn}-{safeTime}','wb'))
    return neighbors

from multiprocessing import Pool

def addToGraph(neighbors,asGraph:networkx.Graph,someAS,linkLevel):
    print("adding, neighbors to graph for",someAS)
    if neighbors == None:
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


def multiProcessNeighbors(neighbors):
    # print(neighbors, "is type; ", type(neighbors))
    if type(neighbors) is int:
        neighbor = getNeighbor(neighbors,queryTime)
        return neighbor
    else:
        allNeighbors = []
        for neighbor in neighbors:
            neigh = getNeighbor(neighbor,queryTime)
            allNeighbors.append(neigh)
        return allNeighbors
    

def getData(originASOfP):
    print("SETTING UP GRAPH!")
    asGraph = networkx.Graph()
    asGraph.add_node(originASOfP,origin='origin',linkLevel=0) 
    print(f"originAS of p x{originASOfP}x")
    lv1Neighbors = getNeighbor(originASOfP,queryTime)
    addToGraph(lv1Neighbors,asGraph,originASOfP,1)
    pool = Pool(processes=8)
    res = pool.map_async(multiProcessNeighbors,list(lv1Neighbors))
    res.wait()
    lv2Neighbors = res.get()
    res2 = pool.map_async(multiProcessNeighbors,list(lv2Neighbors))
    res2.wait()
    pool.close()
    pool.join()
    

    # for neighbor in lv1Neighbors:
        

    #     lv2Neighbors = getNeighbor(neighbor,queryTime)
       
    #     isNone = addToGraph(lv2Neighbors,asGraph,neighbor,2)
    #     if isNone==None:
    #         continue
    #     for neigh in lv2Neighbors:
    #         lv3Neighbors = getNeighbor(neigh,queryTime)
    #         addToGraph(lv3Neighbors,asGraph,neigh,3)
    # # pickle.dump(asGraph,open(f"pickles/asGraph-{originASOfP}.pickle",'wb'))
    # print("DONE!")
    # return asGraph
        # count+=1
def getWhoIsData(prefix:str) -> str:
    """find the origin AS for a given IP Prefix
    input: prefix -> an ip prefix
    returns: originAS -> the origin AS for the specified IP prefix
             True/False -> is the prefix is multihomed or not"""
    print("getting whois for: ",prefix)
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
    
# PREFIX_P = "128.223.0.0/16"
PREFIX_P = "210.78.147.0/24"

# queryTime = "2024-02-08T09:00:00"
global queryTime 
queryTime = "2024-03-01T09:00:00"
def loadPrefixes():
    lines = []
    with open("prefixTestSet.txt",'r') as f:
        for line in f.readlines():    
            if not line.startswith("#"):
                lines.append(line.strip())
    return lines
#~~~~main~~~~#

prefixes = loadPrefixes() #WIP
for prefix in prefixes: 
    originsASOfPStart, isMultihomed  = getWhoIsData(prefix)
    
    if isMultihomed:
        for asn in originsASOfPStart:
            getData(asn)
    else:
        getData(originsASOfPStart)
        #vatican ASNs '8978', '61160', '202865'
asns = ['199524','174']#, , '174']#'8978', '61160']#, '202865','24482']
#huge ases 24482 199524, 174
for asn in asns:
    getData(asn)
# print(isMultihomed)
# getData(originsASOfPStart)