import bgpkit 
import arrow 
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
def createBroker(page_size = 1000):
    return bgpkit.Broker(page_size=page_size)
def queryBroker(broker:bgpkit.Broker,tsStart,tsEnd,collector,data_type):
    """tsStart, tsEnd: timestamp for MRT file, UNIX timestamp format
    data_type: rib or update"""
    return broker.query(ts_start=tsStart,ts_end=tsEnd,collector_id=collector,data_type=data_type)

def parseFile(brokerItem):
    print('parsing file',brokerItem, brokerItem.rough_size)
    filters = {'type':'announce'}
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir=cacheDir,filters=filters)      
    return parser
"""     prefix_super: exact prefix and its super prefixes
        prefix_sub: exact prefix and its sub prefixes
        prefix_super_sub: exact prefix and its super and sub prefixes
"""
def addPrefixToFilter(filters,prefix,prefix_super=False,prefix_sub=False,prefix_super_sub = False):
    """options are mutually exclusive"""
    numOptions = 0
    if prefix_super:
        filters['prefix_super']=prefix
        numOptions+=1
    if prefix_sub:
        filters['prefix_sub']=prefix
        numOptions+=1
    if prefix_super_sub:
        filters['prefix_super_sub'] = prefix
        numOptions+=1
    if numOptions > 1:
        raise Exception("Cant add more than one sub/super prefix")
    if numOptions ==0:
        filters['prefix'] =prefix
    return filters

def addFiltersNotPrefix(origin_asn=False,peer_ip =False, peer_ips=False,peer_asn=False,type='announce',ts_start=False,ts_end=False,as_path=False):
    """prefix is handled seperately because there are more options"""
    filters = {}
    if origin_asn:
        filters['origin_asn'] = origin_asn
    if peer_ip:
        filters['peer_ip'] = peer_ip
    if peer_ips:
        filters['peer_ips'] = peer_ips
    if peer_asn:
        filters['peer_asn'] = peer_asn
    if type:
        if type != 'all':
            filters['type'] = type
    if ts_start:
        filters['ts_start'] = ts_start
    if ts_end:
        filters['ts_end'] = ts_end
    if as_path:
        
        if isinstance(as_path,list) or isinstance(as_path,set):
            as_pathStr = ""
            for asn in as_path:
                as_pathStr = as_pathStr + asn +','
            as_pathStr =as_pathStr[:-1] #remove extra comma
            filters['as_path'] = as_pathStr
        else:
            filters['as_path'] = as_path
    
    return filters

def splitASPathFromString(asPath):
    if asPath:  # check if as_path is not empty
        if '{' in asPath: #handle multihome
            a = asPath.split(',')
            return a[0].replace('{','').replace('}','').split(' ')
            
        else:
            return asPath.split(' ')  # split the as_path by spaces and add to the list
    else:
        print('AS PATH NONE?')
        print(asPath)
        return None
    
def splitASPathFromUpdate(update):
    if len(update)==0:
        return None
    asPath = update['as_path']
    if asPath == None:
        return []
    originAS = update['origin_asns']
    #to handle multihome, 
    # just replace the last element in the list with an origin
    if '{' in asPath: 
            a = asPath.split(' ')
            a.append(originAS[0])
            return a
    else:
        return asPath.split(' ')
    #old version it "should" be fine?
    asPath = update['as_path']
    splitPath = splitASPathFromString(asPath)
    if splitPath == None:
        print(update)
        return None
        #exit (1)
    return splitPath
    


def parseFileWithParams(brokerItem,params):
    print('parsing file',brokerItem, brokerItem.rough_size)
    #params['type']='announce'
    try:
        parser = bgpkit.Parser(url=brokerItem.url,cache_dir=cacheDir,filters=params)      
    except Exception as e:
        print('exception while parsing params ',e.with_traceback())
        with open('parserErrors.txt','a') as f:
            f.write(str(brokerItem))
            f.write(str(params))
            f.write('\n')
        exit(0)
    return parser

# def getNeighborFromUpdate(update):
#     as_path = splitASPathFromUpdate(update)
#     if as_path == None:
#         print("cannot get neighbor for a nonetype path")
#         return None
#     if len(as_path) > 1:
#         return as_path[1]
#     else:
#         print("this is the origin!")
#         return as_path[0]
def createFullPrefList(inequalities):
    """given a list of inequalities e.g.[(a,>,b), (b,>,c)]
    create and return a dict of all the inequalities
    using the example 
    {a: > [b,c],=:[],<[],
     b: > [c],=:[],<[a],
     c: > [],=:[],<[b,a],
    }
    this function also validates that a full list is possible
    by ensuring that all x are in a[operation] where operation is >,=,<
    if there exists some b not in a[operation] then it hard exits."""
    #print('create full pref list')
    allPrefs = []
    for a,r,b in inequalities:
        res = (a,r,b)
        if res not in allPrefs:
            allPrefs.append(res)
        if r == '>':
            allPrefs.append((b,'<',a))
        if r =='=':
            allPrefs.append((b,'=',a))
        
    someDict = {}
    for a,relation,b in allPrefs:
        if a not in someDict.keys():
            someDict[a] = {'>':[],'<':[],'=':[]}
        if b not in someDict.keys():
            someDict[b] = {'>':[],'<':[],'=':[]}
        # if relation not in someDict[a].keys():
        #     someDict[a][relation] = [] 
        if b not in someDict[a][relation]:
            someDict[a][relation].append(b)
    #validates that we have everything
    allNeighbors = set()
    for a,_,b in allPrefs:
        allNeighbors.add(a)
        allNeighbors.add(b)
    for neighbor in list(allNeighbors):
        secondSet = set()
        secondSet.add(neighbor)
        for op in someDict[neighbor]:
            for b in someDict[neighbor][op]:
                secondSet.add(b)
        if secondSet!= allNeighbors:
            print("sets not eq")
            print(neighbor)
            print(secondSet)
            print(allNeighbors)
            print(allNeighbors-secondSet)
            exit(0)
    return someDict    

def findNeighborInUpdate(update):
    if len(update) ==0:
        return None
    if update['elem_type']=='W':
        #print(update)
        return None
    asns = splitASPathFromUpdate(update)
    unique = asns[0]
    #finds the first non duplicate ASN (the second ASN commonly at index 1 unless theres path duplication))
    for asn in asns:
        if asn != unique:
            return asn
    #implies there is only 1 ASN in the path so just return it (its the origin asn)
    return asns[0] 

import gzip
import pickle
import os
def loadFib(collector,peerASN,peerIP):
    filepath = 'pickles/ribProcessedUpdates/'
    file=f'{collector}-({peerASN},{peerIP}).pickle'
    print('loading FIB',file)
    with gzip.open(filepath+file,'rb') as f:
        fib = pickle.load(f)
    return fib
   
def loadUpdates(collector,peerASN,peerIP,single=True):
    #single updates vs updates that contain route flapping
    if single:
        filepath = 'pickles/processedUpdatesSingle/'
    else:
        #filepath = 'pickles/processedUpdates/'
        filepath = 'pickles/processedUpdatesSingle36hrs/'
    file=f'{collector}-({peerASN},{peerIP}).pickle'
    print('loading updates',file)
    updates = pickle.load(open(filepath+file,'rb'))
    return updates


