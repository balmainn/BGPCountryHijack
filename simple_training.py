import helpers 
import policies
import pickle
import os, sys 
import networkx
# note: an ipv4 peer may not hear ipv6 updates and an ipv6 peer may not hear ipv4 peers. For this reason, we limit the peers based on the ip version of prefix P. 

#candidates:
#peerASN,peerIP,numNeighbors
#45494,	27.111.228.161,	3, #not found in 2 days 
#134363,	27.111.228.231,	8,
#58601,	27.111.228.248,	8,
#63516,	27.111.229.15,	33,

# known good settings 
# collector = 'route-views.sg'
# prefixP = '103.84.52.0/24' 
# observerASN = 18106 
# observerIP = '27.111.228.6'

#example route-views.sg 18106 27.111.228.6 103.84.52.0/24 2024-03-30T00:00:00 60
         #route-views.sg 8220 27.111.229.123 103.84.52.0/24 2024-03-30T00:00:00 60

#collector = 'route-views2'
#prefixP = '103.84.52.0/24' 

#todo 4+


#write a thing to do min neighbors 

# collector = 'rrc12'

# prefixP = '185.228.94.0/24'

# prefixP = '38.252.177.0/24'
#prefixP = '103.228.49.0/24' #'194.58.198.0/24'#pulled from fib to start with
# prefixP = '185.228.94.0/24' #RRC00 132825 '43.251.115.197'
#', 'peer_asn': ,
# observerASN = 12779

# observerIP = '80.81.194.186'

# masterPeers = policies.getMasterPeers()
# collectorPeers = masterPeers['collector']['peers']
# for peerASN,peerIP in collectorPeers:
#     if ':' in peerIP:
#         continue
#     else:
#         observerASN = peerASN
#         observerIP = peerIP

def findFibEntryForP(tsStart,tsEnd,prefixP,observerIP,collector):
    
    fibFound = False
    #     at time T, download the observer's FIB and find the entry coresponding to prefix P. 
    #     if there does not exist an entry for prefix P in the FIB, then set T to T-2 hours and try again. repeat until we find an entry for prefix P in the FIB. 
    maxTimeSearch = int((24/hoursToAdd)*10) #search at most n days (n=6)
    cnt = 0
    while not fibFound:
        storageLocation =pickleDir+ f'fibEntryForP/ribs/{prefixP.replace('/','-')}{collector}-{observerIP}-{tsEnd}.pickle'
        if os.path.exists(storageLocation):
            # print('loading fib')
            bad = False
            try:
                fibEntryForP = pickle.load(open(storageLocation,'rb'))
            #sometimes saving the pickle goes wrong, 
            # if it happens remove and parse it again 
            except EOFError:
                bad = True
                os.remove(storageLocation)
                print('EOF error, removing file. ', storageLocation)
                #exit(0)
            #print('trying to load ',fibEntryForP, type(fibEntryForP))
            if not bad:
                if len(fibEntryForP)== 0:
                    print('attempted to load, go again!')
                    tsStart = helpers.subtractTime(tsStart,hours=hoursToAdd)
                    tsEnd = helpers.subtractTime(tsEnd,hours=hoursToAdd)
                    continue
                else:
                    return fibEntryForP,tsStart,tsEnd
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
            cnt+=1
            if cnt >= maxTimeSearch:
                print("could not find FIB entry for P for ",observerIP)
                return None, None, None
                #exit(0)
            tsStart = helpers.subtractTime(tsStart,hours=hoursToAdd)
            tsEnd = helpers.subtractTime(tsEnd,hours=hoursToAdd)
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
def get_all_updates (start_time, end_time,observerIP,collector):     
    #start_time = "2024-03-02T00:00:00"
    #end_time = "2024-03-09T00:00:00"
    storageLocation =pickleDir +f'updatesForP/updates/AllUpdates-{collector}{observerIP}{end_time}.pickle'
    if os.path.exists(storageLocation):
        updates = pickle.load(open(storageLocation,'rb'))
        return updates
    print('finding updates for : ', start_time,end_time,collector,observerIP)
    broker = helpers.createBroker()
    items = helpers.queryBroker(broker,start_time,end_time,collector,'update')
    print('found ', len(items), 'updates files')
    updates = []
    for item in items:
        filters = helpers.addFiltersNotPrefix(peer_ip=observerIP)
        parser = helpers.parseFileWithParams(item,filters)
        
        for elem in parser:
            #print(elem)
            updates.append(elem)
    print('returning ',len(updates), 'updates')
    pickle.dump(updates,open(storageLocation,'wb'))
    return updates

def get_updates_for_p (start_time, end_time,prefixP,observerIP,collector):     
    #start_time = "2024-03-02T00:00:00"
    #end_time = "2024-03-09T00:00:00"
    storageLocation =pickleDir+f'updatesForP/updates/{prefixP.replace('/','-')}{collector}{observerIP}{end_time}.pickle'
    if os.path.exists(storageLocation):
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
        return updates
    print('finding updates for : ', start_time,end_time, prefixP,collector,observerIP)
    broker = helpers.createBroker()
    items = helpers.queryBroker(broker,start_time,end_time,collector,'update')
    print('found ', len(items), 'updates files')
    updates = []
    for item in items:
        filters = helpers.addFiltersNotPrefix(peer_ip=observerIP)
        helpers.addPrefixToFilter(filters,prefix=prefixP)
        parser = helpers.parseFileWithParams(item,filters)
        
        for elem in parser:
            #print(elem)
            updates.append(elem)
    print('returning ',len(updates), 'updates')
    pickle.dump(updates,open(storageLocation,'wb'))
    return updates

