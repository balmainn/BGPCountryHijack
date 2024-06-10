import pickle 
import os 
import networkx
import gzip 
import policies
import bgpkit
somedir = 'pickles/processedUpdates/'
file = 'route-views.chile-27678.pickle'
# file = 'route-views.linx-714.pickle'
# files = os.listdir(somedir)
#for file in files:
prefixNeighborsDict = pickle.load(open(somedir+file,'rb'))
collector = 'route-views.chile'
peer=27678
ribFiles = []
ribsDir = 'pickles/ribData/'
files = os.listdir(ribsDir)
for file in files:
    if collector not in file:
        continue
    ribFiles.append(file)
print(len(ribFiles))

def getAllNeighbors(storeDict):
    allNeighbors = set()
    for prefix in storeDict:
        for neighbor in storeDict[prefix].keys():
            allNeighbors.add(neighbor)
    return allNeighbors
allNeighbors = getAllNeighbors(prefixNeighborsDict)

from collections import OrderedDict
# o= OrderedDict(prefixNeighborsDict)
o= OrderedDict(sorted(prefixNeighborsDict.items(),key=lambda x: len(x[1]),reverse=True))
prefixes = set()# []
i = 0
# maxNumprefs = 10
for prefix in prefixNeighborsDict:
    print(prefix, len(o[prefix]))
    prefixes.add(prefix)
    i+=1
    # if i >=maxNumprefs:
    #     break
# print("LOADING RIB")
# with gzip.open(ribsDir+ribFiles[1],'rb') as f:
#     ribData = pickle.load(f)
# for prefix in prefixes:
# prefix= prefixes[0]
updatesToConsider = []

def findUpdateInRib(ribData,peerASN,peerIP,regASN):
    try:
        updates = ribData[peerASN][peerIP][regASN]
        if len(updates) > 1:
            print("why is there more than 1?")
        return updates
    except Exception as e:
        print("exception ", e)
        print(peerASN,peerIP,regASN)
        return None

broker = bgpkit.Broker(page_size=1000)
def parseFileWithParams(brokerItem,prefix,ribPeer_asn):
    # print('parsing file',brokerItem, brokerItem.rough_size)
    filters = {'type':'announce','prefix':prefix,'peer_asn':str(ribPeer_asn)}
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser
tStart="2024-03-31T12:00:00"
tEnd="2024-03-31T12:00:00"
initialRib = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector,data_type='rib')
print(len(initialRib))
def findPolicyWinner(prefixNeighborsDict,prefix,ribNeighbor,neighborCounts):
    for neighbor in prefixNeighborsDict[prefix]:
        updates = prefixNeighborsDict[prefix][neighbor]     
        for update in updates:
            considerNeighbor = policies.findNeighborInUpdate(update)
            if ribNeighbor == considerNeighbor:
                print(considerNeighbor, "wins!")
                incrementWinner()

def incrementWinCount(ribNeighbor,candidateNeighbors,winCounter):
    for cand in candidateNeighbors:
        if cand == ribNeighbor:
            continue
        winCounter.append((ribNeighbor,cand))
    
def initializeCountingDict(allNeighbors):
    cdict = {}
    d = dict()
    
    secondDict = allNeighbors.copy()
    for neighbor in allNeighbors:
        cdict[neighbor] = {}
        for n2 in secondDict:
            if n2 != neighbor:
                cdict[neighbor][n2]={'wins':0,'losses':0}
                
                 
            else:
                print('skipping',n2,neighbor)
    return cdict
def findNearestUpdate(prefixNeighborsDict,ribNeighbor,prefix,correctUpdate):
    candidateUpdates = prefixNeighborsDict[prefix][ribNeighbor]
    if len(candidateUpdates) ==1:
        return candidateUpdates[0]
    else:#theoretically it SHOULD be the last one, but i'm not sure i trust that.
        return(candidateUpdates[-1])
    for c in candidateUpdates:
        print("~~~~~")
        print(c)
    print("correct update")
    print(correctUpdate)
    exit(0)

countingDict = initializeCountingDict(allNeighbors)
print(allNeighbors)
# print(countingDict)
# for c in countingDict:
#     print(c,countingDict[c])
winCounter = []
# for prefix in prefixes: 