def getPathLength(update):
    return(len(splitASPathFromUpdate(update)))
#update = {'timestamp': 1711843200.0, 'elem_type': 'A', 'peer_ip': '2001:de9:4000::fc', 'peer_asn': 65534, 'prefix': '2001:678:16::/48', 'next_hop': '2001:de9:4000::f', 'as_path': '6939 12389 45029 42385 {20764,42385,43832}', 'origin_asns': [20764, 42385, 43832], 'origin': 'IGP', 'local_pref': 0, 'med': 0, 'communities': ['0:714', '0:2906', '0:6939', '0:12876', '0:12989', '0:13335', '0:15133', '0:15169', '0:16265', '0:16276', '0:16509', '0:20940', '0:22822', '0:32590', '0:48641', '0:49029'], 'atomic': 'NAG', 'aggr_asn': 45029, 'aggr_ip': '193.232.132.254'}

#getPathLength(update)
def getInfoFromFile(file):
    
    lparen = file.find('(')
    comma = file.find(',')
    rparen = file.find(')')
    peerASN = file[lparen+1:comma]
    peerIP = file[comma+1:rparen]
    collector=file[0:lparen-1]
    return collector,peerASN,peerIP

def getPrefixSet(localPrefVals):
    prefixSet = set()
    for a in localPrefVals:
        # print(a,len(localPrefVals))
        for b in localPrefVals[a]:
            for prefix in localPrefVals[a][b]:
                prefixSet.add(prefix)
    return prefixSet           

def storeParsedData(storeDict,collector_id,collectorPeer,folder,compress=False):
    """pickles and stores storeDict in folder location, 
    uses collector_id and collectorPeer for the filename
    optionally, compress the dict with gzip"""
    if len(storeDict) == 0:
        print('nothing to store!')
        return
    safeCollectorPeerString =  '('+str(collectorPeer[0])+','+collectorPeer[1]+')'
    print(f'storing {len(storeDict)} results for',collector_id,collectorPeer)
    filepath = f'{folder}/{collector_id}-{safeCollectorPeerString}.pickle'
    if compress:
        with gzip.open(filepath,'wb') as f:
            pickle.dump(f)
    else:
        pickle.dump(storeDict,open(filepath,'wb'))
    
    #storeNeighborVersion(storeDict,collector_id,safeCollectorPeerString) #store the neighbor version as well

 
def loadPrefVals(collector,peerASN,peerIP):
    
    filepath = 'pickles/localPrefs/'
    file=f'{collector}-({peerASN},{peerIP}).pickle'
    print('loading pref vals',file)
    updates = pickle.load(open(filepath+file,'rb'))
    return updates

def arbLoad(folder,collector,peerASN,peerIP):
    #filepath = 'pickles/localPrefs/'
    file=f'{collector}-({peerASN},{peerIP}).pickle'
    print('loading someObject',file)
    someObject = pickle.load(open(folder+file,'rb'))
    return someObject

def mergeDicts(dictA:dict,dictB:dict):
    outDict = dictA
    for prefix in dictB:
        if prefix not in outDict.keys():
            outDict[prefix] = {}
        for neighbor in dictB[prefix]:
            if neighbor not in outDict[prefix].keys():
                outDict[prefix][neighbor] = []
            outDict[prefix][neighbor].append(dictB[prefix][neighbor])

def addTime(startTime,daysToAdd=0,hoursToAdd=0,minutesToAdd=0):
    if isinstance(startTime,float):
        startTime = datetime.fromtimestamp(startTime)
    fmt = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.strptime(startTime,fmt)
    dt = dt + timedelta(days=daysToAdd,hours=hoursToAdd,minutes=minutesToAdd)
    newTime = dt.strftime(fmt)
    return newTime

def subtractTime(startTime,days=0,hours=0,minutes=0):
    if isinstance(startTime,float):
        startTime = datetime.fromtimestamp(startTime)
    #print('subtracting from',startTime)
    fmt = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.strptime(startTime,fmt)
    dt = dt - timedelta(days=days,hours=hours,minutes=minutes)
    newTime = dt.strftime(fmt)
    return newTime
def convertTimeToUnix(timestamp):
    #tTime = arrow.get(timestamp).utcfromtimestamp()
    tTime = arrow.get(timestamp).isoformat()
    time = datetime.strptime(tTime,"%Y-%m-%dT%H:%M:%S%z")
    time = time.timestamp()
    #print(time,type(time))
    return time
def convertUpdateToTimestring(update):
    if len(update)==0:
        return None
    return convertUnixToTimeString(update['timestamp'])
import pytz
def convertUnixToTimeString(timestamp):
    """there might be loss of precision here."""
    fmt = "%Y-%m-%dT%H:%M:%S"
    gmt = pytz.timezone('GMT')
    timestamp = datetime.fromtimestamp(timestamp,tz=gmt)
    time = timestamp.strftime(fmt)
    return time

def loadCone():
    """Loads the cone dictionary
    cone[someAS] = [list of ASes in the cone]
    sCone is sorted by the number of ASes in someAS's cone
    """
    cone = pickle.load(open('pickles/asnCone.pickle','rb'))
    sCone = sorted(list(cone.items()), key=lambda a_c: len(a_c[1]),reverse=True)
    return cone,sCone

def loadConfig():
    #no config, just return the current directory
    if not os.path.exists('config.txt'):
        return "pickles/", "cache/"
    #specify custom pickles and cache directory with a config file
    with open('config.txt','r') as f:
        pickledir = f.readline().strip()
        cachedir = f.readline().strip()
    return pickledir, cachedir

global pickleDir
global cacheDir

pickleDir , cacheDir = loadConfig()

import time
from random import uniform
def is_time_between(start_time_str, end_time_str, check_time_str):
    # Define the date-time format
    time_format = "%Y-%m-%dT%H:%M:%S"

    # Convert string times to datetime objects
    start_time = datetime.strptime(start_time_str, time_format)
    end_time = datetime.strptime(end_time_str, time_format)
    check_time = datetime.strptime(check_time_str, time_format)

    # Check if the check_time is between start_time and end_time
    return start_time <= check_time <= end_time

def itemInTimerange(item,startTime,endTime):
    itemStart = item.ts_start 
    itemEnd = item.ts_end 
    checkStart = is_time_between(startTime,endTime,itemStart)
    checkEnd = is_time_between(startTime,endTime,itemEnd)
    if not checkStart and checkEnd:
        print('not in range')
        print(item,startTime,endTime)
        return False
        exit(0)
    #print(checkStart,checkEnd)
    return checkStart and checkEnd

def preparse_withdraws(startTime,observerIP,collector,prefixP,hoursToAdd):
    #sleep a random amount of time just to make we dont query a whole bunch of files at once
    time.sleep(uniform(.1,1.1))
    
    print('finding withdraws...')
    endTime = startTime
    startTime = subtractTime(startTime,hours=hoursToAdd)
    storageLocation =pickleDir+f'withdraw/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    print(startTime,endTime)
    # exit(0)
    if os.path.exists(storageLocation):
        # print('loading updates...')
        #updates = pickle.load(open(storageLocation,'rb'))
        return #updates
    broker = createBroker()
    
    items = queryBroker(broker,startTime,endTime,collector,'update')
    
    
    allFilter = addFiltersNotPrefix(peer_ip=observerIP,type='withdraw')
    addPrefixToFilter(allFilter,prefix=prefixP)
    updates = []
    
    allUpdates = []
    for item in reversed(items): 
        
        if not itemInTimerange(item,startTime,endTime):
            continue
    
        parser = parseFileWithParams(item,allFilter)
        for update in parser:
            print(update)
            allUpdates.append(update)   
        
    print(f'found {len(allUpdates)} withdraws') 
    pickle.dump(allUpdates,open(storageLocation,'wb'))
    
    return