def splitAsPathFromUpdate(update):
    asPath = update['as_path']
    originAS = update['origin_asns']
    #to handle multihome, 
    # just replace the last element in the list with an origin
    if '{' in asPath: 
            a = asPath.split(' ')
            a.append(originAS[0])
            return a
    else:
        return asPath.split(' ')

def compare_updates(updates,local_pref_results,fibEntryForP):
    #sort updates in reverse chronological order (because the updates retrieved from bgpkit are ordered chronologically)
    #let fib_neighbor = the neighbor that sent the update that was accepted into the FIB. 
    updates = sorted(updates,key=lambda update: update['timestamp'],reverse=True)
    fib_neighbor = helpers.findNeighborInUpdate(fibEntryForP)
    for i,update1 in enumerate(updates):
        n1 = helpers.findNeighborInUpdate(update1)
        update1pathLen = len(splitAsPathFromUpdate(update1))
        for j, update2 in enumerate(updates):
            if j < i:
                continue
            n2 = helpers.findNeighborInUpdate(update2)
            update2pathLen = len(splitAsPathFromUpdate(update2))
            result = None
            if n1 != n2:
                #this is the table from the whiteboard written out in pseudo code
                if update1pathLen > update2pathLen and n1 == fib_neighbor:
                    result = (n1, '>', n2)
                elif update1pathLen > update2pathLen and n2 == fib_neighbor:
                    result = (n2, '>=', n1)
                elif update1pathLen == update2pathLen and n1 == fib_neighbor:
                    result = (n1, '>=', n2)
                elif update1pathLen == update2pathLen and n2 == fib_neighbor:
                    result = (n2, '>=', n1)
                elif update1pathLen < update2pathLen and n1 == fib_neighbor:
                    result = (n1, '>=', n2)
                elif update1pathLen > update2pathLen and n2 == fib_neighbor:
                    result = (n2,'>', n1)
                else:
                    result = None
                if result == None:
                    print("why is result none?")
                    exit(0)
                #dont store duplicates, they dont help and will break the algorithm when examining the preference results.  
                
                if len (local_pref_results) ==0 and result != None:
                    local_pref_results.append(result)
                else:
                    if result not in local_pref_results and result != None: 
                        store = True
                        for pastResult in local_pref_results:
                            #print(pastResult)
                            if result[0] == pastResult[0] and result[2] == pastResult[2]:
                                if pastResult[1] =='>=':
                                    pastResult = (result[0],result[1],result[2])
                                    #store = True
                                    break
                                else:
                                    store = False
                                    break
                                continue
                        if store:
                            print('appending result',result)
                            local_pref_results.append(result)
                        
    local_pref_results = inferRelationship(local_pref_results)
    # for elem in elemsToAdd:
    #     if elem not in local_pref_results:
    #         print('adding by inference ',elem)
    #         local_pref_results.append(elem)
                        
                        
                    
    return local_pref_results
def didFibChange(oldFibForP,fibEntryForP):
    """checks if two updates are the same or different
    ignores timestamp because that one will probably always change
    we're mostly concerned about the other things, not the timestamp"""
    #handles base case
    if 'timestamp' not in oldFibForP.keys():
        print('originial fib entry, nothing to do')
        return True
    for key in fibEntryForP.keys():
        if key == 'timestamp':
            continue
        if oldFibForP[key] != fibEntryForP[key]:
            print("fib changed!")
            return True
    print("fib did not change")
    return False
def removeExtraResults(results):
    dups = []
    for win1,op1,lose1 in results:
        for win2, op2, lose2 in results:
            if win1 == win2 and op1 != op2 and lose1 == lose2:
                dups.append ((win1,op1,lose1))
                dups.append((win2,op2,lose2))
    removals = []
    for d1 in dups:
        for d2 in dups:
            if d1[1] == '>=':
                if d1 not in removals:
                    removals.append(d1)
            if d2[1] == '>=':
                if d2 not in removals:
                    removals.append(d2)
    for r in removals:
        results.remove(r)
    return results

def findRelation(a,b,results):
    found = []
    for result in results:
        if result[0] == a and result[1]!= '>=' and result[2] == b:
            found.append(result)
    return found

def checkRight (parsed_pref_results):
    changeTo = []
    for result in parsed_pref_results:
        a = result[0]
        op = result[1]
        b = result[2]
        if op == ">=":
            print('examining ',result)
            #find other conditions with b that are not >=
            bcRelations = []
            #find b ? c relation 
            for b2, op2, c in parsed_pref_results:
                #ignore same result
                if result[0]==b2 and result[1] == op2 and result[2] == c:
                    continue

                if op2 != '>=' and b == c:
                    bcRelations.append((b2,op2,c))
            #find a ? c relation 
            print('bc relations', bcRelations)
            acRelations = []
            for a2, acOp, c2 in bcRelations:
                acRelations = findRelation(a2,c2,parsed_pref_results) 
            print('ac relations: ',acRelations)
            if len (acRelations) == 0 :
                print("could not determine relationship for ",result)
                continue
            if len (acRelations) > 1:
                print('how do i do multiple relations?')
                #exit(0)
            for acRelation in acRelations:
                #ignore >=
                change = (result[0], acRelations[0][1], result[2])
                changeTo.append((result,change)) 
                break
    return changeTo