# for i,prefix in enumerate(list(prefixNeighborsDict.keys())[:250]): 
ct = 0
# revPref = list(prefixes).reverse()
# print(revPref)
print(len(prefixes))
from random import shuffle
prefList = list(prefixes)
print(prefList[0])
shuffle(prefList)
print(prefList[0])
# exit(0)
for i,prefix in enumerate(prefList[:250]): 
    if i >251:
        break
    if prefix == None:
        print("why is prefix none?")
        continue
    candidateNeighbors = prefixNeighborsDict[prefix].keys()
    
    correctUpdates = []
    correctUpdate = None
    for ribDict in initialRib:
        #ribDict = initialRib
        
        parser = parseFileWithParams(ribDict,prefix,peer)
        correctUpdate = parser.parse_all()
        if len(correctUpdate) >1:
            print("WHY is there more than one correct update?")
            print(correctUpdate,len(correctUpdate),type(correctUpdate))
            exit(0)
        if len(correctUpdate) ==0:
            break
        correctUpdate = correctUpdate[0]
        ribNeighbor = policies.findNeighborInUpdate(correctUpdate)
        if ribNeighbor in candidateNeighbors:
            # print(ribNeighbor,'wins!',prefix)
            
            findNearestUpdate(prefixNeighborsDict,ribNeighbor,prefix,correctUpdate)
            incrementWinCount(ribNeighbor,candidateNeighbors,winCounter)
            for cand in candidateNeighbors:
                if cand != ribNeighbor:
                    countingDict[ribNeighbor][cand]['wins']+=1
                    countingDict[cand][ribNeighbor]['losses']+=1
        else: #i think this implies we just didnt see the update for this, so lets just assume that
            print("why is there no winner?")
            print(correctUpdate,ribNeighbor,candidateNeighbors)
            for cand in candidateNeighbors:
                countingDict[ribNeighbor][cand]['wins']+=1
                countingDict[cand][ribNeighbor]['losses']+=1
            # exit(0)
    if i % 50 ==0:
        print("~~~~~~~~")
        for n in countingDict:
            print(n,countingDict[n])
dgraph = networkx.DiGraph()

# for c in winCounter:
#     dgraph.add_node(c[0])
#     dgraph.add_node(c[1])
#     dgraph.add_edge(c[0],c[1])
# print(len(c))
# from matplotlib import pyplot
# networkx.draw(dgraph)
# pyplot.show()

    #     if correctUpdate != None and len(correctUpdate)>0:
    #         if not isinstance(correctUpdate,dict):
    #             print("why is this not a dictionary?")
    #             print(len(correctUpdate),type(correctUpdate))
    #             if len(correctUpdate) >1:
    #                 print("WHY is there more than one?")
    #                 print(correctUpdate,len(correctUpdate),type(correctUpdate))
    #                 exit(0)
    #             for correct in correctUpdate:
    #                 correctUpdates.append(correct)
    #         else:
    #             correctUpdates.append(correctUpdate)
    # for correctUpdate in correctUpdates:
    #     ribNeighbor = policies.findNeighborInUpdate(correctUpdate)
    #     findPolicyWinner(prefixNeighborsDict,prefix,ribNeighbor,neighborCounts)
        
    # updatesToConsider.append(updates)

# ncounts = {}
# for n in allNeighbors:


# for updates in updatesToConsider:
#     for update in updates:
#         peerASN = update['peer_asn']
#         peerIP =  update['peer_ip']
#         prefix = update['prefix']
        # regASN = policies.splitASPath(update)[-1] #ignoring multihome because its always the last one that sent the update
        # ribUpdates = findUpdateInRib(ribData,int(peerASN),peerIP,int(regASN))
        # considerNeighbor = policies.findNeighborInUpdate(update)
        # if ribUpdates==None:
        #     continue
        # #find the specific prefix
        # for ribUpdate in ribUpdates:
        #     riPeerASN = ribUpdate['peer_asn']
        #     ribPeerIP =  ribUpdate['peer_ip']
        #     ribPrefix = ribUpdate['prefix']
        #     ribNeighbor = policies.findNeighborInUpdate(ribUpdate)
            
        #     if ribPrefix == prefix:
        #         print("~~~~~~~~~~~~~~~")
        #         print(ribUpdate,considerNeighbor,ribNeighbor)
        #         if considerNeighbor == ribNeighbor:              
        #             print(ribNeighbor, "WINS!")
    
    
    
    
    
    # exit(0)
        # print("~~~~~~~~~")
        # print(u)
# print(len(allNeighbors),len(prefixes))
    # for n in o[prefix]:
    #     print(len(o[prefix][n]))
# print("LOADING RIB")

# for peerASN in ribData:
#     print(peerASN)
#     # exit(0)
#     if peerASN != peer:
#         continue
#     for peerIP in ribData[peerASN]:
#         for regASN in ribData[peerASN][peerIP]:
#             for update in ribData[peerASN][peerIP][regASN]:
#                 prefix = update['prefix']
#                 neighbor = policies.findNeighborInUpdate(update)
#                 try:
#                     neighborUpdates = prefixNeighborsDict[prefix][neighbor]
#                     print(len(neighborUpdates),prefix,neighbor)
#                     exit(0)
#                 except:
#                     pass
