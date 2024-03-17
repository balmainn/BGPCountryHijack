import pickle 
import os 
import networkx
def readfile(file):
    lines = []
    with open(file,'r')as f: 
        f.readline()
        for line in f.readlines():
            # print(line)
            lines.append(line)

    info = {}
    for line in lines:
        parts = line.split(',')
        # print(line)
        #hijackerASN	AVG	     success   partial	failure	linkLevel direct neighbors
        info[parts[0]]={"average":parts[1],"success":parts[2],
                        "partial":parts[3],"failure":parts[4],
                        "linkLevel":parts[5],"neighbors":parts[6]}

    return info

def searchPotentialVictims(asGraph:networkx.Graph,originASOfP,shortestPathsToP,hijackerASN):
    #victims can be both a lv2 node and a lv3 node. 
    #this is not a problem as the link level determines what 'neighbor level' it is wrt ASN0
    print("searching potential victms")
    fullyHijackableCounter = 0
    partiallyHijackableCounter = 0
    notHijackableCounter = 0
    count = 0
    fullyHijackableCounter = 0
    partiallyHijackableCounter= 0
    notHijackableCounter= 0

    for potentialVictimASN in asGraph.nodes:
        potentialVictimASNData = asGraph.nodes.get(potentialVictimASN)
        
        # if count >=10:
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
        count +=1
        # print('victim', potentialVictimASNData)
        potentialVictimPathToP = shortestPathsToP[potentialVictimASN]
        # victimPathToHijacker = networkx.shortest_path(asGraph,source=potentialVictimASN, target=hijackerASN)
        victimPathToHijacker = networkx.shortest_path(asGraph,source=hijackerASN, target=potentialVictimASN)
        
        lenVicToP = len(potentialVictimPathToP)
        lenVicToHij = len(victimPathToHijacker)
        # print("path to p",potentialVictimPathToP, lenVicToP)
        # print("victim to hij",victimPathToHijacker, lenVicToHij)
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
    return count,fullyHijackableCounter, partiallyHijackableCounter, notHijackableCounter

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

def performHijack(asGraph,originASOfP):
    #actually run H on N                 
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
        #we dont hijack lv 3 just continue 
        # if counter >=MAXNODES:
        #     break
        if hijackerASNData['linkLevel'] >=3:
            print("break lv 3")
            hijskip +=1
            continue
        
        # print("hijacker", hijackerASN,hijackerASNData)
        
        
        # print(type(hijackerASNData['linkLevel']))
        # break
        
        # if hijackerASN in allLv3Neighbors:
        #     continue
        if hijackerASN == originASOfP:
            print("node is ASNP!")
            origskip+=1
            score=100 
            # print(shortestPathsToP,type(shortestPathsToP))
            continue
        ct, fullyHijackableCounter, partiallyHijackableCounter, notHijackableCounter =searchPotentialVictims(asGraph,originASOfP,shortestPathsToP,hijackerASN)
        ctr3+=ct
        
        # weights = 100 + 50 + 0 
        # weightSum = 150
        # average =  (100*fullyHijackableCounter + 50*partiallyHijackableCounter)/150
        #i dont believe this average, should probably be recalculated
        average =  (100*fullyHijackableCounter + 50*partiallyHijackableCounter)/(fullyHijackableCounter+partiallyHijackableCounter+notHijackableCounter)
        avgs[hijackerASN] = (average,fullyHijackableCounter,partiallyHijackableCounter,notHijackableCounter)

        counter +=1

    return avgs,counter,ctr3,hijskip,origskip 

def storeScores(avgs,originP,asGraph:networkx.Graph):
    
    with open(f"test-hijackingScores-{originP}.csv","w") as f: 
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

# files = os.listdir('pickles/')
# for file in files: 
#     if file.startswith('asGraph'):
#         asGraph = pickle.load(open('pickles/'+file,'rb'))
#         remove = [node for node, degree in asGraph.degree() if degree <= 1]
#         asGraph.remove_nodes_from(remove)
#         print(file, "has ", len(asGraph.nodes))