def check_if_preference_is_done(local_pref_results):
    parsed_pref_results=local_pref_results.copy()
    #exit(0)
    done = False
    
    while not done:
        changes = False
        for local_pref_result in parsed_pref_results:
            results_to_remove = []
            results_to_add = []
            original_winner = local_pref_result[0]
            original_op = local_pref_result[1]
            original_loser = local_pref_result[2]
            
            for checker_pref_result in parsed_pref_results:
                checker_winner = checker_pref_result[0]
                checker_op = checker_pref_result[1]
                checker_loser = checker_pref_result[2]
                #if (a, ? , b) and (b, ?, a)
                if original_winner == checker_loser and original_loser==checker_winner: 
                    results_to_remove.append(local_pref_result)
                    results_to_remove.append(checker_pref_result)
                    to_add = (original_winner,'=',original_loser)
                    if to_add not in results_to_add:
                        results_to_add.append(to_add)
                    changes = True
                    
            if changes: 
                break
        if changes: 
            
            #remove all results_to_remove from local_pref_results
            for result in results_to_remove:
                try:
                    parsed_pref_results.remove(result)
                except:
                    pass
                    #print('already removed ', result)
            #append all results_to_add to local_pref_results
            for result in results_to_add:
                parsed_pref_results.append(result)
        else:
            done = True

    
    changeTo = checkRight(parsed_pref_results)
    #checkRight(results)
    
    for oldResult,newResult in changeTo:
        parsed_pref_results.remove(oldResult)
        parsed_pref_results.append(newResult)
    return parsed_pref_results


def getAllNeighbors(local_pref_results):
    allNeighbors = set()
    for w,o,l in local_pref_results:
        allNeighbors.add(w)
        allNeighbors.add(l)
    return allNeighbors

def checkResultsPathDone(results):
    
    dgraph = networkx.DiGraph() 
    for result in results:
        a = result[0]
        op = result[1]
        b = result[2]
        if a not in dgraph.nodes:
            dgraph.add_node(a)
        if b not in dgraph.nodes:
            dgraph.add_node(b)
        if op == '=':
            dgraph.add_edge(a,b)
            dgraph.add_edge(b,a)
        if op  =='>':
            dgraph.add_edge(a,b)
    
    for nodeA in dgraph.nodes:
        for nodeB in dgraph.nodes:
            if nodeA == nodeB:
                continue
            try:
                sp = networkx.shortest_path(dgraph,nodeA,nodeB)
                #print(sp)
            except networkx.exception.NetworkXNoPath :
                print("no path between ",nodeA,nodeB)
                try:
                    sp = networkx.shortest_path(dgraph,nodeB,nodeA)
                except:
                    print("reverse check no path between ",nodeB,nodeA)
                
                    return False
    return True

def findElemsInTuple(results,a):
    """returns a list of things sorted by the winner"""
    found = []
    #print('finding ',a,'in ',results)
    for result in results:
        if result[0] == a :
            found.append(result)
    return found

def doesResultAlreadyExist(someDict,winner,loser):
    for op1 in someDict[winner]:    
        losers1 = someDict[winner][op1]
        for l1 in losers1:
            if l1 == loser:
                return True
    return False
                
            

def inferRelationship(results):
    someDict = {}
    for win,op,loser in results:
        if win not in someDict.keys():
            someDict[win] = {}
        if op not in someDict[win].keys():
            someDict[win][op] = [] 
        if loser not in someDict[win][op]:
            someDict[win][op].append(loser)
    print('original ')
    print(someDict)
    for winner1 in someDict:
        for op1 in someDict[winner1]:    
            losers1 = someDict[winner1][op1]
            for winner2 in someDict:
                #ignore duplicates
                if winner1 == winner2:
                    continue
                found = False
                for l1 in losers1:
                    if l1 == winner2:
                        found = True
                        break
                if not found:
                    continue

                for op2 in someDict[winner2]:
                    
                    
                    losers2 = someDict[winner2][op2]
                    
                    
                    #cases
                    #a > b > c
                    #a > b = c
                    #a = b = c
                    #a = b > c

                    #a >=b >= c 
                    #a >= c 

                    if (op1 == '>'or op1 == '=') and (op2 == '>' or op2 =='='):
                        
                        for l2 in losers2:
                            if l2 not in losers1:#if not doesResultAlreadyExist(someDict,winner1,l2) and l2 not in losers1:
                                losers1.append(l2)
                    if op1 == '>=' and (op2 == '>' or op2 == '='):
                        for l2 in losers2:
                            if l2 not in losers1:#if not doesResultAlreadyExist(someDict,winner1,l2) and l2 not in losers1:
                                losers1.append(l2)
                    if (op1 == '=' or op1 =='>') and op2 == ">=":
                        for l2 in losers2:
                            if l2 not in losers1:#if not doesResultAlreadyExist(someDict,winner1,l2) and l2 not in losers1:
                                losers1.append(l2)
                    if op1 == '>=' and op2 == '>=':
                        for l2 in losers2:
                            if l2 not in losers1:#not doesResultAlreadyExist(someDict,winner1,l2) and l2 not in losers1:
                                losers1.append(l2)
    #parse it back into tuple form
    newResults = []
    for winner in someDict:
        for op in someDict[winner]:    
            for loser in someDict[winner][op]:
                newResults.append((winner,op,loser))
    #check for bad (a ? a) 
    remove = []
    for w,o,l in newResults:
        if w == l:
            remove.append((w,o,l))
        #continue
    for r in remove:
        newResults.remove(r)
           #also remove extrainius >=
    newResults = removeExtraResults(newResults)
    remove = []
    #This section:
    # dont store results if we have already found one previously
    for w1,op1,l1 in results:
        for w2,op2,l2 in newResults:
            if w1 == w2 and op1 == op2 and l1 == l2:
                continue
            if w1 == w2 and l1 == l2 and op1 != op2:
                remove.append((w2,op2,l2))
    for r in remove:
        try:
            newResults.remove(r)
        except:
            pass
    return newResults
    # print('infering relationships')
    # elemsToAdd = []
    # for result in results: 
    #     #print('examining first ',result)
    #     win1 = result[0]

    #     for secondResult in results:
    #         #print('examining second ',secondResult)
    #         win2 = secondResult[0]
    #         loser2 = secondResult[2]
    #         if result == secondResult:
    #             continue
    #         if win1 == win2:
    #             elemsWithLoserAsWinner = findElemsInTuple(results, loser2)
    #             #print('elems with loser as winner',elemsWithLoserAsWinner)
    #             for elem in elemsWithLoserAsWinner:
    #                 if win1 != elem[2]:
    #                     elemToAdd = (win1,elem[1],elem[2])
    #                     elemsToAdd.append(elemToAdd)
    # print('returning ',len(elemsToAdd))
    
    return elemsToAdd