def preParse_ALL_updates(startTime,observerIP,collector,prefixP,hoursToAdd):
    #sleep a random amount of time just to make we dont query a whole bunch of files at once
    time.sleep(uniform(.1,1.1))
    
    print('finding ALL updates...')
    endTime = startTime
    startTime = subtractTime(startTime,hours=hoursToAdd)
            
    storageLocation =pickleDir+f'full_updates_w_a/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    print(startTime,endTime)
    # exit(0)
    if os.path.exists(storageLocation):
        # print('loading updates...')
        #updates = pickle.load(open(storageLocation,'rb'))
        return #updates
    broker = createBroker()
    
    items = queryBroker(broker,startTime,endTime,collector,'update')
    # for item in items[:-1]:
    #     print(item)
    # print(startTime,endTime)
    # exit(0)
    #print(items,startTime,endTime,collector)
    
    allFilter = addFiltersNotPrefix(peer_ip=observerIP,type='all')
    addPrefixToFilter(allFilter,prefix=prefixP)
    updates = []
    #find items that will contain inferior updates 
    #examine files in reverse chron.
    #each file is parsed in normal chron order (otherwise i'd have to load the entire file into RAM)
    #scan for a W. if one is found, we're done. 
    
    broken = False
    #items are parsed in chronological order, no need to sort
    #however, the broker gives us an extra 2 on the ends, e.g 9:45-12:15 (specifically 9:45-10:00 and 12:00-12:15 when we only want 10:00 - 12:00)
    allUpdates = []
    for item in reversed(items): 
        
        if not itemInTimerange(item,startTime,endTime):
            continue

        #find all updates, A and W in the file
        parser = parseFileWithParams(item,allFilter)
        for update in parser:
            #print(update)
            allUpdates.append(update)   
         
    sortedUpdates = sorted(allUpdates,key=lambda update: update['timestamp'],reverse=True)
    #exit(0)    
    #dump the inferior updates that we've seen and return them
    print(f'found {len(sortedUpdates)} Updates') 
    pickle.dump(sortedUpdates,open(storageLocation,'wb'))
    
    return
   
    
def preParse_inferior_updates_single_pass(startTime,observerIP,collector,prefixP,hoursToAdd):
    #sleep a random amount of time just to make we dont query a whole bunch of files at once
    time.sleep(uniform(.1,1.1))
    
    print('finding inferior updates single pass...')
    endTime = startTime
    startTime = subtractTime(startTime,hours=hoursToAdd)
    storageLocation =pickleDir+f'inferior_updates/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    print(startTime,endTime)
    # exit(0)
    if os.path.exists(storageLocation):
        # print('loading updates...')
        #updates = pickle.load(open(storageLocation,'rb'))
        return #updates
    broker = createBroker()
    
    items = queryBroker(broker,startTime,endTime,collector,'update')
    # for item in items[:-1]:
    #     print(item)
    # print(startTime,endTime)
    # exit(0)
    #print(items,startTime,endTime,collector)
    
    allFilter = addFiltersNotPrefix(peer_ip=observerIP,type='all')
    addPrefixToFilter(allFilter,prefix=prefixP)
    updates = []
    #find items that will contain inferior updates 
    #examine files in reverse chron.
    #each file is parsed in normal chron order (otherwise i'd have to load the entire file into RAM)
    #scan for a W. if one is found, we're done. 
    
    broken = False
    #items are parsed in chronological order, no need to sort
    #however, the broker gives us an extra 2 on the ends, e.g 9:45-12:15 (specifically 9:45-10:00 and 12:00-12:15 when we only want 10:00 - 12:00)
    allUpdates = []
    for item in reversed(items): 
        
        if not itemInTimerange(item,startTime,endTime):
            continue
    #     print(item)
    #     continue
    # exit(0)
    # for _ in range(3):
        #find all updates, A and W in the file
        parser = parseFileWithParams(item,allFilter)
        for update in parser:
            #print(update)
            allUpdates.append(update)   
        #if we did not see any updates, just keep going  
        if len(allUpdates)==0:
            continue
        #updates are not in chron order, so we sort them so they are DECENDING e.g. (11:30, 11:29, 11:20 ...)
        for update in sorted(allUpdates,key=lambda update: update['timestamp'],reverse=True):
            #if we see a withdraw, we're done.
            if update['elem_type'] == 'W':
                broken = True
                break
            elif update['elem_type']=='A':
                updates.append(update)
            else:
                print("why is update not W or A?",update)
                exit(0)
            #print(update)
            #print(helpers.convertUnixToTimeString(update['timestamp']))
        if broken:
            break
    #exit(0)    
    #dump the inferior updates that we've seen and return them
    print(f'found {len(updates)} inferior updates') 
    pickle.dump(updates,open(storageLocation,'wb'))
    
    return
   
    
def getRVPeers():
    peers = {}
    with open('routeviews_peers.csv','r') as f:
        f.readline()#skip header
        #ROUTEVIEWS COLLECTOR,AS NUMBER,PEERING ADDRESS,PREFIXES
        for line in f.readlines():
            parts = line.split(',')
            collector = parts[0].strip()
            asn = parts[1].strip()
            peerIP = parts[2].strip()
            numPrefixes = parts[3].strip()
            if collector not in peers:
                peers[collector] = {'ipv4':[],'ipv6':[]}
            if ':' in peerIP:
                peers[collector]['ipv6'].append((numPrefixes,asn,peerIP))
            else:
                peers[collector]['ipv4'].append((numPrefixes,asn,peerIP))
    for collector in peers:
        peers[collector]['ipv6'] = sorted(peers[collector]['ipv6'])
        peers[collector]['ipv4'] = sorted(peers[collector]['ipv4'])
    # for collector in peers:
    #     print(collector,peers[collector]['ipv4'][:5])
    return peers    
import requests
def getRipePeers():
    url = "https://stat.ripe.net/data/ris-peers/data.json"
    resp = requests.get(url)
    json = resp.json()
    peers = json['data']['peers']
    # print(peers.keys(),len(peers), len(peers.keys()))
    # peerASNS = set()
    peerDict = {}
    for peerID in peers:
        peerASNS = set()
        # print(peerID, len(peers[peerID]))
        
        for item in peers[peerID]:
            # print(item['asn'])
            peerASNS.add((item['asn'],item['ip']))
        peerDict[peerID] = {'numPeers': len(peerASNS), 'peers':peerASNS}
    return peerDict      
def getPeers(collector):
    peers = []
    if 'rrc' in collector:
        allPeers = getRipePeers()
        for entry in allPeers[collector]['peers']:
            
            peers.append(entry)
        return peers
    else:
        allPeers = getRVPeers()
        #num prefixes, ASN, peering ip 
        for entry in allPeers[collector]['ipv4']:
            peers.append(entry)
        for entry in allPeers[collector]['ipv6']:
            peers.append(entry)
        return peers
           
