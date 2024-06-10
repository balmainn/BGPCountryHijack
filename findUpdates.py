import pickle
import gzip
import os 
import policies
import bgpkit


def parseFileWithParams(brokerItem,prefix,ribPeer_asn):
    #print('parsing ',brokerItem)
    #filters = {'type':'announce','prefix':prefix,'peer_asn':str(ribPeer_asn)}   
    filters = {'type':'announce','peer_asn':str(ribPeer_asn)}   
    # filters = {'type':'announce','peer_ip':'198.32.160.170','peer_asn':str(ribPeer_asn)}   
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser
def parseFile(brokerItem):
    print('parsing ',brokerItem)
    filters = {'type':'announce'}
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser
def addUpdateToDict(storeDict,update):
    neighbor  = policies.findNeighborInUpdate(update)
    prefix = update['prefix']
    #prefix: {neighbor:[update]} #if theres multiple updates for a specific neighbor, then its probably b/c of route flapping
    try:
        neighborLoc = storeDict[prefix]
    except Exception as e:
        # print('exception second loc ',e)
        storeDict[prefix] = {}
        neighborLoc = storeDict[prefix]
    # print(peerIpLoc)
    try:
        updateLoc=neighborLoc[neighbor]
    except Exception as e:
        # print('exception in 3',e)
        neighborLoc[neighbor] = []
        updateLoc=neighborLoc[neighbor]
    
    if len(updateLoc)==0:
        updateLoc.append(update)
        return
    # print('checking diffs')
    replaceValue =55555
    replaceLocation = 55555
    #this always gets us smallest location
    for i,previousUpdate in enumerate(updateLoc):
        value = policies.findTimeDiff(previousUpdate,update)
        if replaceValue > value:
            replaceLocation = i 
            replaceValue = value
    #at this point we know we're in the right place
    #so just do the ifs and replace or append
    # print()
    if replaceValue <=180: #replace
        updateLoc[replaceLocation] = update
    if replaceValue > 180: #180 seconds is 3 minutes
        
        updateLoc.append(update)
            
            
    # updateLoc.append('a')
def getStoredDict(filepath):
    """get the stored Dict, unless it doesnt exist then return empty dict"""
    if os.path.exists(filepath):
        return pickle.load(open(filepath),'wb')
    else:
        return {}

#dict in form of u(P,t,n,update)
#init test collectors[10:11]:
from memory_profiler import profile
@profile
def loadParse(parser):
    elems = parser.parse_all()
    return elems
# route-views6
def printStoreDict(storeDict):
    print('ips: ',len(storeDict.keys()))
    m = 0
    n = 0
    for prefix in storeDict:
        if m < len(storeDict[prefix].keys()):
            m = len(storeDict[prefix].keys())
            for neighbor in storeDict[prefix]:
                if n < len(storeDict[prefix][neighbor]):
                    n = len(storeDict[prefix][neighbor])
    print("max neighs",m)
    print('max updates',n)
        # print(prefix, 'has neighbors',storeDict[prefix].keys())
        # for neighbor in storeDict[prefix]:
            # print('neighbor updates ',len(storeDict[prefix][neighbor]))
def cleanDict(collector_id,collectorPeer,storeDict):
    print("cleaning dict for",collector_id,' ',collectorPeer)
    prefsToPop = set()
    # print(len(storeDict))
    for prefix in storeDict:
        numNeighbors = len(storeDict[prefix].keys())
        if numNeighbors <2:
            prefsToPop.add(prefix)
            continue
    for prefix in prefsToPop:    
        storeDict.pop(prefix)

def storeParsedData(storeDict,collector_id,collectorPeer):
    if len(storeDict) == 0:
        return
    cleanDict(collector_id,collectorPeer,storeDict) #remove prefixes that only have 1 elem in it 
    
    print('storing results',len(storeDict),collector_id,collectorPeer)
    filepath = f'pickles/processedUpdates/{collector_id}-{collectorPeer}.pickle'
    pickle.dump(storeDict,open(filepath,'wb'))
    storeNeighborVersion(storeDict,collector_id,collectorPeer) #store the neighbor version as well