#tsStart="2024-03-09T00:00:00"
# tsStart="2024-03-20T00:00:00"

# tsStart="2024-02-22T00:00:00"
#end time is 2 hours after the start time 

from matplotlib import pyplot    
def plotTuples(tuples):
    dgraph = networkx.DiGraph()
    for result in tuples:
        a = result[0]
        op = result[1]
        b = result[2]
        if a not in dgraph.nodes:
            dgraph.add_node(a)
        if b not in dgraph.nodes:
            dgraph.add_node(b)
        if op == '=':
            dgraph.add_edge(a,b)
            dgraph.add_edge(b,a)
        if op  =='>':
            dgraph.add_edge(a,b)   
    plt = pyplot
    networkx.draw(dgraph,with_labels=True)
    plt.show() 

#     check to see if local_pref_results contains all peers of the observer. 

#print(sortedUpdates[:10])
#fibEntryForP = pickle.load(open(f'pickles/fibEntryForP-{tsEnd}.pickle','rb'))

#get_more_data(results,tsStart,tsEnd,fibEntryForP)

    

#     Download the fib for the end_time 
#     Find the entry for prefix P. 
#     if the neighbor in this entry is not a winner in the results or there exists a neighbor that we dont have data for yet. 

#     download updates from start_time to end_time containing prefix P 
#     do compare_updates (updates, results)

# Find and Download updates from time T-2 hours to T that are annoucing prefix P. 

# local_pref_results = []
# do compare_updates(updates,results)



# loop: do we have enough results to find the local preference? 
#     if either of the following are False, we need to collect more data. 
#     check to see if local_pref_results contains all peers of the observer. 
#     check to see if local_pref_results contains only '>' and '=' values:

#     if both True:
#         done. continue to hijack testing
#     else:
#         local_pref_results = get_more_data(local_pref_results)
#         check_if_preference_is_done(local_pref_results)        

# function get_more_data (results,start_time, end_time):     
    
#     start_time = start_time - 2 hours
#     end_time = end_time - 2 hours

#     Download the fib for the end_time 
#     Find the entry for prefix P. 
#     if the neighbor in this entry is not a winner in the results or there exists a neighbor that we dont have data for yet. 

#     download updates from start_time to end_time containing prefix P 
#     do compare_updates (updates, results)
def check_for_end_duplicates(local_pref_results):
    for w,o,l in local_pref_results:
        cnt = 0
        for w2,o2,l2 in local_pref_results:
            if w2 == w and l ==l2:
                cnt+=1
        if cnt >1:
            return False
    return True



# ~~~~~Hijack Testing~~~~~~

def findLocalPref(benign_neighbor,hijacker_neighbor,dgraph):
    #print(dgraph.nodes())
    #print(benign_neighbor,hijacker_neighbor)
    A = str(benign_neighbor)
    B = str(hijacker_neighbor)
    # if A not in dgraph.nodes():
    #     print(A,'not in graph')
    #     return None
    # if B not in dgraph.nodes():
    #     print(B,'not in graph')
    #     return None
    if not dgraph.has_node(A) and not dgraph.has_node(B):
        print(A,B,'are not in graph!')
        return None
    
    
    is_A_greater_than_B = False
    is_B_greater_than_A = False
    try:
        #path_AB = networkx.has_path(dgraph,A,B)
        
        #find if a > b at least
        path_AB = networkx.shortest_path(dgraph,A,B)
        is_A_greater_than_B = True
    except networkx.exception.NetworkXNoPath: 
        #print("AB exception")
        pass    
    # except networkx.exception.NodeNotFound:
    #     print('node not found!')
    #     print(dgraph.nodes(),A,B)
    #     # print(parsed_pref_results)
    #     # plotTuples(parsed_pref_results)
    #     exit(0)
    try:
        #find if b>a
        #path_BA = networkx.has_path(dgraph,B,A)
        path_BA = networkx.shortest_path(dgraph,B,A)
        is_B_greater_than_A = True
    except:
        #print('BA exception')
        pass
    if is_A_greater_than_B and is_B_greater_than_A:
        return (A,"=",B)
        pass #they are equal
    if is_A_greater_than_B:
        return (A,">",B)
    if is_B_greater_than_A:
        return (B,">",A)
    print("cannot reason about ",A,B)
    return None
    
     #       return None
    
    for result in parsed_pref_results:
        if result[0] == benign_neighbor and result[2] == hijacker_neighbor:
            return result
        if result[0] == hijacker_neighbor and result[2] == benign_neighbor:
            return result
    return None