import random
from datetime import datetime
def extractData(info,x,y,colors):
    #(r,g,b,a)
    random.seed(datetime.now().timestamp())
    r = random.randint(0,100)
    value = 1#(100-r)/100
    
    colorSuccess = (0, value, 0, 1)
    
    colorPartial = (0, 0, value, 1)
    
    colorFail    = (value, 0, 0, 1)
    for hijackerASN in info:
        
        neighbors = int(info[hijackerASN]['neighbors'])
        success = int(info[hijackerASN]['success'])
        partial = int(info[hijackerASN]['partial'])
        failure = int(info[hijackerASN]['failure'])
        # print(f"({x1},{y1})")
        # coords.append((x1,y1))
        x.append(neighbors)
        y.append(success)
        colors.append(colorSuccess)
        x.append(neighbors)
        y.append(partial)
        colors.append(colorPartial)
        x.append(neighbors)
        y.append(failure)
        colors.append(colorFail)
    
    return x,y,colors
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
def countData(asGraph:networkx.Graph):
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
    # print("lv1 ", lv1, "lv2,",lv2, "lv3, ",lv3, "sum ",lv1+lv2+lv3)
    return lv1, lv2, lv3

asns = ['3582','11816','23724','198949','199362','264645']
#199362 this one is big 
for asn in asns:
    asGraph = pickle.load(open('pickles/asGraph-'+asn+'.pickle','rb'))
    avgs,counter,ctr3,hijskip,origskip  =performHijack(asGraph,asn)
    storeScores(avgs,asn,asGraph)
    # prev = len(asGraph.nodes)
    # alv1,alv2,alv3 = countData(asGraph)
    # remove = [node for node, degree in asGraph.degree() if degree <= 1]
    # asGraph.remove_nodes_from(remove)
    # blv1,blv2,blv3 = countData(asGraph)
    # print(asn,'graph was ',prev,' is now ',len(asGraph.nodes))
    # print(alv1, blv1, '|',alv2, blv2, '|',alv3, blv3)
    # for node in asGraph.nodes:

        # shortestPathsToP = networkx.shortest_path(asGraph,target=originASOfP)
        # victimPathToHijacker = networkx.shortest_path(asGraph,source=potentialVictimASN, target=hijackerASN)
    # avgs,counter,ctr3,hijskip,origskip = performHijack(asGraph,asn)
    # lv1,lv2,lv3 = countData(counter,ctr3,hijskip,origskip,asGraph)
    

# import matplotlib.pyplot as plt
# count=1
# files = os.listdir()
# datafiles = []
# for file in files:
#     if file.startswith('hijackingScores-') and file.endswith('.csv'):
#         print(file)
#         datafiles.append(file)
# # for file in datafiles:
    
def getNeighbor(asn,query_time):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    """

    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    if os.path.exists(f'pickles/neighbors/{asn}-{safeTime}'):
        neighbors = pickle.load(open(f'pickles/neighbors/{asn}-{safeTime}','rb'))
        return neighbors
    
import matplotlib.pyplot as plt
queryTime = "2024-03-01T09:00:00"
count = 1

for asn in asns: 
    file = 'test-hijackingScores-'+asn+'.csv'
    plt.subplot(3,2,count)

    x = []
    y = []
    coords = []
    colors = []
    info = {}
    info = readfile(file)
    x,y,colors = extractData(info,x,y,colors)
    a = file.find('-')
    b = file.find('.')
    neighbors = getNeighbor(asn,queryTime)
    title = 'AS '+file[a+1:b]+ ' ' + str(len(neighbors))

    plt.title(title)
    plt.scatter(x,y,c=colors)
    plt.axvline(3,0,10,c='red')
    plt.axvline(1,0,10,c='blue')
    plt.axvline(10,0,10,c='green')
    plt.grid()
    # print(len(x))
    count+=1
    # plt.show()
    # ax.scatter(x,y,c=colors)

plt.show()    


# for file in datafiles: 
#     # file = 'test-hijackingScores-'+asn+'.csv'
#     plt.subplot(3,2,count)

#     x = []
#     y = []
#     coords = []
#     colors = []
#     info = {}
#     info = readfile(file)
#     x,y,colors = extractData(info,x,y,colors)
#     a = file.find('-')
#     b = file.find('.')
#     title = 'AS '+file[a+1:b]

#     plt.title(title)
#     plt.scatter(x,y,c=colors)
#     plt.grid()
#     # print(len(x))
#     count+=1
#     # plt.show()
#     # ax.scatter(x,y,c=colors)

# plt.show()    