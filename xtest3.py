import bgpkit
from datetime import datetime, timedelta
from multiprocessing import Pool
import policies
import pickle
import os
#collector = 'route-views.gixa'
# collector = 'route-views.isc'


def parseFile(brokerItem):
    filters = {'type':'announce'}
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser

def parseFileWithParams(brokerItem,prefix,ribPeer_asn):
    filters = {'type':'announce','prefix':prefix,'peer_asn':str(ribPeer_asn)}
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser

def getNewTimes(tStart,tEnd):
    print("old times: ",tStart,tEnd)
    fmt = "%Y-%m-%dT%H:%M:%S"
    tDelta = 15
    dtStart = datetime.strptime(tStart,fmt)
    dtStart = dtStart-timedelta(minutes=tDelta)
    tEnd = tStart
    tStart = dtStart.strftime(fmt)
    print("NEW times: ",tStart,tEnd)
    return tStart,tEnd
#for routeViews, i can probably just use BGP Updates
def asPathSplit(Dict):
    asPath = Dict.get('as_path', '')  # get the as_path or an empty string if not present
    
    if asPath:  # check if as_path is not empty
        if '{' in asPath: #handle multihome
            a = asPath.split(',')
            pathLen = a[0].replace('{','').replace('}','').split(' ')
            return pathLen
        else:
            return asPath.split(' ')  # split the as_path by spaces and add to the list
    else:
        print('AS PATH NONE?')
        print(asPath)
        return None
    
def findWinner(ribUpdate,update):
    # print('finding winner?')#,ribUpdate,update)
    
    ribPath = asPathSplit(ribUpdate)
    updatePath = asPathSplit(update)
    
    if ribPath  == None or updatePath == None:
        print("PATH IS NONE")
        # print(updatePath, ribPath)
        print(ribUpdate,update)
        return None
    # print(ribPath,updatePath)

    if len(updatePath)!=len(ribPath):
        return None
    # if len(ribPath) == 1:
    #     checkRib = ribPath[0]
    # if len(updatePath)==1:
    #     checkUpdate = updatePath[0]
    try: #probably slightly more expensive than two ifs?
        checkRib = ribPath[1]    
        checkUpdate = updatePath[1]
    except:
        checkRib = ribPath[0]    
        checkUpdate = updatePath[0]

    if checkRib == checkUpdate:
        # print("no winner")
        return None #they're the same so no winner
    else:
        # print("WINNER!")
        if ribPath[0] == updatePath[0]:
            return ({'ribEQ':ribPath[0],'winner':(ribPath[1], updatePath[1])})
        else:
            return ({'rib':ribPath[0],'update':updatePath[0],'winner':(ribPath[1], updatePath[1])})

def storeTestData(dataStore,tid,collector,shouldPrint=True):
    filepath = f'pickles/test/findPrefixes-c{collector}c-{tid}-0'
    if len(dataStore) > 0:
       if shouldPrint:
        print(f'tid {tid} storing {len(dataStore)} results!')
        if os.path.exists(filepath):
            dashLoc= filepath.rfind('-')
            fileNum = int(filepath[dashLoc+1:].strip()) +1
            filepath = f'pickles/test/findPrefixes-c{collector}c-{tid}-{fileNum}'
        pickle.dump(dataStore,open(filepath,'wb'))
    else:
        pass
        #print(f"{tid}NO DATA TO STORE")


    
        # print(f'tid {tid} storing results in!',filepath,len(results))
    #find the next available filepath
def superMagicFunctionOfHopefulDoomIG(initialRib,updateBrokerItem,tid):
    # j = 1
    # for item in initialRib:
        col = initialRib.collector_id
        ribParser = bgpkit.Parser(url=initialRib.url,cache_dir="cache") 
        print(f"{tid} working on inital rib its about {(initialRib.rough_size)} big")
        
        # seen = set()
        #6835928
        i = 1
        updatesComparison = {}
        for ribElem in ribParser:
            i+=1
            if i % 100000==0:
                print(f"{tid}-{col} done {i}/{initialRib.rough_size}")
            ribPrefix = ribElem['prefix']
            # cidr =ribPrefix.split('/')[1]
            # if int(cidr) < 20:
            #     continue
            ribPeer_asn = ribElem['peer_asn']
            ribPeerIp= ribElem['peer_ip']
            #ribPath = ribElem['as_path']
            # if (ribPrefix, ribPeer_asn) in seen:
            #     print(f"{tid} seen {len(seen)} things")
            #     continue
            # else:
            #     seen.add((ribPrefix,ribPeer_asn))
            #semi-preparse for the peer_asn and prefix we want
            parser = parseFileWithParams(updateBrokerItem,ribPrefix,ribPeer_asn)
            # print(f'{tid}-time for a new rib elem!')
            
            # print(parser,ribElem)

            for updateElem in parser:
            
                # exit(0)
                updatePrefix = updateElem['prefix']
                updatePeer_asn = updateElem['peer_asn']
                updatePeerIp= updateElem['peer_ip']
                updatePath = updateElem['as_path']
                if ribPrefix == updatePrefix and updatePeerIp ==ribPeerIp:

                    winner = findWinner(ribElem,updateElem)
                    if winner != None:
                        # for _ in range(3):
                        print(f"~{tid}~~~WINNER~~~")
                        # print(ribElem,updateElem)
                        # exit(0)
                        try:
                            #FOR TESTING ONLY REMOVE OR FIND A BETTER THING LATER
                            # found = False
                            # for alreadyFound in updatesComparison[updatePrefix]:
                            #     if winner == alreadyFound[2]:
                            #         found = True
                            #         print("already found =(")
                            #         break
                            # if not found:
                                updatesComparison[updatePrefix].append((ribElem,updateElem,winner))
                                #policies.allThumbs()
                        except Exception as e:
                            print("exception in update comparison: ",e)
                            updatesComparison[updatePrefix] = []
                            updatesComparison[updatePrefix].append((ribElem,updateElem,winner))
                # print(updateElem)
        storeTestData(updatesComparison,tid,col)
        with open('fileDone.txt','a') as f:
            f.write(f"{tid}, {col}, just finished at {datetime.now()}\n")

