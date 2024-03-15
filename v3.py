import requests
import networkx
import pickle
import matplotlib.pyplot as plt #so we can see draw the graph
import os 

#all data should be collected at a certain point in time
#edit this line to change the time. 
queryTime = "2024-03-01T09:00:00"
#global flag to get data or reuse the saved graph
GET_DATA = False

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

def asnsHung():
    """asns that have a problem returning data from RIPE
    likely issue: they are too big and timeout.
    These ASNs are skipped to improve performance when getting data"""
    
    return [1299,2914,3356,6762,6461]


def getNeighbor(asn,query_time):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    params: 
        asn: the asn we want the neighbors for.
            type: str or int. 
        query_time: the time we use to get the neighbors for.
            type: str
    returns:
        neighbors: a set of neighbor ASes
            None on error
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
    """draws a graph, this function can take hours, if the graph is huge"""
    networkx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()

def updateNode(node,key,value):
    """updates a given node
    this function is not currently used, but might be useful later"""
    node[key]=value



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
    lv1Neighbors = getNeighbor(originASOfP,queryTime)
    #add level 1 neighbors to graph
    addToGraph(lv1Neighbors,asGraph,originASOfP,1)
    nc = 0
    #add lv 2 neighbors to the graph
    for neighbor in lv1Neighbors:
        print('lv1 ',nc ,"/", len(lv1Neighbors))
        nc+=1
        lv2Neighbors = getNeighbor(neighbor,queryTime)
       
        isNone = addToGraph(lv2Neighbors,asGraph,neighbor,2)
        if isNone==None:
            continue
        nc2 = 0
        #add lv 3 neighbors to graph
        for neigh in lv2Neighbors:
            print('lv1 ',nc ,"/", len(lv1Neighbors), 'lv2 ',nc2 ,"/", len(lv2Neighbors))
            lv3Neighbors = getNeighbor(neigh,queryTime)
            addToGraph(lv3Neighbors,asGraph,neigh,3)
            nc2+=1
    #save the file when complete so we dont have to do this again
    pickle.dump(asGraph,open(f"pickles/asGraph-{originASOfP}.pickle",'wb'))
    print("DONE!")
    return asGraph
        

def searchPotentialVictims(asGraph:networkx.Graph,originASOfP,shortestPathsToP,hijackerASN):
    """Ask nodes if the hijacking is successful.
    params: 
        asGraph:networkx.Graph the graph we search
        originASOfP: P's origin AS
        shortestPathsToP: dictionary of paths from every node to P 
            this is generated by the following line in another function
            networkx.shortest_path(asGraph,target=originASOfP)
        hijackerASN: which AS is acting as a hijacker
    returns:
        count: used for information, the number of ASes we queried for hijacking success
        fullyHijackableCounter: the number of successful hijacks (score 100)
        partiallyHijackableCounter: the number of partial hijacks (score 50)
        notHijackableCounter: the number of failed hijacks (score 0)"""
    #victims can be both a lv2 node and a lv3 node. 
    #this is not a problem as the link level determines what 'neighbor level' it is wrt ASN0
    print("searching potential victms")
    fullyHijackableCounter = 0
    partiallyHijackableCounter = 0
    notHijackableCounter = 0
    count = 0

    for potentialVictimASN in asGraph.nodes:
        potentialVictimASNData = asGraph.nodes.get(potentialVictimASN)
        
        #used for debug break early for testing
        # if count >=10:
        #     break
        
        if potentialVictimASN == hijackerASN:
            fullyHijackableCounter+=1
            #score = 100
            continue
        
        #we dont ask the origin of P, as it will always fail so just continue
        if potentialVictimASN == originASOfP:
            continue
        
        #dont check lv3 neighbors
        if potentialVictimASNData['linkLevel'] >=3:
            continue
        
        count +=1
        # print('victim', potentialVictimASNData)
        potentialVictimPathToP = shortestPathsToP[potentialVictimASN]
        victimPathToHijacker = networkx.shortest_path(asGraph,source=potentialVictimASN, target=hijackerASN)
        
        lenVicToP = len(potentialVictimPathToP)
        lenVicToHij = len(victimPathToHijacker)
        # print("path to p",potentialVictimPathToP, lenVicToP)
        # print("victim to hij",victimPathToHijacker, lenVicToHij)
        if lenVicToHij < lenVicToP:
            #score = 100
            fullyHijackableCounter+=1

        if lenVicToHij > lenVicToP:
            notHijackableCounter+=1
            #score = 0
            
        if lenVicToHij == lenVicToP:
            partiallyHijackableCounter+=1
            #score = 50
        # print("SCORE IS: ",score)
        
    # print(count)
    print("fully: ",fullyHijackableCounter, "partial", partiallyHijackableCounter,"not", notHijackableCounter)
    return count,fullyHijackableCounter, partiallyHijackableCounter, notHijackableCounter
    #return scores and sum

