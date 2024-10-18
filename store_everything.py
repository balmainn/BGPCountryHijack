import helpers 
import statistics 
from datetime import datetime
import networkx
import math
from collections import OrderedDict
import pickle 

def discardKnownResults(knownResults,possibleNewResults):
    """discards results that we have already found"""
    #results to discard
    discard = []
    #go over each result, if we already have it, discard it. 
    for old_res in knownResults:
        for new_res in possibleNewResults:
            if new_res == old_res:
                discard.append(new_res)
    for d in discard:
        possibleNewResults.remove(d)

    return possibleNewResults

def extendWithGraphs(inequalities,useShortestPath=True):
    #print('extending with graphs!')
    
    if inequalities  == None:
        return inequalities, False
    G = networkx.DiGraph()    
    # Add inequalities to the graph
    for inique in inequalities:
        if len(inique) ==4:
            a, relation, b,timestamp = inique
        else:
            a, relation, b  = inique
        if relation =='>':
            G.add_node(a)
            G.add_node(b)
            G.add_edge(a,b,weight=1)
    
    #iterate over all a,b and see if a has a path to b.
    #if it does, then a>b.
    found = []
    for node_A in G.nodes():
        for node_B in G.nodes():
            if node_A == node_B:
                continue
            if networkx.has_path(G,node_A,node_B):
                if useShortestPath:
                    paths = networkx.all_shortest_paths(G,node_A,node_B)
                else:
                    paths = networkx.all_simple_paths(G,node_A,node_B)
                #paths are in the form of [a,b,c], we already know [a,b] so skip those. 
                for path in paths:
                    if len(path)<=2:
                        continue
                    if (node_A,'>',node_B) not in found:
                        found.append((node_A,'>',node_B))

    #check for new results that we dont know about                   
    newResults = []
    for f in found:
        if f not in inequalities:
            newResults.append(f)

    #discard the results we already know about
    newRes = discardKnownResults(inequalities,newResults)
    haveNewRes=False
    foundNewRes = False
    for res in newRes:
        haveNewRes = True
        inequalities.append(res)
        contras = helpers.findContradictions(inequalities)
        if len(contras)>0:
            inequalities.remove(res)
            haveNewRes = False
        if haveNewRes:
            foundNewRes = True
    #     contras = 
    return inequalities, foundNewRes
    #attempt to append new results to the inequalities
    #if it causes a contradiction or cycle, remove it. 
    haveNewRes = False
    for newR in newRes:
        if len(newR) == 4:
            a,r,b,tiemstamp = newR
        else:
            a,r,b = newR
        inequalities.append(newR)
        haveNewRes = True
        badChange,reason = helpers.detectBadChange_noexit(inequalities,'inner extend graphs',shouldPrint=True)
        if badChange:
            haveNewRes = False
            inequalities.remove(newR)
            if reason == 'cycles':
                #input('cycles?')
                if (b,r,a) not in inequalities:
                    haveNewRes = True
                    inequalities.append((b,r,a))                    
                badChange,reason = helpers.detectBadChange_noexit(inequalities,'inner extend graphs2',shouldPrint=True) 
                if badChange:
                    haveNewRes = False
                    inequalities.remove((b,r,a))
    #return the new inequalities as well as if we found any new results    
    return inequalities, haveNewRes

def findGreatestDiff(allUpdates):
    """find the time differences between evrey two updates"""
    tdiffs = []
    tdiff = float()
    for i in range(len(allUpdates)):
        update1 = allUpdates[i]
        try:
            update2 = allUpdates[i+1]
        except:
            break
        tdiff = update2['timestamp']-update1['timestamp']
        if tdiff not in tdiffs:
            tdiffs.append(tdiff)    
    #sort the list before returning so we ensure greater values are before lesser ones.        
    return sorted(tdiffs,reverse=True)

def splitUpdates(allUpdates):  
    """same as splitUpdatesMedian, but uses the greatest difference in times to split the updates into buckets"""
    print('spliting updates')
    if len(allUpdates)<=2:
        return []
    allUpdates = sorted(allUpdates,key=lambda x:x['timestamp'])        

    tdiffs = findGreatestDiff(allUpdates)
    
    print('tdiff',tdiffs[0],tdiffs[-1])
    new_buckets = []
    for tdiff in tdiffs:
        lastIndex = 0
        for i in range(len(allUpdates)):
            update1 = allUpdates[i]
            try:
                update2 = allUpdates[i+1]
            except:
                break
            updateDiff = update2['timestamp']-update1['timestamp']
    
            if updateDiff >= tdiff-0.005:
                if i == 0:
                    continue
                new_buckets.append(allUpdates[lastIndex:i])
                lastIndex = i
        #if we did not find a valid split based on the greatest time difference
        #use the next tdiff value
        if len(new_buckets)==0:
            print(tdiff,'not found, trying next')
        else:
            if lastIndex <len(allUpdates):
                new_buckets.append(allUpdates[lastIndex:len(allUpdates)])
            return new_buckets
    #if we couldnt find a way to split the updates, then theres a problem.    
    print('cant find tdiff')
    exit(0)

def splitUpdatesMedian(allUpdates): 
    """splits updates based on some value currently set to 3 seconds, 
    but this can be tailored to the updates based on tdiffs""" 
    print('spliting updates median')
    #sort the updates according to the timestamp. NOTE: update2 replaces update 1, so update2's timestamp should be >= update1's timestamp
    allUpdates = sorted(allUpdates,key=lambda x:x['timestamp'])        
    #if we only have 2 updates, then theres nothing left to compare after splitting, so just return empty lists
    if len(allUpdates)==2:
        return [],[]
    #tdiffs = findGreatestDiff(allUpdates)
    new_buckets = []
    tdiff = 1#.05 #1 worked well .25 worked well
    #index to keep track of where the last split occured
    lastIndex = 0
    for i in range(len(allUpdates)):
        update1 = allUpdates[i]
        try:
            update2 = allUpdates[i+1]
        except:
            break
        updateDiff = update2['timestamp']-update1['timestamp']

        #if the difference between two updates is >= 2.995, split the updates into two buckets.
        #the small amount is necessary because of float values
        if updateDiff >= tdiff-0.005:
            #dont split [0:0] cause it doesnt make sense
            if i == 0:
                continue
            new_buckets.append(allUpdates[lastIndex:i])
            lastIndex = i
    
    #if we still have more to append, do so. 
    if lastIndex <len(allUpdates):
        #print(i,lastIndex)
        new_buckets.append(allUpdates[lastIndex:len(allUpdates)])
        return new_buckets
    
    
    print('cant find tdiff')
    return [allUpdates]
def findActiveNeighbors(updates):
    """finds the active neighbors in a group of updates.
    if we see an update, it means the neighbor is up"""
    neighbors = set()
    for update in updates:
        neighbors.add(helpers.findNeighborInUpdate(update))
    return neighbors
def getPrefDict(updates):
    """sorts updates into their respective prefix via a dictionary
    these updates may need to be sorted again, since dictionaries dont guarentee insertion order"""
    prefDict = {}
    for update in updates:
        prefix = update['prefix']
        if prefix not in prefDict.keys():
            prefDict[prefix] = [] 
        prefDict[prefix].append(update)                
    return prefDict

def findOrigin_Asns(updates):
    """finds the origin asn for a group of updates
    this is meant to be used to ignore multihomed prefixes
    since two prefixes can have different origin ASNs.
    But multihomed ASes could use different paths, 
    which might mess with our results
    sometimes multihomed ASes dont use the origin_asns attribute
    which is why this function uses 3 different methods to find them (based on the if block)"""
    origins = set()

    for update in updates:
        as_path = update['as_path']
        origin_asns = update['origin_asns']
        #multiple asns as the origin are listed in the PATH
        if '{' in as_path:
            origin_asns = as_path.split('{')[1][:-1]
            for origin_asn in origin_asns:
                origins.add(origin_asn)
            continue
        #multiple origin ASNS not listed in the PATH, but are in the origin_asns attribute
        elif len(origin_asns) >1:
            for origin_asn in origin_asns:
                origins.add(origin_asn)
            continue
        else:
            origins.add(as_path.split(' ')[-1])
    return origins    
def removeDuplicateTimestamps(updates):
    """NOTE: only use this function wrt a prefix. 
    the existance of updates with the same timestamp 
    with two different prefixes doesnt mean anything
    however, prefix updates with the same timestamp we dont know who wins."""
    rem = []
    #first remove all duplicate updates
    updates = helpers.cleanUpdates(updates)
    
    #next, remove updates that have the same timestamp
    for i in range(len(updates)):
        update1 = updates[i]        
        for j in range(len(updates)):
            if i ==j:
                continue
            update2 = updates[j]
            if update1['timestamp']==update2['timestamp']:
                if update1 not in rem:
                    rem.append(update1)
                if update2 not in rem:
                    rem.append(update2)
    for r in rem:
        updates.remove(r)

    return updates