def createDiGraph(results):
    dgraph = networkx.DiGraph() 
    for result in results:
        a = str(result[0])
        op = result[1]
        b = str(result[2])
        #if a not in dgraph.nodes:
        dgraph.add_node(a)
        #if b not in dgraph.nodes:
        dgraph.add_node(b)
        if op == '=':
            dgraph.add_edge(a,b)
            dgraph.add_edge(b,a)
        if op  =='>':
            dgraph.add_edge(a,b)
    return dgraph
def storeResult(resultsDict,hijackerAS,victimAS,success,reason):
    if hijackerAS not in resultsDict:
        resultsDict[hijackerAS] = {'success':{'count':0, 'victims':[],'reasonsCount':{'local_pref':0,'as_path':0,'origin':0,'hot_potato':0}},
                                   'fails':{'count':0, 'victims':[],'reasonsCount':{'local_pref':0,'as_path':0,'origin':0,'hot_potato':0}},
                                   'ties':{'count':0, 'victims':[],'reasonsCount':{'local_pref':0,'as_path':0,'origin':0,'hot_potato':0}}}
    
    if success == True:
        resultsDict[hijackerAS]['success']['count']+=1
        resultsDict[hijackerAS]['success']['reasonsCount'][reason]+=1
        if (victimAS,reason) not in resultsDict[hijackerAS]['success']['victims']:
            resultsDict[hijackerAS]['success']['victims'].append((victimAS,reason))
            
    if success == False:
        resultsDict[hijackerAS]['fails']['count']+=1
        resultsDict[hijackerAS]['fails']['reasonsCount'][reason]+=1            
        if (victimAS,reason) not in resultsDict[hijackerAS]['fails']['victims']:
            resultsDict[hijackerAS]['fails']['victims'].append((victimAS,reason))
            
    if success =='tie':
        resultsDict[hijackerAS]['ties']['count']+=1
        resultsDict[hijackerAS]['ties']['reasonsCount'][reason]+=1            
        if (victimAS,reason) not in resultsDict[hijackerAS]['ties']['victims']:
            resultsDict[hijackerAS]['ties']['victims'].append((victimAS,reason))
            
# download updates from time T-i  to time T
# download the FIB for observer O at time T. 
# let fibEntry = the entry for prefix P in the FIB.


import requests
def findPeerNeighbors(tsStart,observerASN,addV4,addV6):
    print('finding peer neighbors')
    #masterPeers = policies.getMasterPeers()
    #peers = masterPeers[collector]['peers']
    # for peerASN,peerIP in peers:
    #     if ':' in peerIP:
    #         continue
        #url=f"https://stat.ripe.net/data/asn-neighbours/data.json?resource=AS136106&query_time=2024-03-31T00:00:00"
    url=f"https://stat.ripe.net/data/asn-neighbours/data.json?resource=AS{observerASN}&query_time={tsStart}"
    nset = set()
    # print(url)
    # exit(0)
    resp = requests.get(url)
    #print(resp.text)
    try:
        js = resp.json()
    except:
        print("js exception for ")#,peerIP, peerASN)
        #continue
        
# print(peerASN,js.keys(),js['messages'])
    #exit(0)
    try:
        neighbors = js['data']['neighbours']
    except:
        return
        #exit(0)
        #print('neighbor error for',peerASN,peerIP, 'data:', js['data'])
    for neighbor in neighbors:
        if addV4:
            if neighbor['v4_peers'] == 0:
                continue
        if addV6:
            if neighbor['v6_peers'] == 0:
                continue
        nset.add(neighbor['asn'])
    #print(peerASN,peerIP,len(nset))
    #if os.path.exists('pickles/neighbors/')
    return nset

def findUpdateThatWasAccepted(newUpdates,fibEntryForP):
    for update in newUpdates:
        for key in update:
            if key == 'timestamp': continue
            if update[key]==fibEntryForP[key]:
                return update['timestamp']
    return None