def countLevels(asGraph:networkx.Graph):
    """counts the number of neighbors for each level
    params:
        asGraph: the graph that checked
    returns: 
        returns: 
            lv1: the number of level 1 neighbors (origin's neighbors)
            lv2: the number of level 2 neighbors (origin's neighbors' neighbors)
            lv3: the number of level 3 neighbors (origin's neighbors' neighbors' neighbors) 
    """
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

def performHijack(asGraph,originASOfP):
    #actually run H on N 
    """Performs the hijack simulation
    params:
        asGraph: Graph we run the simulation on
        originASOfP: the origin AS of P
    returns: 
        avgs: dictionary keyed with a hijacker's ASN
            contains: (average,fullyHijackableCounter,partiallyHijackableCounter,notHijackableCounter)
        counter: the number of hijacks attempted 
        ctr3: the number of times we query different ASes if the hijacking is successful or not
        hijskip: the number times hijacking ASes skipped
        origskip: the number of times the origin was skipped
        counters and skips are used for information and debugging only. 
    """
    
    shortestPathsToP = networkx.shortest_path(asGraph,target=originASOfP)

    #for testing limit only attempt this many hijacker ASNs
    MAXNODES = 10

    #origin ASN hijacking
    counter = 0
    ctr3 = 0
    hijskip = 0
    origskip = 0
    avgs = {}
    #count the different levels for debugging
    lv1, lv2, lv3 = countLevels(asGraph)
    for hijackerASN in asGraph.nodes:
        
        print("examining hijacker", hijackerASN, " number ",counter, "/ ", lv1+lv2)
        # print(count, len(asGraph.nodes))
        hijackerASNData = asGraph.nodes.get(hijackerASN)
        
        #used for debug and testing
        # if counter >=MAXNODES:
        #     break

        #we dont hijack lv 3 just continue 
        if hijackerASNData['linkLevel'] >=3:
            print("break lv 3")
            hijskip +=1
            continue
        
        # print("hijacker", hijackerASN,hijackerASNData)
        
        if hijackerASN == originASOfP:
            print("node is ASNP!")
            origskip+=1
            score=100 
            # print(shortestPathsToP,type(shortestPathsToP))
            continue
        ct, fullyHijackableCounter, partiallyHijackableCounter, notHijackableCounter =searchPotentialVictims(asGraph,originASOfP,shortestPathsToP,hijackerASN)
        ctr3+=ct
        
        #calculate weighted average percentile
        average =  (100*fullyHijackableCounter + 50*partiallyHijackableCounter)/(fullyHijackableCounter+partiallyHijackableCounter+notHijackableCounter)
        #store information in the avgs dict
        avgs[hijackerASN] = (average,fullyHijackableCounter,partiallyHijackableCounter,notHijackableCounter)

        counter +=1

    return avgs,counter,ctr3,hijskip,origskip 

def storeScores(avgs,originP,asGraph:networkx.Graph):
    """stores the avgs table in a csv table
    params:
        avgs: dictionary keyed with a hijacker's ASN
            contains: (average,fullyHijackableCounter,partiallyHijackableCounter,notHijackableCounter)
        originP: the origin AS of P
        asGraph:networkx.Graph, graph is needed for link level query
    returns:
        nothing
    """
    with open(f"scores/hijackingScores-{originP}.csv","w") as f: 
        f.write("hijacker ASN,AVG,success, partial, failure,linkLevel,number direct Neighbors\n")    
        for hijackerASN in avgs:
            hijackerAverage = avgs[hijackerASN][0]
            success = avgs[hijackerASN][1]
            partial = avgs[hijackerASN][2]
            failure = avgs[hijackerASN][3]
            node = asGraph.nodes.get(hijackerASN)
            linkLevel = node['linkLevel']
            edges = networkx.edges(asGraph, [hijackerASN])
            numNeighbors = len(edges)
            f.write(f"{hijackerASN},{hijackerAverage},{success},{partial},{failure},{linkLevel},{numNeighbors}\n")
            # print("if hijacker ", hijackerASN, "hijacked, the average success is ",hijackerAverage)
            print("hijacker ", hijackerASN, "average", hijackerAverage, f"success {success} partial {partial} failure {failure} linkLevel {linkLevel}")

