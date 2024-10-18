"""find all inferior updates for 1 year
should hopefully speed up finding local preference results
To use, change the args below."""
import helpers 
from helpers import pickleDir 
import pickle
import os

collector = 'route-views.sg'
observerIP = '27.111.228.6'
startTime = '2023-03-30T00:00:00' #original start time '2024-03-30T00:00:00'
prefixP = '103.84.52.0/24'
fibEntryForP = ''
#how many months to get data for
months = 6
shouldShuffle = True
def findFibEntryForP(tsStart,tsEnd,prefixP,observerIP,collector):
    
    fibFound = False
    #     at time T, download the observer's FIB and find the entry coresponding to prefix P. 
    #     if there does not exist an entry for prefix P in the FIB, then set T to T-2 hours and try again. repeat until we find an entry for prefix P in the FIB. 
    maxTimeSearch = int((24/hoursToAdd)*10) #search at most n days (n=6)
    cnt = 0
    #while not fibFound:
    storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
    if os.path.exists(storageLocation):
        # print('loading fib')
        bad = False
        try:
            fibEntryForP = pickle.load(open(storageLocation,'rb'))
            return  fibEntryForP,tsStart,tsEnd
        #sometimes saving the pickle goes wrong, 
        # if it happens remove and parse it again 
        except EOFError:
            bad = True
            os.remove(storageLocation)
            print('EOF error, removing file. ', storageLocation)
            #exit(0)
        #print('trying to load ',fibEntryForP, type(fibEntryForP))
        
    print(f'finding fib for {collector}-{observerIP} at {tsEnd} for prefix', prefixP,)
    broker = helpers.createBroker()
    #ribs only use one paramater (end time)
    items = helpers.queryBroker(broker,tsEnd,tsEnd,collector,'rib')
    if len(items) > 1 or len (items) == 0:
        print("there should be excactly one rib! not ",len(items))
        if len(items) == 0:
            print('there is probably a problem with the query',tsEnd,collector,observerIP,prefixP)
            return None, None, None 
        # with open('failed_simple_tests.txt','a+') as f:
        #         f.write(f"{collector},{observerIP},{prefixP} failed by not having exactly one rib {len(items)}")
        #         f.write('\n')
        return
        #exit(0)
    filters = helpers.addFiltersNotPrefix(peer_ip=observerIP)
    helpers.addPrefixToFilter(filters,prefix=prefixP)
    print('parsing fib')
    parser = helpers.parseFileWithParams(items[0],filters)
    fibEntriesForP = []
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
        print("go again!")
        return
    elif len(fibEntriesForP) > 1:
        print("there should only be one entry for P not ",len(fibEntriesForP))
        return
        #exit(0)
    else: #implicit == 1 
        fibEntryForP = fibEntriesForP[0]
        fibFound = True
    print(fibEntriesForP)
    
    pickle.dump(fibEntryForP,open(storageLocation,'wb'))
    return fibEntryForP,tsStart,tsEnd

def find_inferior_updates_single_pass(fibEntryForP,startTime,observerIP,collector,prefixP):
    print('finding inferior updates single pass...')
    endTime = startTime
    startTime = helpers.subtractTime(startTime,hours=hoursToAdd)
    storageLocation =pickleDir+f'inferior_updates/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    if os.path.exists(storageLocation):
        return
        # print('loading updates...')
        # try:
        #     updates = pickle.load(open(storageLocation,'rb'))
        #     return updates
        # except EOFError:
        #         print(storageLocation,'is bad, removing and recreating...')
        #         #bad = True
        #         os.remove(storageLocation)
    
    broker = helpers.createBroker()
    
    items = helpers.queryBroker(broker,startTime,endTime,collector,'update')
    #print(items,startTime,endTime,collector)
    withdrawFilter = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='withdraw')
    helpers.addPrefixToFilter(withdrawFilter,prefix=prefixP)
    annouceFilter = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='announce')
    helpers.addPrefixToFilter(annouceFilter,prefix=prefixP)
    allFilter = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='all')
    helpers.addPrefixToFilter(allFilter,prefix=prefixP)
    wHasBeenSeen = False
    updates = []
    #find items that will contain inferior updates 
    #examine files in reverse chron.
    #each file is parsed in normal chron order (otherwise i'd have to load the entire file into RAM)
    #scan for a W. if one is found, we're done. 
    #if no W is found, append another one. 
    #if NO file contains a W we're super done. 
    itemsWithInferior = []
    foundInfiriorFiles = False
    for item in items:    
        parser = helpers.parseFileWithParams(item,allFilter)
        for update in parser:
            
            print(update)
            if update['elem_type'] == 'W':
                updates = []     
                wHasBeenSeen = True
                continue
            if update['elem_type']!='W':
                updates.append(update)
                
        #its possible that we only need to do this for the first file so i'll leave this here for later jic. 
        # if not wHasBeenSeen:
        #     break
    pickle.dump(updates,open(storageLocation,'wb'))
    print(f'found {len(updates)} inferior updates') 
    return updates

if 'rrc' in collector:
    hoursToAdd = 8 
else:
    hoursToAdd = 2

updateArgs = [] 
fibArgs = []
from random import shuffle

endTime = helpers.subtractTime(startTime,hours=hoursToAdd)
for i in range(months*30 * int(24/hoursToAdd)): #364 days * the number of time ranges in a day
    updateArg = ((fibEntryForP,startTime,observerIP,collector,prefixP))
    fibArg =(startTime,endTime,prefixP,observerIP,collector)
    updateArgs.append(updateArg)
    fibArgs.append(fibArg)
    startTime = helpers.subtractTime(startTime,hours=hoursToAdd)
    endTime = helpers.subtractTime(endTime,hours=hoursToAdd)
#if this is a rerun, shuffle the list to potentially increase the amount of work each thread will do, incresing uptime
if shouldShuffle:
    shuffle(fibArgs)
from multiprocessing import Pool 
pool = Pool(processes=12)
pool.starmap(find_inferior_updates_single_pass,updateArgs)
#pool.starmap(findFibEntryForP,fibArgs)
pool.close()
pool.join()