masterPeers = policies.getMasterPeers()
broker = bgpkit.Broker(page_size=1000)
dataUrls = []
tStart="2024-03-31T00:00:00" #known time do not change
tEnd="2024-03-31T02:00:00"   #known time do not change
initialRib = broker.query(ts_start=tStart, ts_end=tEnd,data_type='rib')

collectors = []
for init in initialRib:
    ribCollector = init.collector_id
    # print('found rib for', ribCollector)
    for collector in masterPeers:
        if collector in ribCollector:
            numPeers = len(masterPeers[collector]['peers'])
            # if 'rrc' in collector:
                # print(collector, len(masterPeers[collector]['peers']))                
            if numPeers < 10:
                # print(collector, len(masterPeers[collector]['peers']))
                collectors.append(init)
#    if collector in masterPeers.keys()
    
# print(collectors,len(collectors))
print('aight theres ',len(collectors),' todo so here we go')
# for c in collectors:
#     print(c)
# exit(0)
def findUpdatesListMT(collector_id):
    tStart="2023-06-30T00:00:00"
    tEnd="2023-06-30T01:00:00"
    updatesList = []
    updatesList = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector_id,data_type='update')
    print("found ",len(updatesList),'for ',collector_id)
cIDs = []
zubat = []
tid = 0
for ribCollector in collectors:
    collectorId = ribCollector.collector_id

    
    # from rib: check if peer matches update
    #   check path length between rib and update 
    #     check if 1st element (not zeroth) are different
    #       if so, asn in the rib must be > asn in the rib update

    prefixes = {}
    num = 0

    cnt = 1
    updatesComparison = {}
    tStart="2023-06-30T00:00:00"
    tEnd="2023-06-30T0:30:00"
    print(f"querying for {collectorId} updates")
    updatesList = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collectorId,data_type='update')
    
    
    print('updates and ribs list', len(updatesList),len(initialRib))
    if len(updatesList) ==0:
        print("no updates found for ",ribCollector)
        continue
    # continue
    # exit(0)
    # print('initial rib lsit', len(initialRib))
    
    #parser = parseFile(initialRib[0])
    elems = 0
    
    for updateFile in updatesList:
        # parser = parseFile(updateFile)
        # elems = 0
        # for elem in parser:
        #     elems+=1
        # print(tid, 'has ',elems, 'elements')
        tid+=1
        zubat.append((ribCollector,updateFile,tid))
    
print(len(zubat))
#superMagicFunctionOfHopefulDoomIG(zubat[2][0],zubat[2][1],zubat[2][2])
#for zubat in zubats:
#exit(0)
pool = Pool(processes=10)
pool.starmap(superMagicFunctionOfHopefulDoomIG,zubat)
pool.close()
print("DONE")
#for zubat in zubats:
    # numProcesses = 10
    # if len(zubat) < 10:
    #     numProcesses = len(zubat)
    # print('starting pool with', numProcesses)
    # for t in zubat:
    #     print(t[0],t[1],t[2])
    # continue
    # exit(0)
    # superMagicFunctionOfHopefulDoomIG(zubat[1][0],zubat[1][1],zubat[1][2])
    # exit(0)
    
    
    #tStart,tEnd = getNewTimes(tStart,tEnd)
# zubat[0]

#to make this faster (maybe)
#pull out ips from the rib 
#use parser to filter both the rib and updates to only that ip
#should simplify some things...?

#superMagicFunctionOfHopefulDoomIG(zubat[0][0],zubat[0][1],zubat[0][2])

    