def tryLoadRib(tsEnd,prefixP,observerIP,collector):
    storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
    if os.path.exists(storageLocation):
        # print('loading fib')
        bad = False
        try:
            fibEntryForP = pickle.load(open(storageLocation,'rb'))
            return fibEntryForP
        #sometimes saving the pickle goes wrong, 
        # if it happens remove and parse it again 
        except EOFError:
            print("EOF FIB something probably went wrong saving this")
            return None
            #exit(0)
    else:
        # for _ in range(15):

        #         tsEnd = addTime(tsEnd,minutesToAdd=1)
        #         print('attempting to load fib at ',tsEnd)
        #         storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
        #         if os.path.exists(storageLocation):
        #             fibEntryForP = pickle.load(open(storageLocation,'rb'))
        #             return fibEntryForP
                
        return None
def findFibEntryForP(tsEnd,prefixP,observerIP,collector):
    hoursToAdd = get_hoursToAdd(collector)
    loadedFib = tryLoadRib(tsEnd,prefixP,observerIP,collector)
    if loadedFib != None:
        return loadedFib
    
    exit(0)
    #     at time T, download the observer's FIB and find the entry coresponding to prefix P. 
    #     if there does not exist an entry for prefix P in the FIB, then set T to T-2 hours and try again. repeat until we find an entry for prefix P in the FIB. 
    #maxTimeSearch = int((24/hoursToAdd)*10) #search at most n days (n=6)
    
    
    storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
    
        #     bad = True
        #     os.remove(storageLocation)
        #     print('EOF error, removing file. ', storageLocation)
        #     #exit(0)
        #print('trying to load ',fibEntryForP, type(fibEntryForP))
    print(f'finding fib for {collector}-{observerIP} at {tsEnd} for prefix', prefixP,)
    broker = createBroker()
    #ribs only use one paramater (end time)
    items = queryBroker(broker,tsEnd,tsEnd,collector,'rib')
    if len(items) > 1 or len (items) == 0:
        print("there should be excactly one rib! not ",len(items))
        if len(items) == 0:
            print(items)
            print('there is probably a problem with the query',tsEnd,collector,observerIP,prefixP)
            fibFound = False
            for _ in range(15):
                
                tsEnd = addTime(tsEnd,minutesToAdd=1)
                print('attempting to load fib at ',tsEnd)
                items = queryBroker(broker,tsEnd,tsEnd,collector,'rib')

                if len(items)==1: 
                    fibFound = True
                    loadedFib = tryLoadRib(tsEnd,prefixP,observerIP,collector)
                    if loadedFib != None:
                        return loadedFib
                    #print(items)
                    break
            if not fibFound:
                print("could not find fib after searching 15 mins")
                exit(0)
        
        #exit(0)
    fibEntriesForP = []

    filters = addFiltersNotPrefix(peer_ip=observerIP)
    addPrefixToFilter(filters,prefix=prefixP)
    #print('parsing fib')
    print(items)
    parser = parseFileWithParams(items[0],filters)
    
    print('parseing elems')
    for elem in parser:
        # if elem['prefix'] != prefixP:
        #     continue
        print(elem)    
        fibEntriesForP.append(elem)
        #assume theres only one and not parse the rest of the file
        break
    #exit(0)
    if len(fibEntriesForP) == 0:
        pickle.dump([],open(storageLocation,'wb'))
    #     print("go again!")
    #     cnt+=1
    #     if cnt >= maxTimeSearch:
    #         print("could not find FIB entry for P for ",observerIP)
    #         return None, None, None
            #exit(0)
        # tsStart = subtractTime(tsStart,hours=hoursToAdd)
        # tsEnd = subtractTime(tsEnd,hours=hoursToAdd)
    # elif len(fibEntriesForP) > 1:
    #     print("there should only be one entry for P not ",len(fibEntriesForP))
    #     return
    #     #exit(0)
    # else: #implicit == 1 
    #     fibEntryForP = fibEntriesForP[0]
        
    #print(fibEntriesForP)
    print(fibEntriesForP)
    fibEntryForP = fibEntriesForP[0]
    #exit(0)
    pickle.dump(fibEntryForP,open(storageLocation,'wb'))
    return fibEntryForP
def allUpdatesForPrefixes(tsEnd,prefixes,observerIP,collector):
    #print('before',prefixes)
    hoursToAdd = get_hoursToAdd(collector)
    #renamed just for convention in this file. tsEnd is the end point we want the updates for. startTime is endtime - hours to add (2 or 8)
    endTime = tsEnd
    startTime = subtractTime(tsEnd,hours=hoursToAdd)
    time.sleep(uniform(.1,1.1))
 
    rem = []
    for prefixP in prefixes:
        storageLocation =pickleDir+f'full_updates_w_a/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
        if os.path.exists(storageLocation):
            rem.append(prefixP)
    for r in rem:
        prefixes.remove(r)
    if len(prefixes) == 0:
        return
    
    #print('after',prefixes)

    broker = createBroker()
    items = queryBroker(broker,startTime,endTime,collector,'update')
    allFilter = addFiltersNotPrefix(peer_ip=observerIP,type='all')

    allUpdatesDict = {}
    #create a dict so we can store the prefixes we care about
    for prefix in prefixes:
        allUpdatesDict[prefix] = []
        
    for item in reversed(items): 
        # print(item)
        # exit(0)
        #ensure the file contains updates in the timerange we care about
        if not itemInTimerange(item,startTime,endTime):
            continue
        #find all updates, A and W in the file
        parser = parseFileWithParams(item,allFilter)
        for update in parser:
            prefix = update['prefix']
            if prefix not in prefixes:
                continue
            # print(update)

            allUpdatesDict[prefix].append(update)   
    for prefixP in prefixes:
        storageLocation =pickleDir+f'full_updates_w_a/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
        allUpdates=allUpdatesDict[prefixP]
    #sort the updates by timestamp     
        sortedUpdates = sorted(allUpdates,key=lambda update: update['timestamp'],reverse=True)
    #exit(0)    
    #dump the updates that we've seen and return them
        print(f'found {len(sortedUpdates)} Updates for',prefixP) 
        # if len(sortedUpdates)>0:
        #     print(storageLocation)

        pickle.dump(sortedUpdates,open(storageLocation,'wb'))

    return 
    