def getAllNeighbors(storeDict):
    allNeighbors = set()
    for prefix in storeDict:
        for neighbor in storeDict[prefix].keys():
            allNeighbors.add(neighbor)
    return allNeighbors
def storeNeighborVersion(prefixNeighborsDict,collector_id,collectorPeer):
    allNeighbors = getAllNeighbors(prefixNeighborsDict)
    neighborUpdates ={}
    for neighbor in list(allNeighbors):
        for prefix in prefixNeighborsDict:
            if neighbor not in prefixNeighborsDict[prefix].keys():
                continue
            updates = prefixNeighborsDict[prefix][neighbor]
            if neighbor not in neighborUpdates.keys():
                neighborUpdates[neighbor] = {}
                if prefix not in neighborUpdates[neighbor].keys():
                    neighborUpdates[neighbor][prefix] = []
            neighborUpdates[neighbor][prefix]= updates
    filepath = f'pickles/collectorPeerASNeighbors/{collector_id}-{collectorPeer}.pickle'
    pickle.dump(neighborUpdates,open(filepath,'wb'))
    
collectors = policies.getAllCollectors()
masterPeers = policies.getMasterPeers()
tStart="2024-03-31T00:00:00"
tEnd="2024-03-31T00:15:00"
broker = bgpkit.Broker(page_size=1000)

riblist = []
updatesList = []
# print(len(collectors))
# exit(0)
#@profile
def runCollector(collector_id):
    updateBrokerItems = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector_id,data_type='update')
    if len (updateBrokerItems)==0:
        #some route-views collector naming schemes are depricated (amsix.ams is now route-views.amsix for example)
        #but it they still exist under the old convention for certain time frames. 
            return
    peers = list(masterPeers[collector_id]['peers']) #test limit TODO
    
    for i,collectorPeer in enumerate (peers):
        print(f"working on collectorPeer {i}/{len(peers)}")
        storeDict = {}#getStoredDict('somefilepath') #TODO
        
        for uBrokerItem in updateBrokerItems:
            parser = parseFileWithParams(uBrokerItem,None,collectorPeer)
            for elem in parser:
                # print(elem)
                addUpdateToDict(storeDict,elem)
            #print('done adding prefixes!')
            #printStoreDict(storeDict)
        
        storeParsedData(storeDict,collector_id,collectorPeer)
        storeDict = {}
        # store here for specific collector peer
    print("NEW COLLECTOR")
from multiprocessing import Pool
pool = Pool(processes=10)
pool.map(runCollector,collectors)
pool.close()
pool.join()

policies.allThumbs()

    # if 'route-views6' not in collector_id:
    #     continue
    # print(collector_id)
    
            # for prefix in storeDict:
            #     # print(prefix,storeDict[prefix])
            #     if len(storeDict[prefix])>1:
            #         test = []
            #         for neighbor in storeDict[prefix]:
            #             print(prefix,neighbor)
            #             updates = storeDict[prefix][neighbor]
            #             if len(updates)>2:
            #                 # print(">2")
            #                 # for update in updates:
                            
            #                 #     found = True
            #                 print(storeDict[prefix].keys())
            #                 print('27986')
            #                 for update in storeDict[prefix]['27986']:
            #                     # print("~~~~")
            #                     # print(update)
            #                     test.append((27986,update['timestamp']))
            #                 print('14259')
            #                 for update in storeDict[prefix]['14259']:
            #                     # print("~~~~")
            #                     # print(update)
            #                     test.append((14259,update['timestamp']))
            #                 for t in test:
            #                     print(t)
            #                 exit(0)
                 
   # exit(0)
            # store here for specific collector peer