def testBucket(bucketUpdates,neighborsToFind = [],p_before_ranks=[]):
    """test a group of updates for a>b results.
    if neighborsTofind (list of specific neighbors we want a result for)
        is specified, then only examine updates that contain these neighbors"""
    #print('testing bucket') 
    bucketRes = []
    #find the neighbors that are present in the burst of updates
    neighbors = findActiveNeighbors(bucketUpdates)

    neighborsInBucket = []
    #if we're looking for specific neighbors
    if len(neighborsToFind)>0:
        for n in neighbors:
            for neighborToFind in neighborsToFind:
                if n == neighborToFind:
                    if n not in neighborsInBucket:
                        neighborsInBucket.append(n)
    
    #sort the updates by their respective prefix into a dictionary
    #we do this because comparing two different prefixes is meaningless on its own.
    prefDict = getPrefDict(bucketUpdates)
    prefList = []
    for prefix in prefDict:
        prefList.append(prefix)
    #shuffle(prefList)
    for prefix in prefList:
        #multihomed prefixes can take different paths, which may interfere with our results. 
        #specifically, load balancing 
        origin_asns = findOrigin_Asns(prefDict[prefix])
        if len(origin_asns) >=2:
            continue    
        #sort the updates based on their timestamp so update2 replaces update1
        someUpdates = sorted(prefDict[prefix],key=lambda x:x['timestamp'])
        if len(prefDict[prefix])<=1:
            continue
        #sometimes the collector/peer is busy and sends updates with the same timestamp
        #we cant reason about two updates with the same timestamp for the same prefix
        #so remove them. 
        someUpdates = removeDuplicateTimestamps(someUpdates)
        for i in range(len(someUpdates)):  
            update1 = someUpdates[i]
            try:
                update2 = someUpdates[i+1]
            except:
                break  
            # print(update1['timestamp'])
            # print(helpers.convertUpdateToTimestring(update1))
            # print(update2['timestamp'])
            # print(helpers.convertUpdateToTimestring(update2))
            # exit(0)
            
            #withdraw updates dont give us a result.
            #this should skip comparing update1 and update3 in the following scenario
            #update1: good, update2: W, update3: good
            if update1['elem_type'] == 'W' or update2['elem_type']=='W':
                continue
            #if we somehow find two updates with the same timestamp, there is a problem.
            if update1['timestamp'] == update2['timestamp']:
                print('found same timestamp')
                print(update1)
                print(update2)
                exit(0)
            
            #find the neighbor that sent the update
            update1Neighbor = helpers.findNeighborInUpdate(update1)
            update2Neighbor = helpers.findNeighborInUpdate(update2)
            #if they are the same, we cant learn anything so continue. 
            if update1Neighbor == update2Neighbor:
                continue
            #only find results related to the neighbors that we need (if specified)
            if len(neighborsToFind) >0:
                if update1Neighbor not in neighborsInBucket and update2Neighbor not in neighborsInBucket:
                    continue

            #find the as_path of the updates
            update1Path = helpers.splitASPathFromUpdate(update1)
            update2Path = helpers.splitASPathFromUpdate(update2)
            
            #skip if the neighbor is not active during the burst
            if update1Neighbor not in neighbors:
                continue 
            if update2Neighbor not in neighbors:
                continue 
            res = None
            if len(p_before_ranks)>0:
                # if not neighborsAreSameRank(update1Neighbor,update2Neighbor,p_before_ranks):
                # # print('skipping not in same rank')
                # # print(update1Neighbor,update2Neighbor)
                # # for i in range(len(p_before_ranks)):
                # #     print(i,p_before_ranks[i])
                #     continue
                if len(update1Path) != len(update2Path):
                    #print('skipping path len')
                    continue
                if not updatesHaveSameOrigin(update1,update2):
                    #print('skipping updates origin')
                    continue
                res = (update2Neighbor,'>',update1Neighbor)
                if res not in bucketRes:
                    bucketRes.append(res)
            else:
                if len(update2Path) > len(update1Path):
                    res = (update2Neighbor,'>',update1Neighbor,update2['timestamp'])
            #if we found a result thats not in the bucket's results, append it. 
            if res != None:
                bucketRes.append(res)
            #everyRes is mostly used for debugging and examining the big picture
            # this necessarily means that this list will contain contradictions and cycles.            
            if res not in everyRes and res != None:  
                everyRes.append(res)

    #if we didnt find any result in the bucket, then just return.
    if len(bucketRes)==0:
        return True, []
    
    #expand the results we have found using graph theory. 
    # innercnt = 0    
    # haveNewResults = True
    # while haveNewResults:
    #     bucketRes, haveNewResults = extendWithGraphs(bucketRes,useShortestPath=False)
    #     if innercnt > 10:
    #         input('this seems to be taking a while...?')
    #     innercnt+=1     

    #extendWithGraphs shouldnt produce a contradiction.
    #but just in case it does, remove them. 
    contras = helpers.findContradictions(bucketRes)  
    
    if len(contras) == 0:
        #print('no contras found')
        return True,bucketRes
    else:
        return False,''
    
    for c in contras:
        try:
            bucketRes.remove(c[0])
        except:
            pass
        try:
            bucketRes.remove(c[1])
        except:
            pass
  
    return True,bucketRes
def testBucketForNotAnd(bucketUpdates):
    """test a group of updates for a>b results.
    if neighborsTofind (list of specific neighbors we want a result for)
        is specified, then only examine updates that contain these neighbors"""
    #print('testing bucket') 
    bucketRes = []
    #find the neighbors that are present in the burst of updates
    neighbors = findActiveNeighbors(bucketUpdates)

    neighborsInBucket = []
    #if we're looking for specific neighbors

    
    #sort the updates by their respective prefix into a dictionary
    #we do this because comparing two different prefixes is meaningless on its own.
    prefDict = getPrefDict(bucketUpdates)
    prefList = []
    for prefix in prefDict:
        prefList.append(prefix)
    #shuffle(prefList)
    someDict = {}
    for prefix in prefList:
        
        #multihomed prefixes can take different paths, which may interfere with our results. 
        #specifically, load balancing 
        origin_asns = findOrigin_Asns(prefDict[prefix])
        if len(origin_asns) >=2:
            continue    
        #sort the updates based on their timestamp so update2 replaces update1
        someUpdates = sorted(prefDict[prefix],key=lambda x:x['timestamp'])
        if len(prefDict[prefix])<=1:
            continue
        #sometimes the collector/peer is busy and sends updates with the same timestamp
        #we cant reason about two updates with the same timestamp for the same prefix
        #so remove them. 
        someUpdates = removeDuplicateTimestamps(someUpdates)
        for i in range(len(someUpdates)):  
            update1 = someUpdates[i]
            try:
                update2 = someUpdates[i+1]
            except:
                break  
            # print(update1['timestamp'])
            # print(helpers.convertUpdateToTimestring(update1))
            # print(update2['timestamp'])
            # print(helpers.convertUpdateToTimestring(update2))
            # exit(0)
            
            #withdraw updates dont give us a result.
            #this should skip comparing update1 and update3 in the following scenario
            #update1: good, update2: W, update3: good
            if update1['elem_type'] == 'W' or update2['elem_type']=='W':
                continue
            #if we somehow find two updates with the same timestamp, there is a problem.
            if update1['timestamp'] == update2['timestamp']:
                print('found same timestamp')
                print(update1)
                print(update2)
                exit(0)
            
            #find the neighbor that sent the update
            update1Neighbor = helpers.findNeighborInUpdate(update1)
            update2Neighbor = helpers.findNeighborInUpdate(update2)
            #if they are the same, we cant learn anything so continue. 
            if update1Neighbor == update2Neighbor:
                continue
            #only find results related to the neighbors that we need (if specified)
           

            #find the as_path of the updates
            update1Path = helpers.splitASPathFromUpdate(update1)
            update2Path = helpers.splitASPathFromUpdate(update2)
            
            
            #skip if the neighbor is not active during the burst
            if update1Neighbor not in neighbors:
                continue 
            if update2Neighbor not in neighbors:
                continue 
            neighborT = (update2Neighbor,update1Neighbor)
            if neighborT not in someDict:
                someDict[neighborT] = []
            if len(update2Path) == len(update1Path):
                someDict[neighborT].append('not_as_path')
            if len(update2Path) < len(update1Path):
                someDict[neighborT].append('as_path_or_lp')
        for neighborT in someDict:
            results = someDict[neighborT]
            if len(results)<=1:
                continue
            if 'not_as_path' in results and 'as_path_or_lp' in results:
                res = (neighborT[0],'>',neighborT[1])
                if res not in bucketRes:
                    bucketRes.append(res)
  
    return True,bucketRes

def removeMultihomeASNS(allUpdates):
    #remove multihome ASNs
    rem = []
    for update in allUpdates:
        if len(update['origin_asns'])>1:
            if update not in rem:
                rem.append(update)
    for r in rem:
        allUpdates.remove(r)        
    allUpdates = sorted(allUpdates,key=lambda x: x['timestamp'],reverse=True)
    return allUpdates