import time    
from random import uniform
def main(collector=None,observerASN=None,observerIP=None,prefixP=None,tsStart=None,maxDays=None):
    global pickleDir
    global cacheDir
    pickleDir , cacheDir = helpers.loadConfig()
    if collector == None:
        collector = sys.argv[1]
        observerASN = sys.argv[2]#testSet[tNum][1]
        observerIP = sys.argv[3]#testSet[tNum][2]
        prefixP = sys.argv[4]
        tsStart=sys.argv[5]
        maxDays= int(sys.argv[6])
    else:
        #sleep a random amount of time to slightly alter file access frequency
        time.sleep(uniform(.1,1))
    # prefixP = '185.228.94.0/24'
    # collector = 'route-views.sg'
    # tsStart="2024-03-30T00:00:00"
    # maxDays= 60
    #example route-views.sg 7713 27.111.228.134 185.228.94.0/24 2024-03-30T00:00:00 60
    # collector = sys.argv[1]
    # observerASN = sys.argv[2]#testSet[tNum][1]
    # observerIP = sys.argv[3]#testSet[tNum][2]
    # prefixP = sys.argv[4]
    # tsStart=sys.argv[5]
    # maxDays= int(sys.argv[6])
    
    
    
    tNum =4

    testSet = [(970576, '38880', '27.111.228.169'),
            (964275, '18106', '27.111.228.6'),
            (959649, '132337', '27.111.228.134'),
            (952239, '7713', '27.111.228.77'),
            (952239, '7713', '27.111.228.155'),
            (950246, '9002', '27.111.229.103'),
            (950104, '24482', '27.111.228.159'),
            (947633, '58511', '27.111.229.175'),
            (947047, '49544', '27.111.229.225'),
            (947028, '16552', '27.111.229.252'),
            (945308, '199524', '27.111.228.222'),
            (943960, '3257', '27.111.228.217'),
            (941822, '8220', '27.111.229.123'),
            (938585, '3491', '27.111.228.43')]
    #have to create FIB at time T in order to have accurate results 
    #otherwise it might change it (unless i ensure that it doesnt)
    #observerASN = testSet[tNum][1]
    #observerIP = testSet[tNum][2]#'64.71.137.241'
    #print(observerASN,observerIP)

    #tsStart="2024-03-24T00:00:00"
    neighbors = findPeerNeighbors(tsStart,observerASN,addV4=True,addV6=False)
    MIN_NEIGHBORS = 40#len(neighbors) #TODO
    global hoursToAdd
    numberPeerNeighbors = None #TODO
    if 'rrc' in collector:
        hoursToAdd=8
    else:
        hoursToAdd=2

    tsEnd = helpers.addTime(tsStart,hoursToAdd=hoursToAdd)
    originalStart = tsStart
    originalEnd = tsEnd

    foundUpdates = False
    foundEnoughUpdatesForPolicy = False
    local_pref_results = []
    
    #dont re-run tests that have already been completed.
    if os.path.exists(pickleDir + f'newTestResults2/{collector}-{observerIP}-{prefixP.replace('/','-')}'):
        print('these tests have already been ran!')
        resultsDict = pickle.load(open(pickleDir+f'newTestResults2/{collector}-{observerIP}-{prefixP.replace('/','-')}','rb'))
        if len(resultsDict) == 0:
            resultsDict = {}
            print("empty dict, no results found, going again.")
        else: 
            return
    
    if 'rrc' in collector:
        numInDay = 3 #rrc collectors get RIBS 8 hours apart so 8*3=24*maxDays=number of max days to search
    else:
        numInDay = 12#route-view collectors get ribs 2 hours apart. 

    maxSearch = maxDays*numInDay 
    cnt =0
    updatesToConsider = []
    oldFibForP = {}
    compared = False
    #~~~ main loop ~~~#
    while not foundEnoughUpdatesForPolicy:
        while not foundUpdates:
            if cnt >= maxSearch:
                print('could not find enough information in ',maxSearch,'tries')
                with open('failed_simple_tests.txt','a+') as f:
                    f.write(f"{collector},{observerIP},{observerASN},{prefixP} failed by max Search {maxSearch}")
                    f.write('\n')
                return 
                #exit(0)
            #every 10 iterations if we're not done reduce min neighbors by 1
            if cnt %10 == 0 and cnt!=0:
                MIN_NEIGHBORS = MIN_NEIGHBORS-5
            cnt+=1 
            #spawn 5 threads and do this (thread thing really only useful for rrcs i think)
            fibEntryForP,foundStart,foundEnd = findFibEntryForP(tsStart,tsEnd,prefixP,observerIP,collector)
            
            if fibEntryForP == None:
                print('no FIB found in 10 days ')
                print('or there was a problem with the query')
                with open('failed_simple_tests.txt','a+') as f:
                    f.write(f"{collector},{observerIP},{prefixP} failed by no fib in 6 days or problem with query")
                    f.write('\n')
                return
            #the 5 threads then do this 
            newUpdates = get_updates_for_p(foundStart, foundEnd,prefixP,observerIP,collector)
            timestampOfUpdate = findUpdateThatWasAccepted(newUpdates,fibEntryForP)
            #find updates from this time to the endtime 
            updatesToConsider = []
            if timestampOfUpdate != None:
                for update in newUpdates:
                    if update['timestamp'] > timestampOfUpdate and update['timestamp'] < foundEnd:
                        updatesToConsider.append(update)
            else:
                updatesToConsider = newUpdates
            #<TODO> find the fib entry in the Updates here
            #use only the ones from the fib entry to the end time 
            #if the fib entry is not found in the updates, necessarily implies there are no withdrawls, so we can use all of them
            #check each thread for if the fib changed from the old one, 
            #if no just append updates. 
            # if yes, do the ones that didnt change 
            # then do the ones that did 
            # if didFibChange(oldFibForP,fibEntryForP):
                
            #     updates = []
            #     oldFibForP = fibEntryForP
            
            # for newUpdate in newUpdates:
            #     updates.append(newUpdate)
            # updates = get_updates_for_p(tsStart, tsEnd,prefixP,observerIP,collector)
            if len(updatesToConsider) == 0:
                print("no updates found, go again")
                tsStart = helpers.subtractTime(tsStart,hours=hoursToAdd)
                tsEnd = helpers.subtractTime(tsEnd,hours=hoursToAdd)
            else:
                foundUpdates = True
        foundUpdates = False
        tsStart = helpers.subtractTime(tsStart,hours=2)
        tsEnd = helpers.subtractTime(tsEnd,hours=2)
        print(f'comparing {len(updates)} updates')
        local_pref_results = compare_updates(updatesToConsider,local_pref_results,fibEntryForP)
        #print('local prefs found: ', local_pref_results)
        # if len(local_pref_results) > 0 :
        #     exit(0)
        print("checking if prefs is done")
        print(local_pref_results)
        #local_pref_results = removeExtraResults(local_pref_results)
        #parsed_pref_results = removeExtraResults(parsed_pref_results)
        #infers a >b >c 
        local_pref_results = check_if_preference_is_done(local_pref_results)
        
        #local_pref_results = parsed_pref_results
        #print("after ",parsed_pref_results)
       # print("after ",local_pref_results)
        #print(local_pref_results)
        # exit(0)
        
    #    doneFlag=  True
        #doneFlag = checkResultsPathDone(parsed_pref_results)
        doneFlag = checkResultsPathDone(local_pref_results)
        for result in local_pref_results:
        #for result in parsed_pref_results:
            print(result, result[1])
            if result[1] == '>=':
                print("not done yet!")
        
                doneFlag = False
                break
        allNeighbors = getAllNeighbors(local_pref_results)
        if MIN_NEIGHBORS <=0:#removeforolddata
            MIN_NEIGHBORS = 10
        if len(allNeighbors)>= MIN_NEIGHBORS:
            if doneFlag:
                doneFlag=True
        else:
            print('not done by minNeighbors ', len(allNeighbors), MIN_NEIGHBORS)
            doneFlag = False
        
        
        tsStart = helpers.subtractTime(foundStart,hours=hoursToAdd)
        tsEnd = helpers.subtractTime(foundEnd,hours=hoursToAdd)
        if doneFlag:
            print('were done!')
            foundEnoughUpdatesForPolicy = True
            break

    print(local_pref_results)
    #print('parsed',parsed_pref_results)
    for p in local_pref_results:
        print(p)
    pickle.dump(local_pref_results,open(pickleDir+f'/pref_results/{collector}-{observerIP}-{prefixP.replace('/','-')}','wb'))
    # return
    print("this took:",cnt*2,'hours')
    
    #exit(0)
    # updatesForP = get_updates_for_p(originalStart,originalEnd,prefixP,observerIP,collector)
    # nSet = set()
    # updates = get_all_updates(originalStart,originalEnd,observerIP,collector)
    # for update in updates:
    #     nSet.add(helpers.findNeighborInUpdate(update))
    # print(nSet)
    # exit(0)
    allNeighbors = getAllNeighbors(local_pref_results)
    resultsDict = {}


    #do this n times to get more results
    numTests =1
    dgraph = createDiGraph(local_pref_results)
    for i in range(numTests): 
        if i != 0:
            print(f'running new fib {i}/{numTests}')
            originalStart = helpers.subtractTime(originalStart,hours=hoursToAdd*i)
            originalEnd = helpers.subtractTime(originalEnd,hours=hoursToAdd*i)
        fibEntryForP,foundStart,foundEnd = findFibEntryForP(originalStart,originalEnd,prefixP,observerIP,collector)
        updates = get_all_updates(foundStart,foundEnd,observerIP,collector)
        updatesForP = get_updates_for_p(foundStart,foundEnd,prefixP,observerIP,collector)

        if len(updates) ==0:
            continue
        if len(updatesForP) ==0:
            continue
        #updates = get_updates_for_p(originalStart,originalEnd,prefixP,observerIP,collector)#get_all_updates(originalStart,originalEnd,observerIP,collector)
        # note: time T-i to T are in the range of updates and fibs previously gathered. For example time T-2hours to time T. 

        #single result is this 
        #{"hijacker_neighbor":hijacker_neighbor,"victim_neighbor":fibNeighbor,'result':False} 
        #{hijackerAS: 'successes': {count: 0, victims:[(victimAS,reason)]}
        #            'fails': {count: 0, victims:[(victimAS,reason)]}}
        #             ties: {count: 0, victims:[(victimAS,reason)]}

        
        bupdates = [] 
        bct = 1
        for benign_update in updatesForP:
            print(f'examining {bct}/{len(updatesForP)}')
            bct+=1
        #go back to buptdate thing 
        # bupdates.append(fibEntryForP)
        # for benign_update in bupdates:
            benign_neighbor = helpers.findNeighborInUpdate(benign_update) #the neighbor that sent the benign_update to the observer.
            #cant reason about a neighbor not in all neighbors
            if benign_neighbor not in allNeighbors:
                continue
            victimAS = benign_update['origin_asns']
            if len(victimAS)==1:
                victimAS = victimAS[0]

            for hijacker_update in updates:
                hijackerAS = hijacker_update['origin_asns']
                if len(hijackerAS)==1:
                    hijackerAS = hijackerAS[0]
                #ignore multihome hijackers
                else:
                    continue
                if benign_update == hijacker_update:
                    continue
                
                hijacker_neighbor = helpers.findNeighborInUpdate(hijacker_update)#the neighbor that sent the hijacker_update to the observer.
                fib_neighbor = helpers.getNeighborFromUpdate(fibEntryForP)#the neighbor that sent the update that was accepted into the FIB. 
                
                if hijacker_neighbor not in allNeighbors:
                    continue
                if benign_neighbor not in allNeighbors:
                    continue

                #if they have the same neighbor, they'll have the same local preference, so skip this. 
                if benign_neighbor != hijacker_neighbor:
                    #print('checking local pref ')
                #the entry in local_pref_results that contains the benign_neighbor and hijacker_neighbor.
                    local_pref_result  = findLocalPref(benign_neighbor,hijacker_neighbor,dgraph)
                    
                    #print('found ', benign_neighbor, hijacker_neighbor,local_pref_result)
                    #if benign_neighbor ('174', '>', '8529')
                    if local_pref_result == None:
                        print('why is there no local pref result for',benign_neighbor, hijacker_neighbor)
                        print(local_pref_results)
                        print(allNeighbors)
                        exit(0)
                        continue
                        
                    winningNeighbor = local_pref_result[0]
                    operation = local_pref_result[1]
                    losingNeighbor = local_pref_result[2]
                    if operation == '>':
                        if winningNeighbor == benign_neighbor:
                            #hijacker loses, store this result.
                            storeResult(resultsDict,hijackerAS,victimAS,False,'local_pref')
                            continue
                        if losingNeighbor == benign_neighbor:
                            #hijacker wins, store this result
                            storeResult(resultsDict,hijackerAS,victimAS,True,'local_pref')
                            
                            continue 
                    elif operation != '=':
                        print(local_pref_result,benign_neighbor,hijacker_neighbor)
                        print('there was a problem in the local_pref_results')# since the only allowed values here are > or =. In addition, we can only reason about > and = cases. during the finding of 'enough' information, the local_pref_results array will be transformed to only contain values of < or =. ')
                        exit(0)
                    
                #implicit operation is = case 
                benign_path = splitAsPathFromUpdate(benign_update) #the AS Path in benign_update
                hijacker_path = splitAsPathFromUpdate(hijacker_update) #the AS Path in hijacker_update
                # print('examining AS Path:')
                # print('begnign ', len(benign_path))
                # print('hijackers', len(hijacker_path))
                
                if len(benign_path) < len(hijacker_path):
                    
                    #hijacker loses, store this result.
                    storeResult(resultsDict,hijackerAS,victimAS,False,'as_path')
                    continue 
                if len(benign_path) > len(hijacker_path):
                    #hijacker wins, store this result. 
                    storeResult(resultsDict,hijackerAS,victimAS,True,'as_path')
                    continue
                #implicit  len(benign_path) == len(hijacker_path):
                            
                benign_origin =  benign_update['origin']#the origin_type in benign_update
                hijacker_origin = hijacker_update['origin']#the origin_type in hijacker_update
                    
                #compare benign_origin and hijacker_origin and store the result if they are different. if they are the same, continue on. basically we just use a dictionary with assigned values to avoid a big if/else if block

                origin_types_dict = {'IGP':3, 'EGP':2, 'INCOMPLETE':1}
                if origin_types_dict[benign_origin] > origin_types_dict[hijacker_origin]:
                    
                    #Hijacker loses, store this result. 
                    storeResult(resultsDict,hijackerAS,victimAS,False,'origin')
                    continue
                    
                elif origin_types_dict[benign_origin] < origin_types_dict[hijacker_origin]:
                    #Hijacker wins, store this result. 
                    storeResult(resultsDict,hijackerAS,victimAS,True,'origin')
                    continue
                
        #             #hot potato preference section 
                #cant do hot potato on a neighbor thats not in the fib
                if fib_neighbor != benign_neighbor and fib_neighbor != hijacker_neighbor:
                   continue
                if fib_neighbor == benign_neighbor and fib_neighbor == hijacker_neighbor:
                    
                    #we dont know anything, this is a tie. Store this result. 
                    storeResult(resultsDict,hijackerAS,victimAS,None,'hot_potato')
                    continue
                elif fib_neighbor == benign_neighbor:

                    #hijacker loses, store this result
                    storeResult(resultsDict,hijackerAS,victimAS,False,'hot_potato')
                    continue
                elif fib_neighbor == hijacker_neighbor:
                    
                    #hijacker wins, store this result.
                    storeResult(resultsDict,hijackerAS,victimAS,True,'hot_potato')
                    continue
                else:
                    #storeResult()
                    print('cant reason about neighbor not in fib at this point in time. ')
                    # print('something probably went wrong in the training process ')
                    # print(fib_neighbor)
                    # print(benign_neighbor)
                    # print(hijacker_neighbor)
                    # exit(0)
                    continue
                    #exit(0)
                    #neither update == fib_neighbor, which doesnt make sense. something probably went wrong in the training process. Print an error. 
        originalStart = helpers.subtractTime(originalStart,hours=hoursToAdd)
        originalEnd = helpers.subtractTime(originalEnd,hours=hoursToAdd)
    print('dumping results!')
    pickle.dump(resultsDict,open(pickleDir+f'newTestResults2/{collector}-{observerIP}-{prefixP.replace('/','-')}','wb'))
    print(resultsDict)
    someWin = 0
    for win in resultsDict:
        #print(win)#,resultsDict[win])  
        if resultsDict[win]['success']['count'] !=0:
            print(win,resultsDict[win]['success'])
            someWin+=1
    if someWin == 0:
        print('no winners found =(')
        # for key in resultsDict[win].keys():
        #     if resultsDict[win][key]['count'] !=0:
                #print(key, resultsDict[win][key])
    #hopefully return helps with mutliprocessing this stuff 
    return
if __name__ == "__main__":
    main()
    # exit(0)