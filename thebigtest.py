import bgpkit
from datetime import datetime, timedelta
#collector = 'route-views.gixa'
# collector = 'route-views.isc'
collector = 'rrc06'
broker = bgpkit.Broker(page_size=1000)
dataUrls = []
tStart="2024-03-31T00:00:00"
tEnd="2024-03-31T02:00:00"

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
import pickle
import os
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
        print(f"{tid}NO DATA TO STORE")


    
        # print(f'tid {tid} storing results in!',filepath,len(results))
    #find the next available filepath
    

initialRib = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector,data_type='rib')
# prefixes = set()
cnt = 10

# from rib: check if peer matches update
#   check path length between rib and update 
#     check if 1st element (not zeroth) are different
#       if so, asn in the rib must be > asn in the rib update
import policies
prefixes = {}
num = 0

cnt = 1
updatesComparison = {}
tStart="2023-09-30T00:00:00"
#tEnd="2023-10-01T00:00:00"
tEnd="2023-09-30T08:00:00"
updatesList = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector,data_type='update')
zubat = []
tid = 0
for updateFile in updatesList:
    tid+=1
    zubat.append((initialRib,updateFile,tid))
zubat[0]

#to make this faster (maybe)
#pull out ips from the rib 
#use parser to filter both the rib and updates to only that ip
#should simplify some things...?
def superMagicFunctionOfHopefulDoomIG(initialRib,updateBrokerItem,tid):
    i = 1
    for item in initialRib:
        updatesComparison = {}
        ribParser = bgpkit.Parser(url=item.url,cache_dir="cache") 
        print(f"{tid} working on updates {i}/{len(updatesList)}")
        
        seen = set()
        #6835928
        for ribElem in ribParser:
            i+=1
            if i % 100000:
                print(f"{tid} done {i}/6,835,928")
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
            
            for updateElem in parser:
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
        storeTestData(updatesComparison,tid,collector)

#superMagicFunctionOfHopefulDoomIG(zubat[0][0],zubat[0][1],zubat[0][2])
from multiprocessing import Pool
pool = Pool(processes=10)
pool.starmap(superMagicFunctionOfHopefulDoomIG,zubat)
pool.close()
print("DONE")
    #tStart,tEnd = getNewTimes(tStart,tEnd)
    

#         for elem in parser:


        # prefixes.add(elem['prefix'])
# print(prefixes)
#items = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector,data_type='update')
tStart="2024-03-31T00:00:00"
tEnd="2024-03-31T02:00:00"




#these will be sorted by insertion. 
#when we find a winner, we know what goes on left, and what goes on right. 
#so insert them into the list in that order (empty)
#if one is already in the list, put it on one side of it
#repeat until the list is full (always works for left, dunno what to do about right) 

#actually...
#we have a bunch of sublists, and we merge them together (probably)
#can also just do this manually because this sounds stupid hard...

#     if num > 1000:
        #         exit(0)
        #     num +=1
        #     print(ribElem)
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    # exit(0)
        #     try:
        #         prefixes[ribPrefix] +=1
        #     except:
        #         prefixes[ribPrefix]=0
        #     # print(ribElem)
        # gtp =""
        # gtn = 0
        # for pre in prefixes:
        #     print(prefixes[pre])
        #     if gtn < prefixes[pre]:
        #         gtn = prefixes[pre]
        #         gtp = pre
        # print(gtp,gtn)
        # exit(0)