def fibsForPrefixes(tsEnd,prefixes,observerIP,collector):
    hoursToAdd =get_hoursToAdd(collector)
    #sleep a random amount of time just to make we dont query a whole bunch of files at once
    time.sleep(uniform(.1,1.1))
    # getPeers(collector)
    rem = []
    for prefixP in prefixes:
        storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
        if os.path.exists(storageLocation):
            rem.append(prefixP)
    for r in rem:
        prefixes.remove(r)
    if len(prefixes) == 0:
        return

        
    print(f'finding fib for {collector}-{observerIP} at {tsEnd} for prefixs')#, prefixP,)
    broker = createBroker()
    #ribs only use one paramater (end time)
    items = queryBroker(broker,tsEnd,tsEnd,collector,'rib')
    if len(items) > 1 or len (items) == 0:
        print("there should be excactly one rib! not ",len(items))
        if len(items) == 0:

            print('there is  probably a problem with the query',tsEnd,collector,observerIP,prefixP)
    #        pickle.dump(None,open(storageLocation,'wb'))
            return None, None, None 
       
        return
    fibEntriesForP = []
    
    filters = addFiltersNotPrefix(peer_ip=observerIP)

   
    #addPrefixToFilter(filters,prefix=prefixStr[:-1])
    print('parsing fib')
    parser = parseFileWithParams(items[0],filters)
    
    print('parseing elems')
    numIps = 0#len(prefixes)
    for elem in parser:
        if elem['prefix'] in prefixes:
            #print(elem)
            fibEntriesForP.append(elem)
            numIps+=1
            if numIps >= len(prefixes):
                break
        #assume theres only one and not parse the rest of the file
        #break
    rem = []
    print(f'found {len(fibEntriesForP)}/{len(prefixes)} prefix fib entries')
    for fibEntry in fibEntriesForP:
        prefixP = fibEntry['prefix']
        rem.append(prefixP)
        storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
        pickle.dump(fibEntry,open(storageLocation,'wb'))       
    print("found results for ",rem)
    if len(rem) == len(prefixes):
        return
    else:
        for r in rem:
            prefixes.remove(r)
        for prefixP in prefixes:
            print("dumping empty prefix",prefixP)
            storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
            pickle.dump([],open(storageLocation,'wb'))
    return
    exit(0)        
    #exit(0)
    if len(fibEntriesForP) == 0:
        # if manual:
        #     print('removing ',storageLocation)
        #     print('removing ',cacheDir+'manual/'+file)
        #     try:
        #         os.remove(storageLocation)
        #     except FileNotFoundError:
        #         pass
        #     try:
        #         os.remove(cacheDir+'manual/'+file)
        #     except FileNotFoundError:
        #         pass
        # else:
        pickle.dump([],open(storageLocation,'wb'))
        print("go again!")
        return
    elif len(fibEntriesForP) > 1:
        print("there should only be one entry for P not ",len(fibEntriesForP))
        return
        #exit(0)
    else: #implicit == 1 
        fibEntryForP = fibEntriesForP[0]

    print(fibEntriesForP)
    
    pickle.dump(fibEntryForP,open(storageLocation,'wb'))
    return fibEntryForP,tsStart,tsEnd
#sleep a random amount of time just to make we dont query a whole bunch of files at once
    time.sleep(uniform(.1,1.1))
    getPeers(collector)
    storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
    if os.path.exists(storageLocation):
   
            return "exists"# fibEntryForP,tsStart,tsEnd
        
    print(f'finding fib for {collector}-{observerIP} at {tsEnd} for prefix', prefixP,)
    broker = createBroker()
    #ribs only use one paramater (end time)
    items = queryBroker(broker,tsEnd,tsEnd,collector,'rib')
    if len(items) > 1 or len (items) == 0:
        print("there should be excactly one rib! not ",len(items))
        if len(items) == 0:

            print('there is  probably a problem with the query',tsEnd,collector,observerIP,prefixP)
            pickle.dump(None,open(storageLocation,'wb'))
            return None, None, None 
       
        return
    fibEntriesForP = []
    
    filters = addFiltersNotPrefix(peer_ip=observerIP)
    addPrefixToFilter(filters,prefix=prefixP)
    print('parsing fib')
    parser = parseFileWithParams(items[0],filters)
    
    print('parseing elems')
    for elem in parser:

        fibEntriesForP.append(elem)
        #assume theres only one and not parse the rest of the file
        break
    #exit(0)
    if len(fibEntriesForP) == 0:
        # if manual:
        #     print('removing ',storageLocation)
        #     print('removing ',cacheDir+'manual/'+file)
        #     try:
        #         os.remove(storageLocation)
        #     except FileNotFoundError:
        #         pass
        #     try:
        #         os.remove(cacheDir+'manual/'+file)
        #     except FileNotFoundError:
        #         pass
        # else:
        pickle.dump([],open(storageLocation,'wb'))
        print("go again!")
        return
    elif len(fibEntriesForP) > 1:
        print("there should only be one entry for P not ",len(fibEntriesForP))
        return
        #exit(0)
    else: #implicit == 1 
        fibEntryForP = fibEntriesForP[0]

    print(fibEntriesForP)
    
    pickle.dump(fibEntryForP,open(storageLocation,'wb'))
    return fibEntryForP,tsStart,tsEnd
from random import shuffle
from multiprocessing import Pool 
def preparseData(collector,observerIP,prefixP,months,startTime,shouldShuffle=False,manual=False,updates=True,ribs=True,numProcs=12):
    if 'rrc' in collector:
        hoursToAdd = 8 
    else:
        hoursToAdd = 2

    updateArgs = [] 
    fibArgs = []
    endTime = subtractTime(startTime,hours=hoursToAdd)
    for i in range(months*30 * int(24/hoursToAdd)): #364 days * the number of time ranges in a day
        updateArg =(startTime,observerIP,collector,prefixP,hoursToAdd)
        fibArg =(startTime,endTime,prefixP,observerIP,collector,hoursToAdd,manual)
        updateArgs.append(updateArg)
        fibArgs.append(fibArg)
        startTime = subtractTime(startTime,hours=hoursToAdd)
        endTime = subtractTime(endTime,hours=hoursToAdd)
    #if this is a rerun, shuffle the list to potentially increase the amount of work each thread will do, incresing uptime
    if shouldShuffle:
        shuffle(fibArgs)
        shuffle(updateArgs)
    print("updates, ",updates,'ribs',ribs)
    # exit(0)
    if ribs:
        pool = Pool(processes=numProcs)
        pool.starmap(preParseFindFib,fibArgs)
        print("done")
        pool.close()
        print('close')
        pool.join()
        print('join')
    
    if updates:
        pool = Pool(processes=numProcs)
        #rrc may have an off by 1, it should end at 00 not 05
        #double check and i may have to reparse things...
        pool.starmap(preParse_inferior_updates_single_pass,updateArgs)
        print('done')
        pool.close()
        print('close')
        pool.join()
        print('join')
    return