def startProcess(startTime,endTime,observerIP,collector, neighborsToFind = [],p_before_ranks=[],doNotAnd=False):
    
    allUpdates = helpers.getUpdatesForCollectorObserverAndTime(startTime,endTime,collector,observerIP)    
    
    #print('not helpers')
    #print('found',len(allUpdates),'updates')
    
    #remove multihome ASNs
    rem = []
    for update in allUpdates:
        if len(update['origin_asns'])>1:
            if update not in rem:
                rem.append(update)
    for r in rem:
        allUpdates.remove(r)        
    allUpdates = sorted(allUpdates,key=lambda x: x['timestamp'])
    if len (allUpdates)<=2:
        return None,None
    buckets = [] 
    #split the updates into buckets based on a 3 second difference between two updates 
    buckets = splitUpdatesMedian(allUpdates)
    print('start bucket len ', len(buckets))
    
    allRes = []
    recurse = True
    newBuckets = []
    rec = 0 
    splitBuckets = buckets
    while recurse:
        rec +=1 
        #print('recursing ',rec)
        #only do this a maximum of 50 times (infinite loop prevention)
        if rec > 50:
            break
        b = 1
        
        if len(newBuckets)>0:
            buckets = newBuckets
        if len(newBuckets)==0:
            newBuckets=buckets 
        #go through the buckets and collect results for each            
        for singleBucket in buckets:
            
            #remove the bucket we are working on from the buckets we need to do
            newBuckets.remove(singleBucket)
            #exit(0)
        
            #print(f'working on {b}/{len(buckets)} with len',len(singleBucket))
            b+=1
            #if we only have 1 update in the bucket, dont work on it, just continue
            if len(singleBucket) <=1:
                continue
            
            #if we are looking for specific neighbors, 
            #only gather results relating to that. 
            #otherwise gather all results
            if doNotAnd:
                noContras,values = testBucketForNotAnd(singleBucket)
            elif len (p_before_ranks) >0:
                if len(neighborsToFind)>1:
                    noContras,values = testBucket(singleBucket,neighborsToFind=neighborsToFind,p_before_ranks=p_before_ranks)
                else:
                    noContras,values = testBucket(singleBucket,p_before_ranks=p_before_ranks)
            elif len(neighborsToFind)>1:
                noContras,values = testBucket(singleBucket,neighborsToFind)
            else:
                noContras,values = testBucket(singleBucket)
            #if we found a contradiction, we need to split the bucket again (else block)                
            #otherwise we combine results from the bucket together
            if noContras:
                #if we have results to add, combine all previous results we've found into a combined list
                if len(values)>0:
                    combined = []
                    for resList in allRes:
                        for res in resList:
                            if res not in combined:
                                combined.append(res)
                    #results from the bucket
                    valsToCheck = combined  

                    #only add results that dont cause a contradiction or a cycle                          
                    for i in range(len(values)):
                        res = values[i]
                        if res not in valsToCheck:
                            valsToCheck.append(res)
                            badChange,reason = helpers.detectBadChange_noexit(valsToCheck,'internal combine',shouldPrint=True)  
                            if badChange:
                                valsToCheck.remove(res)
                                if reason == 'cycles':
                                    print('try b,r,a?')
                                    a,r,bval = res 
                                    if (bval,r,a) not in valsToCheck:
                                        
                                        valsToCheck.append((bval,r,a))
                                        badChange,reason = helpers.detectBadChange_noexit(valsToCheck,'internal combine',shouldPrint=True)  
                                        if(badChange):
                                            valsToCheck.remove((bval,r,a))
                                    
                                    #exit(0)
                    #append the remaining values to the combined list                         
                    for res in valsToCheck:
                        if res not in combined:
                            combined.append(res)                            
                    #this only includes results that wont cause contradiction or a cycle
                    badChange,reason  = helpers.detectBadChange_noexit(combined,'internal combine',shouldPrint=False)
                    if not badChange:
                        allRes.append(valsToCheck)
                    else:
                        #if we found a contradiction, based on the values we found, we need to split the bucket again.
                        splitBuckets = splitUpdates(singleBucket)
                        for sb in splitBuckets:
                            #print(len(sb))
                            newBuckets.append(sb)
            
            #found a contradiction already in the bucket, split the bucket again
            else:
                splitBuckets = splitUpdates(singleBucket)
                for sb in splitBuckets:
                    newBuckets.append(sb)
        #if we dont have any remaining buckets to test, break the while loop.                
        if len(newBuckets) ==0:
            break
        else:
            pass
            #print('go again!',len(buckets))
    #combine all results we have found previously
    combined = []
    for resList in allRes:
        for res in resList:       
            if res not in combined:
                print(res)
                combined.append(res)
    #if we find a contradiction/cycle hard exit here.                 
    helpers.detectBadChange(combined,'combined')

    #extend the results we have found with graph theory
    #if nothing else to not have to do a>b, b>c -> a>c by hand for long chains of inequalities. 
    innercnt = 0    
    haveNewResults = True
    while haveNewResults:
        
        combined, haveNewResults = extendWithGraphs(combined,useShortestPath=False)
        if innercnt > 10:
            input('this seems to be taking a while...?')
        innercnt+=1     
    #do we know the relationship for all a b?
    done = helpers.all_a_b_exist(combined)
    print('do all a_b exist? ',done)
    if done:

        print('yay done')
        # findNeededNeighbors(combined)
        # dgraph = helpers.construct_digraph(combined)
        # tg = networkx.topological_generations(dgraph)
        # for a in tg:
        #     print(a)
        # allTopos = networkx.all_topological_sorts(dgraph)
        # for a in allTopos:
        #     print(a)
        # print(combined)
        # exit(0)
    print(combined)
    return combined,done
def findNeededNeighbors(results):
    """find neighbors we still need results for by using topological generation.
    tg is in the form of level: [asns]
    if len(asns) > 1, then we have multiple neighbors at the same level, so their p_before is equal.
    when a result is added, neighbor a can really only move down in rank"""
    neededNeighbors = set()
    dgraph = helpers.construct_digraph(results)
    tg = networkx.topological_generations(dgraph)
    print('tg')
    for level1,asns in enumerate(tg):
        #print(level1,asns)
        if len(asns)>1:
            tg = networkx.topological_generations(dgraph)
            for level2,asns2 in enumerate(tg):
                print(level2,asns2)
                if level2 < level1:
                    continue
                for asn in asns2:
                    neededNeighbors.add(asn)
            print('found we need to find results for ',neededNeighbors)      
            return neededNeighbors
    #there was no level with more than 1 neighbor
    return None  
def combineNeighborResults(combined,combined2):
    #extend the neighbor results with graphs
    innercnt = 0    
    haveNewResults = True
    while haveNewResults:
        combined2, haveNewResults = extendWithGraphs(combined2,useShortestPath=False)
        if innercnt > 10:
            input('this seems to be taking a while...?')
        innercnt+=1     
    for newRes in combined2:
        if newRes not in combined:
            combined.append(newRes)
            badChange,reason  = helpers.detectBadChange_noexit(combined,'foundResults',shouldPrint=True)
            if badChange:
                combined.remove(newRes)
    return combined

def make_ranks(results):
    dgraph = helpers.construct_digraph(results)
    tg = networkx.topological_generations(dgraph)
    ranks = []
    for level,asns in enumerate(tg):
        ranks.append(asns)
    return ranks
def neighborsAreSameRank(update1Neighbor,update2Neighbor,p_before_ranks):
    for rank in p_before_ranks:
        if len(rank)<=1:
            continue
        print('examining ',rank,'for ',update1Neighbor,update2Neighbor)
        if update1Neighbor in rank and update2Neighbor in rank:
            return True
    return False
def updatesHaveSameOrigin(update1,update2):
    update1_origin = update1['origin']
    update2_origin =  update2['origin']
    if update1_origin == update2_origin:
        return True
    return False