def countData(counter,ctr3,hijskip,origskip,asGraph:networkx.Graph):
    """same as getLevels, but prints information"""
    print("ran search on ",counter," candidates", "searched for ",ctr3, " potential victms", "hij skkp: ",hijskip, " orig skip ",origskip, "total: ",hijskip+origskip)        
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
    print("lv1 ", lv1, "lv2,",lv2, "lv3, ",lv3, "sum ",lv1+lv2+lv3)
    return lv1, lv2, lv3
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

def createDirs():
    """sets up initial directory structure if it doesnt exist
    params: nothing
    returns: nothing"""
    if os.path.exists('scores'):
        os.makedirs('scores')
    if os.path.exists('imgs'):
        os.makedirs('imgs')
    if os.path.exists('graphs'):
        os.makedirs('graphs')
    if os.path.exists('pickles'):
        os.makedirs('pickles')
    if os.path.exists('pickles/graphs'):
        os.makedirs('pickles/graphs')
    if os.path.exists('pickles/neighbors'):
        os.makedirs('pickles/neighbors')
    
    
#main body without a main function
#~~~~main~~~~#
createDirs()
prefixes = loadPrefixes() 
        #vatican ASNs '8978', '61160', '202865'


for prefix_p in prefixes:
    
    originsASOfPStart, isMultihomed = getWhoIsData(prefix_p)

    if isMultihomed:
        #do the same steps for both ASes
        
        print("IS MULTIHOMED")
        # print(originsASOfPStart)
        # exit(1)
        for originP in originsASOfPStart:
            asGraph = networkx.Graph()
            avgs =0
            counter =0
            ctr3 =0
            hijskip =0
            origskip =0
            lv1 =0
            lv2 =0
            lv3 =0 
            if GET_DATA:
                asGraph = setupGraph(originP)
            else:   
                print("loading as graph from file")
                asGraph = pickle.load(open(f"pickles/asGraph-{originP}.pickle",'rb'))
            # #delete nodes that only have 1 neighbor or are disjoint (shouldnt be possible but jic ig)
            # remove = [node for node, degree in asGraph.degree() if degree <= 1]
            # asGraph.remove_nodes_from(remove)
            avgs,counter,ctr3,hijskip,origskip = performHijack(asGraph,originP)
            lv1,lv2,lv3 = countData(counter,ctr3,hijskip,origskip,asGraph)
            storeScores(avgs,originP,asGraph)
            
        
    else:
        avgs =0
        counter =0
        ctr3 =0
        hijskip =0
        origskip =0
        lv1 =0
        lv2 =0
        lv3 =0 
        asGraph = networkx.Graph()
        if GET_DATA:
            asGraph = setupGraph(originsASOfPStart)
        else:
            
            print("loading as graph from file")
            asGraph = pickle.load(open(f"pickles/asGraph-{originsASOfPStart}.pickle",'rb'))
        # #delete nodes that only have 1 neighbor or are disjoint (shouldnt be possible but jic ig) leaving this in case we need it later
        # remove = [node for node, degree in asGraph.degree() if degree <= 1]
        # asGraph.remove_nodes_from(remove)
        avgs,counter,ctr3,hijskip,origskip = performHijack(asGraph,originsASOfPStart)
        
        storeScores(avgs,originsASOfPStart,asGraph)
        countData(counter,ctr3,hijskip,origskip,asGraph)

#same as above but for ASNs instead 
    #uncomment below to do tests on specific ASNS  

# asns = ['24482'] #'199524''174']'8978']'61160']#, '202865']#,
# GET_DATA = True

# for asn in asns:
#     avgs =0
#     counter =0
#     ctr3 =0
#     hijskip =0
#     origskip =0
#     lv1 =0
#     lv2 =0
#     lv3 =0 
#     asGraph = networkx.Graph()
#     if GET_DATA:
#         asGraph = setupGraph(asn)
#     else:
        
#         print("loading as graph from file")
#         asGraph = pickle.load(open(f"pickles/asGraph-{asn}.pickle",'rb'))
#     avgs,counter,ctr3,hijskip,origskip = performHijack(asGraph,asn)
    
#     storeScores(avgs,asn,asGraph)
#     countData(counter,ctr3,hijskip,origskip,asGraph)