import requests 
import shutil
def downloadBrokerRequest(item,file):
    #print("file does not exist, downloading")
    timeoutConnect = 60
    timeoutRead = 60
    numFailes = 0
    responseSuccess = False
    while not responseSuccess:
        try:
            response = requests.get(item.url, stream=True,timeout=(timeoutConnect, timeoutRead))
            responseSuccess = True
        except Exception as e:
            print('failed to download broker item.\n got exception',e)
            timeoutConnect+=60
            timeoutRead+=60
            numFailes+=1
            if numFailes >10:
                #responseSuccess = True
                return False
            print("TIMEOUT try again" )
    print(cacheDir+'manual/'+file)
    try:
        with open(cacheDir+'manual/'+file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
    except Exception as e:
        print("broker req exception",e)
        return False
    return True

def convertUpdate(elem):
    """converts update from bgp parser cli to pybgp format
    there are only a few differences, e.g. as_path and elem_type instead of type
    but its important to remain consistant."""
    update = {'timestamp': 0, 'elem_type': 'A', 'peer_ip': '', 'peer_asn': 0, 
            'prefix': '', 'next_hop': '', 'as_path': '', 
            'origin_asns': [], 'origin': '', 'local_pref': 0, 
            'med': 0, 'communities': [], 'atomic': '', 'aggr_asn': 0, 'aggr_ip': ''}

    for key in elem:
        if key =='as_path':
            path = ''
            for p in elem['as_path']:
                path= path+' '+str(p)
            update['as_path']=path[1:]
            continue
        if key =='type':
            update['elem_type']==elem['type'][0]
            continue
        update[key] = elem[key]
    if len(elem['origin_asns']) >1:
        print('multihomed')
        exit(0)
    return update

import networkx
from matplotlib import pyplot
def add_inequality(graph, a, relation, b):
    if relation == '>=':
        graph.add_edge(a, b, weight=-1)
        graph.add_edge(b, a, weight=-1)
    elif relation == '=':
        graph.add_edge(a, b, weight=0)
        graph.add_edge(b, a, weight=0)
    elif relation == '>':
        graph.add_edge(a, b, weight=1)
    else:
        raise ValueError(f"Unsupported relation: {relation}")
def plotTuplesWithWeight(tuples,show,save):
    dgraph = networkx.DiGraph()
    for a, relation, b in tuples:
        add_inequality(dgraph, a, relation, b)
    
    plt = pyplot
    #pos = networkx.spring_layout(dgraph)
    pos = networkx.circular_layout(dgraph)
    networkx.draw(dgraph,pos,with_labels=True,arrows=True)
    edge_labels = networkx.get_edge_attributes(dgraph, 'weight')

    # Draw the edge labels
    networkx.draw_networkx_edge_labels(dgraph, pos, edge_labels=edge_labels)
    if save:
        print('saving graph')
        watGraphs = os.listdir('watGraphs')
        numGraphs = len(watGraphs)
        plt.savefig(f'watGraphs/{numGraphs}.png')
    if show:
        plt.show() 
def get_minutesForFile(collector):
    if 'rrc' in collector:
        return 5
    else:
        return 15        
def get_hoursToAdd(collector):
    if 'rrc' in collector:
        return 8
    else:
        return 2
def findContradictions(results):
    contradictions = []
    for a1,r1,b1 in results:
        for a2,r2,b2 in results:
            if a1==a2 and r1==r2 and b1 ==b2:
                continue
            if (a1==a2 and b1==b2) or (a1==b2 and b1==a2):
                if r1 =='=' and r2 =='=':
                    continue
                contra1 = (a1,r1,b1)
                contra2 = (a2,r2,b2)
                shouldAdd = True
                for foundContras in contradictions:
                    foundContra1, foundContra2 = foundContras
                    if contra1 ==foundContra1 and contra2 == foundContra2:
                        shouldAdd = False
                        break
                if shouldAdd:
                    contradictions.append((contra1,contra2))
    return contradictions         
def get_withdraws_for_p(startTime,prefixP,observerIP,collector):
    """find withdraws from all updates"""
    
    allUpdates = get_all_updates_for_p(startTime,observerIP,collector,prefixP)
    withdraws = []
    for update in allUpdates:
        if update['elem_type'] =='W':
            withdraws.append(update)
    return withdraws
    #print('finding ALL withdraws...')
    hoursToAdd = get_hoursToAdd(collector)
    endTime = startTime
    
    startTime = subtractTime(startTime,hours=hoursToAdd)
    #print(startTime,endTime)            
    storageLocation =pickleDir+f'full_updates_w_a/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    if os.path.exists(storageLocation):
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
        withdraws = []
        for update in updates:
            if update['elem_type'] =='W':
                withdraws.append(update)
        return withdraws
  
    #exit(0)
    broker = createBroker()
    
    items = queryBroker(broker,startTime,endTime,collector,'update')
 
    allFilter = addFiltersNotPrefix(peer_ip=observerIP,type='all')
    addPrefixToFilter(allFilter,prefix=prefixP)
    updates = []
    
   
    allUpdates = []
    
    for item in reversed(items): 
        # print(item)
        # exit(0)
        if not itemInTimerange(item,startTime,endTime):
            continue

        #find all updates, A and W in the file
        parser = parseFileWithParams(item,allFilter)
        for update in parser:
            # print(update)
            allUpdates.append(update)   
         
    sortedUpdates = sorted(allUpdates,key=lambda update: update['timestamp'],reverse=True)
    #exit(0)    
    #dump the inferior updates that we've seen and return them
    print(f'found {len(sortedUpdates)} Updates') 
    # exit(0)
    pickle.dump(sortedUpdates,open(storageLocation,'wb'))

    withdraws = []
    for update in sortedUpdates:
        if update['elem_type'] =='W':
            withdraws.append(update)
    return withdraws        
def detectCycles(tuples,showGraph = False):
    # print('detecting cycles')
    """detects if cycles are present in the given set of tuples of a>b
    returns:
        True, [cycles] if there are cycles present AND the cycles present are not a result of a=b,b=a
        False, '' on no cycles detected"""
    G = networkx.DiGraph()
    knownEQ = []
    for t in tuples:
    #for t in fullTuples:
        a,op,b = t
        G.add_node(a)
        G.add_node(b)
        if op == '>':
            G.add_edge(a,b,weight=1)    
        if op =='=':
            G.add_edge(a,b, weight=0)
            G.add_edge(b,a, weight=0)
            if (a,b) not in knownEQ and (b,a) not in knownEQ:
                knownEQ.append((a,b))
        #print(t)
    cycles = list(networkx.simple_cycles(G))
    cyclesDetected = False
    if len(cycles) >0:
        pass
        #print('cycles detected!')
        # print(cycles)
    cyclesToReturn = cycles        
    for cycle in cycles:
        # if len(cycle)==2:
        #     a = cycle[0]
        #     b = cycle[1]
        #     #equals is fine
        #     if (a,b) in knownEQ or (b,a) in knownEQ:
        #         continue
        
        pathWeights = []
        cycleStr = ""
        for i in range(len(cycle)):
            u = cycle[i]
            try:
                v = cycle[i+1]
                
            except:
                v=''
                break
            data = G.get_edge_data(u,v)
            
            weight = data['weight']
            pathWeights.append(weight)
            cycleStr = cycleStr + f"{u} {weight} "
            #print(u,weight,v)
        
        
        #print(cycle)            
        # print(pathWeights)            
        if all (w==0 for w in pathWeights):
            cyclesToReturn.remove(cycle)
            continue
        else:
            cyclesDetected = True
        #print(cycleStr+v)    
        #exit(0)
        #optionally, we can print the cycle to the graph with the code below
        # print(cycle)
        if showGraph:
            H = networkx.DiGraph()
            networkx.add_cycle(H,cycle)
            pos = networkx.circular_layout(H)
            pos = networkx.spring_layout(H)
            networkx.draw(H, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=1000, font_size=16, font_weight='bold')        
            plt.show()  
        #return True, cycles   
        #exit(0)   
    if cyclesDetected:
        #print("len diff",len(cyclesToReturn),len(cycles))
        return True,cyclesToReturn
    else:
        return False, ''   
def detectBadChange(resultsBefore,funcfail):
    """this function hard exits (on purpose)
        detects if we made a contradictory mistake, e.g. a>b, b>a, a>=b when we know a>b etc.
        this also detects cycles with the help of detectCycles.
        cycles are contradictory since by definition this implies a>b>c>a, which is bad (a>c c>a)"""
    if len(resultsBefore)==0:
        return
    # print(resultsAfter,funcfail)
    for a1, rel1, b1 in resultsBefore:
        for a2, rel2, b2 in resultsBefore:
            #since we're iterating over the same list twice, skip situations of the same value
            if a1 ==a2 and rel1 ==rel2 and b1==b2:
                continue
            #(a ? b) and (b ? a)
            if a1 == b2 and b1 == a2:
                #this is fine, it implies a=b,b=a
                if rel1 == '>=' and rel2 =='>=':
                    continue
                #this one is also fine 
                elif rel1 == '=' and rel2 =='=':
                    continue
                #this is not k 
                #we cant have a>b, b>a under this function. So it should be handled elsewhere
                #it could be that 
                elif rel1 =='>' and rel2 == '>':
                    print('bad change detected!', funcfail)
                    print(a1,rel1,b1)
                    print(a2,rel2,b2)
                    exit(0)
                else:
                    print('bad change detected! else block', funcfail)
                    print(a1,rel1,b1)
                    print(a2,rel2,b2)
                    exit(0)
            # implies rel1 !=rel2                    
            if a1 == a2 and b1 == b2:
                print('bad change detected! implicit rel1 != rel2', funcfail)
                print(a1,rel1,b1)
                print(a2,rel2,b2)
                exit(0)
    haveCycles,cycles =  detectCycles(resultsBefore)
        
    if haveCycles:
        print('bad change detected! cycles ', cycles, funcfail)
        exit(0)    

def detectBadChange_noexit(resultsBefore,funcfail):
    """this function does not hard exit (on purpose)
        detects if we made a contradictory mistake, e.g. a>b, b>a, a>=b when we know a>b etc.
        this also detects cycles with the help of detectCycles.
        cycles are contradictory since by definition this implies a>b>c>a, which is bad (a>c c>a)"""
    if len(resultsBefore)==0:
        return False
    # print(resultsAfter,funcfail)
    for a1, rel1, b1 in resultsBefore:
        for a2, rel2, b2 in resultsBefore:
            #since we're iterating over the same list twice, skip situations of the same value
            if a1 ==a2 and rel1 ==rel2 and b1==b2:
                continue
            #(a ? b) and (b ? a)
            if a1 == b2 and b1 == a2:
                #this is fine, it implies a=b,b=a
                if rel1 == '>=' and rel2 =='>=':
                    continue
                #this one is also fine 
                elif rel1 == '=' and rel2 =='=':
                    continue
                #this is not k 
                #we cant have a>b, b>a under this function. So it should be handled elsewhere
                #it could be that 
                elif rel1 =='>' and rel2 == '>':
                    print('bad change detected! a>b b>a', funcfail)
                    print(a1,rel1,b1)
                    print(a2,rel2,b2)
                    return True
                    
                else:
                    print('bad change detected! else block', funcfail)
                    # print(a1,rel1,b1)
                    # print(a2,rel2,b2)
                    return True
            # implies rel1 !=rel2                    
            if a1 == a2 and b1 == b2:
                print('bad change detected! implicit rel1 != rel2', funcfail)
                # print(a1,rel1,b1)
                # print(a2,rel2,b2)
                return True
    haveCycles,cycles =  detectCycles(resultsBefore)
    if haveCycles:
        #print('bad change detected! cycles ', cycles, funcfail)
        print('bad change detected! cycles ', funcfail)
        return True
    
    return False


def get_all_updates_for_p(startTime,observerIP,collector,prefixP): 
    """simply returns all updates from t0 to t1 where t1= startTime
     difference between t0 and t1 is set by hoursToAdd which is found from the collector
        2 for route-views, 8 for rrc """
    #print('finding ALL updates...')
    
    hoursToAdd = get_hoursToAdd(collector)
    endTime = startTime
    startTime = subtractTime(startTime,hours=hoursToAdd)
            
    storageLocation =pickleDir+f'full_updates_w_a/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    #print(startTime,endTime)
    # exit(0)
    if os.path.exists(storageLocation):
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
    
        return updates
  
    #exit(0)
    broker = createBroker()
    
    items = queryBroker(broker,startTime,endTime,collector,'update')
    # for item in items[:-1]:
    #     print(item)
    # print(startTime,endTime)
    # exit(0)
    #print(items,startTime,endTime,collector)
    
    allFilter = addFiltersNotPrefix(peer_ip=observerIP,type='all')
    addPrefixToFilter(allFilter,prefix=prefixP)


    #items are parsed in chronological order, no need to sort
    #however, the broker can give an extra 2 on the ends, e.g 9:45-12:15 (specifically 9:45-10:00 and 12:00-12:15 when we only want 10:00 - 12:00)
    allUpdates = []
    
    for item in reversed(items): 
        # print(item)
        # exit(0)
        if not itemInTimerange(item,startTime,endTime):
            continue

        #find all updates, A and W in the file
        parser = parseFileWithParams(item,allFilter)
        for update in parser:
            # print(update)
            allUpdates.append(update)   
    #sort the updates by timestamp     
    sortedUpdates = sorted(allUpdates,key=lambda update: update['timestamp'],reverse=True)
    #exit(0)    
    #dump the updates that we've seen and return them
    print(f'found {len(sortedUpdates)} Updates') 

    pickle.dump(sortedUpdates,open(storageLocation,'wb'))

    return sortedUpdates



def get_annoucements_for_p(startTime,prefixP,observerIP,collector):     

    all_updates = get_all_updates_for_p(startTime,observerIP,collector,prefixP)

    annoucements = []
    for update in all_updates:
        if update['elem_type'] =='A':
            annoucements.append(update)
    return annoucements

def parseFibAllNeighborsSingleP(timePoint,collector,prefixP):
    """parses a given RIB for ALL peers FIBs for a single Prefix
    inputs:
        Timepoint: the time we want the fib for 
        collector: the collector's Peers we want 
        prefixP: the prefix we want the peers' FIB route to
    Returns: 
        nothing, this is for preparsing only.
        Though as a byproduct it only dumps at the end"""
#sleep a random amount of time just to make we dont query a whole bunch of files at once
    time.sleep(uniform(.1,1.1))
        
    print(f'finding fib for {collector} at {timePoint} for prefix', prefixP,)
    broker = createBroker()
    #ribs only use one paramater (end time)
    items = queryBroker(broker,timePoint,timePoint,collector,'rib')
    if len(items) > 1 or len (items) == 0:
        print("there should be excactly one rib! not ",len(items))
        if len(items) == 0:
            print('there is  probably a problem with the query',timePoint,collector,observerIP,prefixP)
        #    exit(0)
        return
    fibEntriesForP = []
    
    filters = {}
    addPrefixToFilter(filters,prefix=prefixP)
    print('parsing fib')
    parser = parseFileWithParams(items[0],filters)
    
    print('parseing elems')
    for elem in parser:
        fibEntriesForP.append(elem)
    for fibEntryForP in fibEntriesForP:
        observerIP = fibEntryForP['peer_ip']    
        storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{timePoint}.pickle'
        pickle.dump(fibEntryForP,open(storageLocation,'wb'))
    return 

def construct_digraph(local_preference_results):
    dgraph = networkx.DiGraph() 
    for result in local_preference_results:
        a = result[0]
        op = result[1]
        b = result[2]
        if a not in dgraph.nodes():
            dgraph.add_node(a)
        if b not in dgraph.nodes():
            dgraph.add_node(b)
        if op == '=':
            dgraph.add_edge(a,b)
            dgraph.add_edge(b,a)
        if op  =='>':
            dgraph.add_edge(a,b)
    return dgraph
def all_a_b_exist(local_preference_results):
    #create a directed graph with a node for all a, b in the local_preference_results
    #if a>b add a path from a->b 
    #if a=b add a path from a->b and b->a
    
    dgraph = construct_digraph(local_preference_results)
    done = []
    for nodeA in dgraph.nodes():
        for nodeB in dgraph.nodes():
            if nodeA == nodeB:
                continue
            try:
                #check if a can reach all other nodes 
                sp = networkx.shortest_path(dgraph,nodeA,nodeB)
                continue
                #print(sp)
            except networkx.exception.NetworkXNoPath :
                #print("no path between ",nodeA,nodeB)
                #if a cannot reach node b, can b reach a?
                #if so this is fine, this implies b>a
                try:
                    sp = networkx.shortest_path(dgraph,nodeB,nodeA)
                except:
                    print("reverse check no path between ",nodeB,nodeA)
                
                    return False
    return True
def find_inferior_updates_from_all_annoucements(startTime,observerIP,collector,prefixP):
    """finds inferior updates (annoucements after a W message)"""
    print('finding inferior updates from annoucements...')
    allUpdates = get_all_updates_for_p(startTime,observerIP,collector,prefixP)
    # for update in allUpdates:
    #     print(convertUnixToTimeString(update['timestamp']),update['elem_type'])
    #print("~~~~")
    endTime = startTime
    hoursToAdd = get_hoursToAdd(collector)
    startTime = subtractTime(startTime,hours=hoursToAdd)

    storageLocation =pickleDir+f'inferior_updates/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    print(startTime,endTime)

    #need to test <TODO>
    if os.path.exists(storageLocation):
        
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
        # for update in updates: 
        #     print(convertUnixToTimeString(update['timestamp']),update['elem_type'])
        return updates
        # if len(updates)==0:
        #     return updates
        # return find_subset_inferior(updates,fibEntryForP)
    
    
    broken = False
    #find items that will contain inferior updates 
    #scan for a W. if one is found, we're done. 
    #updates are not in chron order, so we sort them so they are DECENDING e.g. (11:30, 11:29, 11:20 ...)
    inferior_updates = []
    for update in sorted(allUpdates,key=lambda update: update['timestamp'],reverse=True):
        #print(convertUnixToTimeString(update['timestamp']),update['elem_type'])
        #print(update)
        #if we see a withdraw, we're done.
        if update['elem_type'] == 'W':
            break
        elif update['elem_type']=='A':
            inferior_updates.append(update)
        else:
            print("why is update not W or A?",update)
            exit(0)
        #print(update)
        #print(convertUnixToTimeString(update['timestamp']))
    
    #dump the inferior updates that we've seen and return them
    print(f'found {len(inferior_updates)} inferior updates') 
    #pickle.dump(updates,open(storageLocation,'wb'))
    
    return inferior_updates    

def getAllNeighborsFromResults(results):
    allNeighbors = set() 
    for a,r,b in results:
        allNeighbors.add(a)
        allNeighbors.add(b)
    return allNeighbors



def removeInferiorResults(results):
    """removes results we already know about, e.g. removes a>=b when we have a>b in results"""
    remove = []
    for a1,r1,b1 in results:
        originalRes = (a1,r1,b1)
        for a2,r2,b2 in results: 
            #weird = False  
            newRes = (a2,r2,b2) 
            if a1== b1 and a2==b2 and r1 ==r2:
                continue
            if a1 == b2 and b1 == a2:
                if r1 !='>=' and r2 ==">=":
                    if (a2,r2,b2) not in remove:
                        remove.append((a2,r2,b2))
            if a1 == a2 and b1 == b2:
                if r1 !='>=' and r2 ==">=":
                    if (a2,r2,b2) not in remove:
                        remove.append((a2,r2,b2))    
               
    for r in remove:
        results.remove(r)
    return results


def getMergedCleanUpdates(startTime,endTime,collector,observerIP):
    """merges and cleans updates, see CleanUpdates"""
    start_endStorageLocation =pickleDir+f'clean_updates/C{collector}O{observerIP}S{startTime}E{endTime}.pickle'
    if os.path.exists(start_endStorageLocation):            
        updates = pickle.load(open(start_endStorageLocation,'rb'))
        return updates
    mins = get_minutesForFile(collector)
    tmpTime = startTime
    allUpdates = []
    print(startTime,endTime,mins)
    # exit(0)
    while tmpTime != endTime:
        tmpTime = addTime(tmpTime,minutesToAdd=mins)
        #storageLoc tmpTime end
        storageLocation =pickleDir+f'clean_updates/C{collector}O{observerIP}S{startTime}E{tmpTime}.pickle'
        if os.path.exists(storageLocation):
            # print('loading updates...')
            updates = pickle.load(open(storageLocation,'rb'))
            allUpdates.extend(updates)
        else:
            updates = getCleanUpdates(startTime,tmpTime,collector,observerIP)
            allUpdates.extend(updates)
        startTime = addTime(startTime,minutesToAdd=mins)  
    cleanedUpdates = cleanUpdates(allUpdates)
    pickle.dump(cleanedUpdates,open(start_endStorageLocation,'wb'))
    return cleanedUpdates
def getCleanUpdates(startTime,endTime,collector,observerIP):
    storageLocation =pickleDir+f'clean_updates/C{collector}O{observerIP}S{startTime}E{endTime}.pickle'
    print(startTime,endTime)
    # exit(0)
    if os.path.exists(storageLocation):
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
        return updates
    allUpdates = []
    broker = createBroker()
    items = broker.query(startTime,endTime,collector, data_type='update')
    filters = addFiltersNotPrefix(peer_ip=observerIP)
    for item in items:
        parser = parseFileWithParams(item,filters)
        for elem in parser:
            #print(elem)
            allUpdates.append(elem)   
    cleanedUpdates = cleanUpdates(allUpdates)
    pickle.dump(cleanedUpdates,open(storageLocation,'wb'))
    return cleanedUpdates

def areUpdatesSame(update1,update2):
    """checks if two updates are the same
    sometimes RIPE and RV supply duplicate updates
    This simply returns True if update1 and update2 are the same
    this function is necessary because {1:a,2:b}!={2:b,1:a}"""
    for key in update1.keys():
        if key =='communities':
            oldCom = update2[key]            
            newCom = update1[key]
            if oldCom != None and newCom!=None:
                if set(oldCom) == set(newCom):
                    pass
                else:
                    return False
            else:
                if oldCom == newCom:
                    pass
                else:
                    return False    
        if update2[key] != update1[key]:
            return False
    return True

def cleanUpdates(allUpdates):
    print('cleaning updates ...')

    for i in range(len(allUpdates)):
        update1 = allUpdates[i]
        if allUpdates[i] == None:
            continue
        for j in range(len(allUpdates)):
            if i ==j:
                continue
            if allUpdates[j] == None:
                continue
            update2 = allUpdates[j]  
            if areUpdatesSame(update1,update2):
                allUpdates[j] = None
                #print("update 1,2 are same")
    print('removing Duplicates ...')            
    while None in allUpdates:
        allUpdates.remove(None)
    return allUpdates  