def convert_float_to_time(value):
    #working with floating point values is SO FUN

    #if we have a very small value, it will have an e
    if 'e' in str(value):
        epart = int(str(value).split('e-')[1])
        formatted_value = f"{value:.10f}"
        #if the e is >=5, this is too small so lets just consider it 0
        if epart >=5:
            ms = 0
        else:
            ms=formatted_value[:-6]
        #print('eeeeeeeeeeeeee')
       # print(epart)
       #exit(0)
        total_days = 0 
        hours= 0 
        minutes = 0 
        seconds = 0 
        
        return total_days, hours, minutes, seconds,ms
    
    #seperate the whole part of the float time value
    #this whole represents the amount of SECONDS
    whole = int(str(value).split('.')[0])
    if whole >0:
        #print(value,'>',0)
        total_seconds = whole
        #there are 86400 seconds in a day 
        total_days = int(total_seconds // 86400)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
    #print(value)        
    else:
        total_days = 0 
        hours= 0 
        minutes = 0 
        seconds = 0 
    ms = float('.'+str(value).split('.')[1][:6])
    return total_days, hours, minutes, seconds,ms
 
def findResult(results,a,b):
    for x,r,y in results:
        if x==a and y==b:
            return r
    return None
def findMinMaxNeighbors(results):

    allNeighbors = set()
    for result1 in results:
        a1,r1,b1 = result1
        allNeighbors.add(a1)
        allNeighbors.add(b1)
    neverOnRight = []
    neverOnLeft = []
    for n1 in allNeighbors:
        appearedLeft = False
        appearedRight = False
        for a,r,b in results:
            if r !='=':
                if n1==a:
                    appearedLeft = True
                if n1==b:
                    appearedRight = True
            
        if not appearedRight:
            neverOnRight.append(n1)
        if not appearedLeft:
            neverOnLeft.append(n1)
    lowestPrefNeighbors = neverOnLeft
    highestPrefNeighbors = neverOnRight
    return lowestPrefNeighbors,highestPrefNeighbors
def printResultForSingleNeighbor(results,neighbor,left,right):
    if left:
        print(neighbor,'on left')
        for a,r,b in results:
            if a == neighbor:
                print(a,r,b)
    if right:
        print(neighbor,'on right')
        for a,r,b in results:
            if b == neighbor:
                print(a,r,b)                
def whyWasUpdateReplaced(update1,update2):
    update1Time = update1['timestamp']
    update2Time = update2['timestamp']
    #we assume update2 is > update 1, if that doesnt happen hard crash. 
    assert(update2Time>=update1Time)
    neighbor1 = helpers.findNeighborInUpdate(update1)
    neighbor2 = helpers.findNeighborInUpdate(update2)
    #find the as_path of the updates
    update1Path = helpers.splitASPathFromUpdate(update1)
    update2Path = helpers.splitASPathFromUpdate(update2)
    if len(update2Path)>len(update1Path):
        return('p_before')
    if len(update2Path)<len(update1Path):
        return ('as_path')
    origin_types_dict = {'IGP':1, 'EGP':2, 'INCOMPLETE':3}
    update2Origin = update2['origin']
    update1Origin = update1['origin']
    if origin_types_dict[update2Origin] <  origin_types_dict[update1Origin]:
        return 'origin_type'
    if origin_types_dict[update2Origin] >  origin_types_dict[update1Origin]:
        print("why is update2's origin > update1 origin?")
        print(update2)
        print(update1)
        exit(0)
    return('p_after')
    #implicit |u1| = |u2|
def isContradiction(result1,result2):
    #print(result1,result2)
    res1,time1,prefix1,why1 = result1
    res2,time2,prefix2,why2 = result2
    # print('finding contradiction ',res1,res2)
    a1,r1,b1 = res1
    a2,r2,b2 = res2
    #same result is not a contradiction
    if res1 == res2:
        return False
    
    if a1 == a2 and b1 == b2:
        
        if r1 != r2: #simplifies a>b, a?b or a?b a>b                        
            if r1 =='?' and r2 =='=':
                return False
            elif r1 == '=' and r2 =='?':
                return False
            else:
                return True
        else:            
            return False #-> a>b, a>b or a?b, a?b 
                
    #a?b b?a 
    if a1 == b2 and b1 == a2:
        if r1 =='>' and r2 == '>': #a>b b>a is a conradiction
            return True 

        if r1 =='?' and r2 =='?': 
            #a?b b?a may or may not be a contradiction, 
            # we dont know yet, as ? is not resolved to > or =
            return False
        if r1 =='=' and r2 =='=':
            #equality is not a contradiction
            return False
        #a?b and b>a or a>b and b?a 
        return True


def scanResults(results):
    print('Scanning results...')
    sortedResults = sorted(results,key=lambda x: x[1],reverse=True)
    curTime = int(sortedResults[0][1])
    slices = {}
    someResults = []  
    #print(len(sortedResults),curTime)    
    for i in range(len(sortedResults)):
        if curTime not in slices:
            slices[curTime] = []
        result1 = sortedResults[i]
        #print(result1)
        res1,time1,prefix1,why1 = result1
        
        if len(someResults)==0:
            someResults.append(result1)
            continue
        contraFound = False
        #does this contradict something we already know in this bucket
        for knownResult in someResults:
            #print('is ',knownResult,'a contradiction against',result1)
            if isContradiction(knownResult,result1):
                contraFound = True 
                print('found contradiction')
                break     
            #else:
                #print('no')           
                
        if contraFound:
            slices[curTime] = someResults
            someResults = [result1]
            curTime = time1
        else:
            someResults.append(result1)

    slices[curTime] = someResults
    
    #print results
    # for t in slices:
    #     if len(slices[t])>0:
    #         print(t)
    #         for result in slices[t]:
    #             print(result)
    return slices
    #exit(0)
def getSliceResults(slices):
    yoloCombine = []
    for t in slices:
        for result in slices[t]:
            res,time,prefix,why = result
            a,r,b = res
            if r != '?':
                if res not in yoloCombine:
                    yoloCombine.append(res)
                #print('appending',res)
                #print(yoloCombine)
                contras = helpers.findContradictions(yoloCombine)
                if len(contras)>0:
                    #print('contradiction detected')
                    yoloCombine.remove(res)
                haveCycles,badCycles = helpers.detectCycles_ignore_eq(yoloCombine,False)                        
                if haveCycles:
                    #print('cycle detected')
                    yoloCombine.remove(res)
    return yoloCombine
def main():
    #this thing blows up and doesnt work if the observer only dumps its results at the exact same timestamp
    #so thats just a limitation we cant support, but i suppose thats fine. 
    #every result for debugging purposes
    global everyRes
    everyRes = []
    doneObservers= []
    #collector = 'rrc04'
    collector = 'route-views2'
    # observerIP = '192.65.185.3' #rrc04
    #observerIP = '192.65.185.157' #rrc04 #dumps results at same timestamp
    observerIP = '37.139.139.17' #routeviews2
    startTime = '2024-03-30T00:00:00'
    originalStart = startTime
    #for _ in range(1):
    # ripePeers = helpers.getRipePeers()
    # for peer_asn,observerIP in ripePeers['rrc04']['peers']:
    #     print(observerIP)
    # exit(0)
    # for minctr in range(25):
    allData = {}
    for _ in range(1):
        #minctr = 2
        minctr = 1
        #observerIP = '192.65.185.244'
        peer_asn = 'xxx'
        for _ in range(1):
            if observerIP not in allData:
                allData[observerIP] ={}
        # for peer_asn,observerIP in ripePeers['rrc04']['peers']:
            #skip ones where we're done, currently it just has >3 resuls
            results = []
            allNeighbors = set()
            if observerIP in doneObservers:
              continue

            #minutesToAdd = 45#helpers.get_minutesForFile(collector) # 15 #just use 15 for both 
            minutesToAdd = 120*(minctr+1) #45#helpers.get_minutesForFile(collector) # 15 #just use 15 for both 
            
            endTime = helpers.addTime(originalStart,minutesToAdd=minutesToAdd)
            print('start process 1')
            allUpdates = helpers.getUpdatesForCollectorObserverAndTime(startTime,endTime,collector,observerIP)
            prefDict = getPrefDict(allUpdates)
            allTimeDiffs = []
            prefixSlices = {}
            prefixResults = []
            for prefix in prefDict:
                if prefix not in allData[observerIP]:
                    allData[observerIP][prefix] ={}
                prefixSlices[prefix]={}
                #specifically, load balancing 
                origin_asns = findOrigin_Asns(prefDict[prefix])
                if len(origin_asns) >=2:
                    continue    
                #sort the updates based on their timestamp so update2 replaces update1
                someUpdates = sorted(prefDict[prefix],key=lambda x:x['timestamp'])
                if len(prefDict[prefix])<=1:
                    continue
                #print(prefix)
                #sometimes the collector/peer is busy and sends updates with the same timestamp
                #we cant reason about two updates with the same timestamp for the same prefix
                #so remove them. 
                someUpdates = removeDuplicateTimestamps(someUpdates)
                #print(len(someUpdates))
                
                for i in range(len(someUpdates)): 

                    update1 = someUpdates[i]
                    try:
                        update2 = someUpdates[i+1]
                    except:
                        break  
                    update1Time = update1['timestamp']
                    update2Time = update2['timestamp']
                    neighbor1 = helpers.findNeighborInUpdate(update1)
                    neighbor2 = helpers.findNeighborInUpdate(update2)
                    allNeighbors.add(neighbor1)
                    allNeighbors.add(neighbor2)
                    if neighbor1 == neighbor2:
                        continue
                    #find the as_path of the updates
                    update1Path = helpers.splitASPathFromUpdate(update1)
                    update2Path = helpers.splitASPathFromUpdate(update2)
                    why = whyWasUpdateReplaced(update1,update2)
                    if len(update2Path) > len(update1Path):                       
                        #res = ((neighbor2,">",neighbor1),update2['timestamp'],prefix,why,(update1,update2))
                        res = ((neighbor2,">",neighbor1),update2['timestamp'],prefix,why)
                        #results.append(res)
                    else:
                        #res = ((neighbor2,"?",neighbor1),update2['timestamp'],prefix,why,(update1,update2))
                        res = ((neighbor2,"?",neighbor1),update2['timestamp'],prefix,why)
                    prefixResults.append(res) 
                    # tdiff = convert_float_to_time(update2Time-update1Time)
                    # days,hours,mins,seconds,ms = tdiff
                    # if days>0 or hours>0 or mins>0 or seconds > 5:
                    #     #prefixSlices[prefix] = prefixResults
                    #     #prefixResults = []
                    #     #new slice here
                    #     continue 
                    # else:
                        
            sortedResults = sorted(prefixResults,key=lambda x: x[1],reverse=True)
            sliceTimeDistanceValue = -3 
            prefixDict ={} 
            for result in sortedResults:
                #res, time,prefix,why,updates = result
                res, time,prefix,why = result

                if prefix not in prefixDict:
                    prefixDict[prefix] = [] 
                prefixDict[prefix].append(result)
            someResultsDict ={}
            for prefix in prefixDict:
                slices = scanResults(prefixDict[prefix])
                someResultsDict[prefix]=slices
            
            for prefix in someResultsDict:
                print(prefix)
                slices = someResultsDict[prefix]            
                for t in slices:
                    print(t)
                    # for result in slices[t]:
                    #     print(result)
                    for i in range(len(slices[t])):
                        result1 = slices[t][i]
                        #res1,time1,prefix1,why1,updates1 = result1
                        res1,time1,prefix1,why1 = result1
                        a1,r1,b1 = res1
                        #skip results when the observer rebroadcasts a route it already has
                        if a1==b1:
                            continue
                        try:
                            result2 = slices[t][i+1]
                            #res2,time2,prefix2,why2,updates2 = result2
                            res2,time2,prefix2,why2 = result2
                            a2,r2,b2 = res2
                        except:
                            break
                        assert(prefix1==prefix2)
                    
                        #filter down results
                        newResult = None
                        if r1 =='?' and r2 == r1 and a1 == b2 and a2 == b1:
                            if why1 == 'p_after' and why2=='p_after':
                                newResult =(a1,'=',b1)
                                slices[t][i] = newResult,time1,prefix1,why1
                                slices[t][i+1] = (a2,'=',b2),time2,prefix2,why2
                        if r1 =='=' and r2 == '?' and a1 == b2 and a2 == b1:
                                if why1 == 'p_after' and why2=='p_after':
                                    slices[t][i+1] = (a2,'=',b2),time2,prefix2,why2
                        if r1 =='=' and r2 == '?' and a1 == a2 and b1 == b2:
                            if why1 == 'p_after' and why2=='p_after':
                                    slices[t][i+1] = (a2,'=',b2),time2,prefix2,why2
                    haveNewResults = True
                    innercnt = 0
                    expandedResults = [] 
                    for result in slices[t]:
                        res,time,prefix,why = result
                        expandedResults.append(res)
                    while haveNewResults:                
                        expandedResults, haveNewResults = extendWithGraphs(expandedResults,useShortestPath=False)
                        if innercnt > 10:
                            input('this seems to be taking a while...?')
                        innercnt+=1
                    toAdd = []
                    for newResult in expandedResults:
                        found = False
                        for result in slices[t]:
                            res,time,prefix,why = result
                            if newResult == res:
                                found = True
                                break
                        if not found:
                            toAdd.append(newResult)
                    for a in toAdd:
                        #ap = a,time,prefix,why
                        slices[t].append((a,'',prefix,'expanded'))
            print('after expanding')
            for prefix in someResultsDict:
                print(prefix)
                
                slices = someResultsDict[prefix]            
                for t in slices:
                    print(t)
                    
                    # for result in slices[t]:
                    #     print(result)
                    for i in range(len(slices[t])):
                        result1 = slices[t][i]
                        print(result1)
            pcounter = 0
            for prefixP in someResultsDict:
            #yolo combine
                pcounter+=1
                print('combining results',prefixP, f'{pcounter}/{len(someResultsDict.keys())}')
                yoloCombine = []
                #prefixP = '197.138.83.0/24'
                slices = someResultsDict[prefixP] 
                yoloCombine = getSliceResults(slices)
                somecounter = 0
                
                otherResults = []
                for prefix in someResultsDict:
                    somecounter+=1
                    #print(f'{somecounter}/{len(someResultsDict.keys())}')                
                    if prefix == prefixP:
                        continue

                    
                    slices = someResultsDict[prefix] 
                    for t in slices:
                        for newResults in slices[t]:
                            res,time,prefix,why = newResults
                            if time =='':
                                    time = 0
                            if (res,time,prefix,why) not in otherResults:
                                    otherResults.append((res,time,prefix,why)) 
                #print("adding other results")            
                newResCtr = 0
                toRem = []
                #simplify the new results to hopefully reduce how long it takes to add everything
                for possibleNewRes in otherResults:
                    newResult,time,prefix,why = possibleNewRes
                    a,r,b = newResult
                    if r =='?':
                        toRem.append(possibleNewRes)
                        continue
                    if newResult in yoloCombine:
                        toRem.append(possibleNewRes)
                for rem in toRem:
                    otherResults.remove(rem)  

                for newResults in sorted(otherResults,key=lambda x: x[1],reverse=True):
                        newResCtr+=1
                        #print(f"{newResCtr}/{len(otherResults)}")
                        
                        #print(newResult)
                        newResult,time,prefix,why = newResults
                        # if time !='':
                        #     print(helpers.convertUnixToTimeString(time))
                        a,r,b = newResult
                        if r =='?':
                            continue
                        if newResult not in yoloCombine:
                            yoloCombine.append(newResult)
                        #only check results if we added something
                        else:
                            continue
                        contras = helpers.findContradictions(yoloCombine)
                        if len(contras)>0:
                            yoloCombine.remove(newResult)
                            continue
                        haveCycles,badCycles = helpers.detectCycles_ignore_eq(yoloCombine,False)
                        if haveCycles:
                            yoloCombine.remove(newResult)
                            continue
                        #abandon SAT solving for now, this will be future work
                        # model = helpers.create_cp_model(yoloCombine)
                        # solver,status = helpers.solveModel(model)
                        # isSolveable =helpers.isModelSolveable(status)                     
                        # if not isSolveable:
                        #     yoloCombine.remove(newResult)
                        # else:
                        #     ranks = helpers.getModelRanks(model,solver)
                        #     print(ranks)
                        #     if helpers.haveUniqueRanks(ranks):
                        #         print('we have unique ranks!')
                        #         for rank,asn in ranks:
                        #             print(rank,asn)
                                
                        #         print(yoloCombine)
                        #         exit(0)
            
                print('yolo combine')
                print(yoloCombine)
                # for result in yoloCombine:
                #     print(result)
                prefIsDone = helpers.all_a_b_exist(yoloCombine)
                if prefIsDone:
                    print(prefixP)
                    for _ in range(5):
                        print("~~~~~~~PREFIX IS DONE~~~~~~~")
                #print(slices[t])            
                
                gtResults =[]
                eqResults = []
                for result in yoloCombine:
                    a,r,b = result
                    if r =='>':
                        gtResults.append(result)
                    elif r =='=':
                        eqResults.append(result)
                    else:
                        print('unkown relationship')
                        exit(0)
                someGraph = helpers.construct_digraph(gtResults)
                topSort = list(networkx.topological_generations(someGraph))
                eqSets = []
                for eqRes in eqResults:
                    
                    a,r,b = eqRes   
                    if len(eqSets)==0:
                        newSet = set()
                        newSet.add(a)
                        newSet.add(b)
                        eqSets.append(newSet)
                        continue
                    found = False             
                    for oldSet in eqSets:
                        if a in oldSet:
                            found=True
                            oldSet.add(b)
                        if b in oldSet:
                            found=True
                            oldSet.add(a)
                    if not found:
                        newSet = set()
                        newSet.add(a)
                        newSet.add(b)
                        eqSets.append(newSet)
               #print(eqSets)
                #print(eqResults)
                minNeighbors,maxNeighbors = findMinMaxNeighbors(yoloCombine)
                seenAsns = []
                rankDict ={}
                ranks = []
                for rank,asns in enumerate(topSort):
                    rankedAsns = []
                    
                    for asn in asns:
                        if asn not in seenAsns:
                            rankedAsns.append(asn)
                            seenAsns.append(asn)
                    for eqSet in eqSets:
                        for asn in eqSet:
                            if asn not in seenAsns:
                                rankedAsns.append(asn)
                                seenAsns.append(asn)
                    if len(rankedAsns)>0:
                        ranks.append((rank,rankedAsns))
                        print(rank,rankedAsns)
                    continue
                rankDict[prefixP] = ranks     
            
            pickle.dump(rankDict,open(f'pickles/rankDict-C{collector}-O{observerIP}.pickle','wb'))
            for prefixP in rankDict:
                print(prefix)
                orderedRanks = rankDict[prefix]
                for rank,asns in orderedRanks:
                    print(rank,asns)
                print("~~~~~")
            exit(0)
            for _ in range(0):
                asns = []
                asns.append(asn)
                for eqRes in eqResults:
                    a,r,b = eqRes
                    if asn == a and b not in asns:
                        asns.append(b)
                    if asn ==b and a not in asns:
                        asns.append(a)
                print(rank,asns)
            exit(0)
            for prefix in someResultsDict:

                print(prefix)
                slices = someResultsDict[prefix]        
                
                for t in slices:
                    if len(slices[t])>5:
                        print(t)
                        for result in slices[t]:
                            print(result)
            
            for prefix in prefixDict:
                break
                if prefix not in someResultsDict:
                    someResultsDict[prefix] = []#{} #eventually
                someResults = []
                for i in range(len(prefixDict[prefix])):
                    result1 = prefixDict[prefix][i]
                    #res1,time1,prefix1,why1,updates1 = result1
                    res1,time1,prefix1,why1 = result1
                    a1,r1,b1 = res1
                    #skip results when the observer rebroadcasts a route it already has
                    if a1==b1:
                        continue
                    try:
                        result2 = prefixDict[prefix][i+1]
                        #res2,time2,prefix2,why2,updates2 = result2
                        res2,time2,prefix2,why2 = result2
                        a2,r2,b2 = res2
                    except:
                        
                        break
                    assert(prefix1==prefix2)
                   
                    #filter down results
                    newResult = None
                    if r1 =='?' and r2 == r1 and a1 == b2 and a2 == b1:
                        if why1 == 'p_after' and why2=='p_after':                    
                            newResult =(a1,'=',b1)
                            prefixDict[prefix][i] = newResult,time1,prefix1,why1
                            #print(prefixDict[prefix][i])

            for prefix in prefixDict:
                scanResults(prefixDict[prefix])
                if len(prefixDict[prefix])>2:
                    print(prefix)
                    for i in range(len(prefixDict[prefix])):
                        result = prefixDict[prefix][i]
                        res, time,prefix,why = result
                        print(result)
                        
                    #exit(0)
            exit(0)
                    
            # gtc = 0
            # gtp = None
            # for prefix in prefCountDict:
            #     if gtc < prefCountDict[prefix]:
            #         gtp = prefix
            #         gtc = prefCountDict[prefix]
            # print(gtp,gtc)
            # for result in sortedResults:
            #     res, time,prefix = result
            #     if prefix != gtc:
            #         sortedResults.remove(result)
            # print(sortedResults)
            # #exit(0)
            # print(sortedResults[0],sortedResults[-1])
            #start by dividing things into slices of 5 seconds each 
            curTime = int(sortedResults[0][1])
            slices = {}
            someResults = []
            print('after sorting')
            for result in sortedResults: #results for every prefix for a single observer
                
                res, time,prefix,why = result
                
                if curTime not in slices:
                    slices[curTime] = []

                
                nextTime = curTime +sliceTimeDistanceValue
                
                #print(curTime,time,nextTime, 'time value <--')
                #exit(0)   
                #print('first time is',sTime,'next time is',nextTime)
                    #todo
                #exit(0)
                    
                if curTime <= time and time > nextTime:
                    #print(curTime,time,nextTime, 'time value <--')
                    #print(convert_float_to_time(time))
                    #exit(0)
                    slices[curTime].append(result)
                else:
                    curTime = nextTime
                    slices[nextTime] = []
            print("~~~~~")
            #print(slices)
            someRes = {}
            for t in slices:
                if len(slices[t])>1:
                    print(t)
                    for result in slices[t]:
                        res,time,prefix,why = result
                        
                        if prefix not in someRes:
                            someRes[prefix] = []
                        someRes[prefix].append(result)
                        print(result)
            exit(0)                        
            slices = {}
            for prefix in someRes:
                if prefix not in slices:
                    slices[prefix] = {}
                for result in someRes[prefix]:                
                    res, time,prefix,why = result                    
                    if curTime not in slices[prefix]:
                        slices[prefix][curTime] = []
                    nextTime = curTime +sliceTimeDistanceValue                    
                    if curTime <= time and time > nextTime:            
                        slices[prefix][curTime].append(result)
                    else:
                        curTime = nextTime
                        slices[prefix][nextTime] = []
            
            for prefix in slices:                
                             
                for t in slices[prefix]:
                    if len(slices[prefix][t])>2:
                        print('prefix',prefix)   
                        print(t)
                        for result in slices[prefix][t]:
                            print(result)
            # for prefix in slices:                
            #     if len(slices[prefix])>0:
            #         for t in slices[prefix]:
            #             sliceResults[prefix][t] = []

            possibleEQ = [] 
            possibleGT = []
            
            print('slice keys')
            #print(slices.keys())
            
            
            sliceResults = OrderedDict()
            exit(0)

            for t in slices:
                sliceResults[t] = []
                if len(slices[t])>1:
                   # print(t)
                    for result1 in slices[t]:
                        found = False
                        res1,time1,prefix1 = result1
                        a1,r1,b1 = res1
                        for result2 in slices[t]:
                            if result1 == result2:
                                continue
                            
                            res2,time2,prefix2 = result2
                             
                            a2,r2,b2 = res2
                            if a1 == b2 and a2 == b1:
                                if prefix1 == prefix2:
                                    found=True
                            # print('reverse found')
                                #found = True
                                    break
                        newRes = None
                        if found:
                            newRes = (a1,'=',b1)                            
                            possibleEQ.append(result1)
                        else:
                            if r1 =='>':
                                newRes = (a1,'>',b1)
                            possibleGT.append(result1)
                        if newRes not in sliceResults[t] and newRes!=None:
                            sliceResults[t].append(newRes)
            print(list(sliceResults.keys())[0])
            print(list(sliceResults.keys())[-1])
            print(list(sliceResults.keys())[0]>list(sliceResults.keys())[-1])
            for t in sliceResults:
                if len(sliceResults[t])>1:
                    print(t)
                    for result in sliceResults[t]:
                        print(result)
            #exit(0)                            
            combinedResults = []
            for t in sliceResults:
                if len(sliceResults[t])>0:
                    print(t,helpers.convertUnixToTimeString(t))
                    for result in sliceResults[t]:
                        if result not in combinedResults:
                            combinedResults.append(result)
                        contras = helpers.findContradictions(combinedResults)
                        if len(contras)>0:
                            combinedResults.remove(result)
                            continue
                        # G = networkx.DiGraph()
                        # for res in combinedResults:
                        #     a,r,b = res
                        #     if r=='>':
                        #         G.add_edge(a,b)
                        # cycles = list(networkx.simple_cycles(G))
#                        cycles problem 
                        haveCycles, cycles = helpers.detectCycles_ignore_eq(combinedResults)
                        if haveCycles:
                        #if len(cycles)>0:
                            combinedResults.remove(result)
                        #badRes = helpers.detectBadChange_noexit(combinedResults,'combining',shouldPrint=True)
                        # if badRes:
                        #     combinedResults.remove(result)
                        print(result)
            print('combined results')
            for res in combinedResults:
                print(res)
            
            print(combinedResults)
            print(helpers.all_a_b_exist(combinedResults))
            
            noNewResult=True
            innercnt = 0
            while noNewResult:
                if innercnt >= 10:
                    input("this seems to be taking a while....")
                innercnt+=1
                G = networkx.DiGraph()
                for res in combinedResults:
                    a,r,b = res
                    if r =='=':
                        G.add_edge(a,b,weight=0)
                    if r =='>':
                        G.add_edge(a,b,weight=1)
                allNeighbors = helpers.getAllNeighborsFromResults(combinedResults)
                newResults = []
                for nodeA in allNeighbors:                    
                    for nodeB in allNeighbors:
                        if nodeA == nodeB:
                            continue
                        if networkx.has_path(G,nodeA,nodeB):
                            sp = networkx.shortest_path(G,nodeA,nodeB)
                            if len(sp)>2:
                                print(sp)
                                pathWeights = []
                                for i in range(len(sp)):
                                    u = sp[i]
                                    try:
                                        v = sp[i+1]
                                    except:
                                        break
                                    uvWeight = G.get_edge_data(u,v,'weight')
                                    pathWeights.append(uvWeight)
                                if all(weight ==0 for weight in pathWeights):
                                    newRes = (nodeA,'=',nodeB)
                                else:
                                    newRes = (nodeA,'>',nodeB)
                                if newRes not in newResults:
                                    newResults.append(newRes)
                newRes = discardKnownResults(combinedResults,newResults)
                print(newResults)
                noNewResult = False
                
                for newRes in newResults:    
                    if newRes not in combinedResults:
                        combinedResults.append(newRes)                                                
                    contras = helpers.findContradictions(combinedResults)                    
                    haveCycles, cycles = helpers.detectCycles_ignore_eq(combinedResults)
                    if len(contras)>0:                                          
                        combinedResults.remove(newRes)
                    elif haveCycles:
                        combinedResults.remove(newRes)
                        #print(cycles)
                        #exit(0)
                    else:
                        print("added new result",newRes)
                        noNewResult = True

            print('Extended results')
            # for res in combinedResults:
            #     print(res)      
            print(combinedResults)
            print(helpers.findContradictions(combinedResults))
            print(helpers.all_a_b_exist(combinedResults))
            
            minNeighbors,maxNeighbors = findMinMaxNeighbors(combinedResults)            
            print(minNeighbors,maxNeighbors)
            printResultForSingleNeighbor(combinedResults,'1299',True,True)
            printResultForSingleNeighbor(combinedResults,'6830',True,True)
            
            # print('min neighs')
            # for m in minNeighbors:
            #     printResultForSingleNeighbor(combinedResults,m,True,True)
            # print('max neighs')
            # for m in maxNeighbors:
            #     printResultForSingleNeighbor(combinedResults,m,True,True)
            # for a,r,b in combinedResults:
            #     if r =='=':
            #         print(a,r,b)
            #exit(0)
            G = networkx.DiGraph()
            for res in combinedResults:
                a,r,b = res
                if r=='>':
                    G.add_edge(a,b)
            cycles = networkx.simple_cycles(G)
            print('cycles?',len(list(cycles))>0)
            for cycle in cycles:
                print(cycle)
            
            generations = list(networkx.topological_generations(G))
            combinedGenerations = {}
            foundInOldGens = []
            for i, tg in enumerate(generations):
                print(i,tg)
                combinedGenerations[i]=tg
                for res in combinedResults:
                    a,r,b = res
                    if r=='=':
                        #print(res)                        
                        if a in tg or b in tg:
                            print(a,'or',b,'in',tg)
                            # if a not in foundInOldGens or b not in foundInOldGens:
                            #     foundInOldGens.append(a)
                            #     foundInOldGens.append(b)
                            if a not in combinedGenerations[i]:
                                combinedGenerations[i].append(a)
                            if b not in combinedGenerations[i]:
                                combinedGenerations[i].append(b)
            exit(0)
            previousGenerations = []
            for level in combinedGenerations:
                print(level,combinedGenerations[level])
                rem = []
                for asn in combinedGenerations[level]:                    
                    if asn in previousGenerations:
                        rem.append(asn)
                    else:
                        previousGenerations.append(asn)    
                for r in rem:
                    combinedGenerations[level].remove(r)
            print(combinedGenerations)
                
                

                    
            #exit(0)
            contras = helpers.findContradictions(combinedResults)
            
            innercnt = 0    
            haveNewResults = True
            while haveNewResults:
                
                combinedResults, haveNewResults = extendWithGraphs(combinedResults,useShortestPath=False)
                if innercnt > 10:
                    input('this seems to be taking a while...?')
                innercnt+=1
            
            print('combined results new ')
           
            
            minNeighs,maxNeighs = findMinMaxNeighbors(combinedResults)
            print(minNeighs,maxNeighs)
            
            
            for res1 in combinedResults:
                for res2 in combinedResults:
                    if res1 ==res2:
                        continue
            #print(helpers.all_a_b_exist(combinedResults))
            exit(0)                
            print('possible gt')
            fixedGT = []
            for result in possibleGT:
                print(result)
                res,time,prefix = result
                a,r,b = res 
                newRes = (a,'>',b)
                if newRes not in fixedGT:
                    fixedGT.append(newRes)
            print('fixed gt')                    
            for res in fixedGT:
                print(res)
            contras = helpers.findContradictions(fixedGT)
            print(len(contras),contras[0])                
            #exit(0)
            for result in possibleEQ:
                print(result)
                    
            exit(0)
            #for prefix in prefixSlices:
                # if len(prefixSlices[prefix])>99999:
                #     print(prefix)
                #     print(prefixSlices[prefix])
                    
                    # if tdiff not in allTimeDiffs:
                    #     allTimeDiffs.append(tdiff)
                    # print(tdiff)
                    # continue
            #exit(0)
            sortedAllTimes = sorted(allTimeDiffs,key=lambda x: (x[0],x[1],x[2],x[3],x[4]))
            print('minmax timediff')
            print(sortedAllTimes[0],sortedAllTimes[-1])
            for t in sortedAllTimes[20:]:
                print(t)
            print(len(sortedAllTimes))
            #exit(0)
            #for _ in range(0):
             #   for _ in range(0):
                    #print(helpers.convertUpdateToTimestring(update1))
                    #print(helpers.convertUpdateToTimestring(update2))
                    #exit(0)
                    

            tsResults = sorted(results,key=lambda x: x[1],reverse=True)
            
            firstTime = tsResults[0][1]            
            lastTime = tsResults[-1][1]
            
            slices = {}
            sliceValue = .01 #3 minutes
            slices[firstTime] = []
            curTime = firstTime
            someResults = []
            s2 = 0
            for result in tsResults:
                res,timestamp,prefix = result 
                a,r,b = res 
                slices[curTime].append(result)
                if r == '>':
                    someResults.append(res)                    
                    s2+=1
                    contras = helpers.findContradictions(someResults)
                else:
                    contras = []
                #print(contras)
                if len(contras)>0:
                    someResults.remove(res)
                    slices[curTime].remove(result)
                    #s2= s2-1                    
                    someResults = [res]
                    curTime = timestamp 
                    slices[curTime] = [result]
            testRes = []
            
            for t in slices:
                if t not in sliceResults:
                    sliceResults[t] = []
                print(t)
                # for res in slices[t]:
                #     print(res)
                # continue
                for result1 in slices[t]:
                    found = False
                    for result2 in slices[t]:
                        if result1 == result2:
                            continue
                        res1,time1,prefix1 = result1
                        res2,time2,prefix2 = result2
                        a1,r1,b1 = res1 
                        a2,r2,b2 = res2
                        if a1 == b2 and a2 == b1:
                           # print('reverse found')
                            found = True
                            break
                            # if time1 == time2:
                            #     print(result1)
                            #     print(result2)
                            #     #exit(0)
                            # else:
                            #     print('times not eq')
                            #     print(result1)
                            #     print(result2)
                    if not found:
                        if res1 not in sliceResults[t]:
                            sliceResults[t].append(res1)
                    else:
                        if (res1,('implies eq',prefix1)) not in sliceResults[t]:
                            sliceResults[t].append((res1,('implies eq',prefix1)))
                        #if res1 not in testRes:
                         #   testRes.append(res1)
                            #print('already found',result1)
                print(result1)
            #split the slice results into two sets, those that may imply equality and those that do not
            print('~~~~~')
            possibleGT = {}
            possibleEQ = {}
            for t in sliceResults:
                possibleGT[t] = [] 
                possibleEQ[t] = []
                print(t)
                for result in sliceResults[t]:
                    print(result,len(result))
                    if len(result)==2:
                        possibleEQ[t].append(result)
                    else:
                        possibleGT[t].append(result)
            for t in possibleEQ:
                print(t)
                for result in possibleEQ[t]:
                    print(result)
            exit(0)
            #what happens if i raw dog append everything?
            reses = []
            for t in possibleGT:
                print(t)
                for result in possibleGT[t]:
                    a,r,b = result
                    print(result)
                    if result not in reses and r =='>':
                        reses.append(result)
                        contras = helpers.findContradictions(reses)
                        if len(contras)>0:
                            print('contra found')
                            reses.remove(result)
            print(reses)
            exit(0)
            #slices[curTime] = someResults                
            s = 0
            someResults = []
            # print(slices[1711756835.047292])
            # exit(0)
            for t in slices:
                print(t,helpers.convertUnixToTimeString(t))
                for result in slices[t]:
                    res,timestamp,prefix = result
                    if res not in someResults:
                        #print(res)
                        someResults.append(res)
                        badChange,reason = helpers.detectBadChange_noexit(someResults,'adding by time',shouldPrint=True)
                        if badChange:
                            someResults.remove(res)

                    s+=1
                    print(result)
                #print("~~~")
            
            print(someResults)
            print(len(tsResults),s,s2)
            exit(0)
            haveNewResults = True
            innercnt =0
            while haveNewResults:
                someResults, haveNewResults = extendWithGraphs(someResults,useShortestPath=False)
                if innercnt > 10:
                    input('this seems to be taking a while...?')
                innercnt+=1
            print(someResults)
            gtResults = someResults
            dgraph = helpers.construct_digraph(someResults)
            torder = list(networkx.topological_sort(dgraph))
            tgenerations = networkx.topological_generations(dgraph)
            for level,asns in enumerate(tgenerations):
                print(level,asns)
            print(torder)
            print(len(allNeighbors))
            print(len(helpers.getAllNeighborsFromResults(someResults)))
            print(allNeighbors - helpers.getAllNeighborsFromResults(someResults))
            #exit(0)
            # tdiffs = list(slices.keys())
            # for i in range(len(tdiffs)):
            #     ts1 = tdiffs[i]
            #     try:
            #         ts2 = tdiffs[i+1]
            #     except:
            #         break
            #     print(convert_float_to_time(ts1-ts2))
            exit(0)                
            #continue
            print('start finding equals')
            allUpdates = helpers.getUpdatesForCollectorObserverAndTime(startTime,endTime,collector,observerIP)    
            allNeighbors = set()
            next_hops = set()
            # for update in allUpdates:
            #     n = helpers.findNeighborInUpdate(update)
            #     nh = update['next_hop']
            #     next_hops.add(nh)
            # print(next_hops)
            # exit(0)
            #     allNeighbors.add(n)
            prefDict = getPrefDict(allUpdates)
            #{(a,b):[(timestamp,prefix)], (b,a)[(timestamp,prefix)]}
            resDict = {}
            for prefix in prefDict:
                
                #specifically, load balancing 
                origin_asns = findOrigin_Asns(prefDict[prefix])
                if len(origin_asns) >=2:
                    continue    
                #sort the updates based on their timestamp so update2 replaces update1
                someUpdates = sorted(prefDict[prefix],key=lambda x:x['timestamp'])
                if len(prefDict[prefix])<=1:
                    continue
                #sometimes the collector/peer is busy and sends updates with the same timestamp
                #we cant reason about two updates with the same timestamp for the same prefix
                #so remove them. 
                someUpdates = removeDuplicateTimestamps(someUpdates)
                #print(len(someUpdates))
                for i in range(len(someUpdates)): 

                    update1 = someUpdates[i]
                    try:
                        update2 = someUpdates[i+1]
                    except:
                        break  
                    #print(helpers.convertUpdateToTimestring(update1))
                    #print(helpers.convertUpdateToTimestring(update2))
                    #exit(0)
                    neighbor1 = helpers.findNeighborInUpdate(update1)
                    neighbor2 = helpers.findNeighborInUpdate(update2)
                    update2Time = update2['timestamp']
                    allNeighbors.add(neighbor1)
                    allNeighbors.add(neighbor2)
                    if neighbor1 == neighbor2:
                        continue
                    for i,t in enumerate(list(slices.keys())): 
                        print(i,i+1,len(list(slices.keys())))                       
                        #res,timestamp,prefix = result
                        curtime = list(slices.keys())[i]
                        print(curtime)
                        #curString = str(curTime)+'-allres'={}
                        neighborT = (neighbor2 ,'?', neighbor1)
                        # if curString not in slices:
                        #     slices[curString] = {}
                        # if neighborT not in slices[curString]:
                        #     slices[curString][neighborT] = []
                        try:
                            nextTime =list(slices.keys())[i+1]
                        except Exception as e:
                            print('exception e', e)
                            nextTime = -1
                        if update2Time <= curtime and update2Time > nextTime:
                            print('placing result between ',curTime,nextTime)
                            slices[curtime].append((neighborT,update2Time,prefix))
                            break
                    # if neighborT not in resDict:
                    #     resDict[neighborT] = []
                    # #print(neighborT)
                    # resDict[neighborT].append((update2Time,prefix))
            print('combined slices')
            for t in slices:
                print(t,helpers.convertUnixToTimeString(t))
                for result in slices[t]:
                    res,time,prefix = result
                    a,r,b = res
                    print(res,time,prefix,helpers.convertUnixToTimeString(time))
            exit(0)
            equalNeighbors = []
            possibleGT = []
            for neighbor_a in allNeighbors:
                for neighbor_b in allNeighbors:
                    if neighbor_a == neighbor_b:
                        continue
                    abRes = (neighbor_a,'?',neighbor_b)
                    baRes = (neighbor_b,'?',neighbor_a)
                    # if abRes in resDict and baRes not in resDict:
                    #     print('abr does this imply',abRes,'is >?')
                    #     if (neighbor_a,'>',neighbor_b) not in possibleGT:
                    #         possibleGT.append((neighbor_a,'>',neighbor_b))
                    # if baRes in resDict and abRes not in resDict:
                    #     print('bar does this imply',baRes,'is >?')
                    #     if (neighbor_b,'>',neighbor_a) not in possibleGT:
                    #         possibleGT.append((neighbor_b,'>',neighbor_a))
                    if abRes in resDict and baRes in resDict:
                        abTime,abPrefix = resDict[abRes]
                        baTime,baPrefix = resDict[baRes]
                        
                        for i,t in enumerate(list(slices.keys())):
                            curtime = list(slices.keys())[i]
                            try:
                                nextTime =list(slices.kyes())[i+1]
                            except:
                                pass
                            #     todo
                            # if abTime >= curTime and abTime < nextTime:
                            # if baTime >= curtime and baTime < nextTime:
                            
                        #print(resDict[abRes][0],resDict[baRes][0])
                        for abResult in resDict[abRes]:
                            abTime,abPrefix = abResult
                            # print(type(abTime),abTime,abPrefix,abResult,abRes)
                            # exit(0)
                            for baResult in resDict[baRes]:                                
                                baTime,baPrefix = baResult
                                #print(baTime)
                                if abTime > baTime:
                                    timeDiff = abTime - baTime
                                else:
                                    timeDiff = baTime - abTime
                                #print(timeDiff)
                                tDiffInfo = convert_float_to_time(timeDiff)
                                days, hours, minutes, seconds,ms = tDiffInfo
                                if days>0 or hours>0 or minutes > 0:
                                    continue
                                # print(tDiffInfo,abResult,baResult)
                                # print(minutes,seconds)
                                # print(neighbor_a,neighbor_b)
                                eqRes = ((neighbor_a,'=',neighbor_b),(abResult,baResult)) 
                                if eqRes not in equalNeighbors:
                                    equalNeighbors.append(eqRes)
                                
                        
                        #exit(0)
                    else:
                        pass
                        #print(neighbor_a,neighbor_b,'not in resdict')
            # print(resDict.keys())
    dgraph = helpers.construct_digraph(gtResults)
    torder = list(networkx.topological_sort(dgraph))
    tgenerations = networkx.topological_generations(dgraph)
    for level,asns in enumerate(tgenerations):
        print(level,asns)
    print(torder)
    print(len(allNeighbors))
    print(len(helpers.getAllNeighborsFromResults(gtResults)))
    print(allNeighbors - helpers.getAllNeighborsFromResults(gtResults))
    #print(possibleGT)            
    print('~~~~')
    # for res in possibleGT:
    #     if res in gtResults:
    #         pass
    #        #print(res,'in gtres')
    #     else:
    #         #print(res,'not in gtres')
    #         gtResults.append(res)
    #         badChange = helpers.detectBadChange_noexit(gtResults,'gtres')
    #         if badChange:
    #             gtResults.remove(res)
    #     # innercnt = 0    
    # haveNewResults = True
    # while haveNewResults:
    #     gtResults, haveNewResults = extendWithGraphs(gtResults,useShortestPath=False)
    #     if innercnt > 10:
    #         input('this seems to be taking a while...?')
    #     innercnt+=1     
    # print(gtResults)
    # print(helpers.all_a_b_exist(gtResults))
    # take out the results that cause contradictions
    # treat them as equal 
    # see what happens
    # dgraph = helpers.construct_digraph(gtResults)
    # torder = list(networkx.topological_sort(dgraph))
    # tgenerations = networkx.topological_generations(dgraph)
    # for level,asns in enumerate(tgenerations):
    #     print(level,asns)
    # print(torder)
    # print(len(allNeighbors))
    # print(len(helpers.getAllNeighborsFromResults(gtResults)))
    # print(allNeighbors - helpers.getAllNeighborsFromResults(gtResults))
    #print(possibleGT)
    #print(gtResults)
    exit(0)
    eqN = set()
    for neighbor_a in allNeighbors:
        for res, specRes  in equalNeighbors:
            a,r,b = res
            abr,bar = specRes
            if a == neighbor_a:
                if abr[1]== bar[1]:
                #if abr[0]!= bar[0]:
                    print(a,r,b,abr,bar,"<----")
                else:
                    print(a,r,b,abr,bar)
                eqN.add(a)
                eqN.add(b)
    print(eqN - allNeighbors)
    print(len(allNeighbors-eqN))
    print('done')

if __name__ == "__main__":
    main()
    TODO 
    #split updates based on prefix instead of all updates 
    #find a suiteable time slice that we can find equal neighbors 
    #use those as a baseline, and compare a>b after that, but do so in the context of each slice 
    #combine all results
    #find p_after for a=b
    #done