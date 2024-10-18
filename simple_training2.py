#fix the annoying wayland bug with selecting desktop instead of window
#sudo pkill -HUP mutter-x11-fram

import helpers
import networkx
import pickle 
import os
import sys
import requests
from datetime import datetime 
#to sleep thread random amount of time
import time 
from random import uniform 
#Download all updates for the observer from time [t_-1,t0]
#Construct a set of inferior BGP updates, U by scanning the updates in reverse chronological order for the first withdrawal update W(p,t_w).
#let A(p,t_a,n_a) be an annoucement update annoucing prefix p with neighbor n_a. 
#If no W(p,t_w) is found, then U = all A(p,t_a,n_a) from [t_-1,t]. 
#if W(p,t_w) is found, then U= A(p,t_a,n_a) where t_w< t_a <t.
def find_inferior_updates(fibEntryForP,startTime,observerIP,collector,prefixP):
    print('finding inferior updates...')
    endTime = startTime
    startTime = helpers.subtractTime(startTime,hours=hoursToAdd)
    storageLocation =pickleDir+f'inferior_updates/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    if os.path.exists(storageLocation):
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
        return updates
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
    #parse only Ws of P (should be faster)
    #print(reversed(items))
    print('finding Ws')
    for item in reversed(items):
        #print(item)
        itemsWithInferior.append(item)
        parser = helpers.parseFileWithParams(item,withdrawFilter)
        for update in parser:
            if update['elem_type'] == 'W':
                foundInfiriorFiles = True
                break 
        if foundInfiriorFiles:
            break
    #if no file had any Ws, just return the whole list
    #parse only A's of P (should be faster)
    if not foundInfiriorFiles:
        print('no Ws found!')
        for item in reversed(items):
            parser = helpers.parseFileWithParams(item,annouceFilter)
            for update in parser: 
                #if update['elem_type'] == 'A':
                #print(update)
                updates.append(update)
        pickle.dump(updates,open(storageLocation,'wb'))
        return updates
    #for each file that does not contain a W and the last file that does contain a W
    #find the W and give all updates after that. 
    print("w found, finding inferior...")
    for item in itemsWithInferior:    
        parser = helpers.parseFileWithParams(item,allFilter)
        for update in parser:
            
            print(update)
            if update['elem_type'] == 'W':
                updates = []     
                wHasBeenSeen = True
                continue
            if wHasBeenSeen and update['elem_type']!='W':
                updates.append(update)
        #its possible that we only need to do this for the first file so i'll leave this here for later jic. 
        # if not wHasBeenSeen:
        #     break
    pickle.dump(updates,open(storageLocation,'wb'))
    return updates
def find_inferior_updates_single_pass(fibEntryForP,startTime,observerIP,collector,prefixP):
    print('finding inferior updates single pass...')
    endTime = startTime
    startTime = helpers.subtractTime(startTime,hours=hoursToAdd)
    storageLocation =pickleDir+f'inferior_updates/{prefixP.replace('/','-')}{collector}{observerIP}{endTime}.pickle'
    
    if os.path.exists(storageLocation):
        # print('loading updates...')
        updates = pickle.load(open(storageLocation,'rb'))
        return updates
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
            
            # print(update)
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
    
def addPreferenceToResults(local_preference_results:list,prefResult,reasonToAdd='update'):
    #print("adding ",prefResult, 'to ',local_preference_results)
    
    #checks if (a,_,b) already exists
    #if we already have a result for a,b then we dont add a new one. 
    #this is important to not create duplicates
    #however, if a>=b exists, and our new result is a>b, replace it. 
    new_a = prefResult[0]
    new_relation= prefResult[1]
    new_b=prefResult[2]
    #dont add a ? a 
    if new_a == new_b:
        return local_preference_results
    shouldAdd = True
    shouldReplace = False
    for prev_result in local_preference_results:
        prev_a = prev_result[0]
        prev_relation= prev_result[1]
        prev_b=prev_result[2]
        
        
        #dont add results of b ? a unless we have a>=b and b>=a  
        
        
        if prev_b == new_a and prev_a == new_b:
            #this really shouldnt happen.
            if new_relation == '>' and prev_relation == '>':
                #specifically for when updates call this method
                if reasonToAdd == 'update':
                    print('a?b and b?a')
                    print(prev_a,prev_relation,prev_b)
                    print(new_a,new_relation,new_b)
                    exit(0)
            #this can happen and implies a=b
            if new_relation == '>=' and prev_relation == '>=':
                shouldAdd = True                
                shouldReplace =True
                removeIndex= prev_result 
                prefResult = (prev_a,'=',prev_b)  
                break
            else:
                shouldAdd = False
                break
                
            
            
        #verify this block, i'm not convinced about >= and ! >=
        if prev_a == new_a and prev_b == new_b:
            shouldAdd = False
            #a >= b and a = b or a > b 
            if prev_relation == '>=' and new_relation!='>=':  
                
                #exit(0)              
                shouldReplace = True
                removeIndex= prev_result                
                break
            
    if shouldReplace:
        local_preference_results.remove(removeIndex)
        local_preference_results.append(prefResult)
        return local_preference_results
    
    if shouldAdd:
        local_preference_results.append(prefResult)
    return local_preference_results

def find_local_preference(fibEntryForP,inferior_updates,local_preference_results):
    print("finding local preference",len(inferior_updates))
    updates = sorted(inferior_updates,key=lambda update: update['timestamp'],reverse=True)
    fib_neighbor = helpers.findNeighborInUpdate(fibEntryForP)
    # for update in updates[:10]:
    #     update_neighbor =helpers.findNeighborInUpdate(update)
    #     print(update_neighbor,fib_neighbor, datetime.fromtimestamp(update['timestamp']))
    #exit(0)
    
    fib_path_length = len(splitAsPathFromUpdate(fibEntryForP))
    seenResults = []
    for update in updates:
        update_neighbor = helpers.findNeighborInUpdate(update)
        update_path_length = len(splitAsPathFromUpdate(update))
        prefResult = None
        if update_path_length > fib_path_length:
            prefResult = (fib_neighbor,'>=',update_neighbor)
            
        elif update_path_length == fib_path_length:
            prefResult = (fib_neighbor,'>=',update_neighbor)
            seenResults.append((fib_neighbor,'not_as_path',update_neighbor))
        elif update_path_length < fib_path_length:
            prefResult = (fib_neighbor,'>',update_neighbor)
            seenResults.append((fib_neighbor,'as_path_or_lp',update_neighbor))
        if prefResult == None:
            print("why is pref result none?",prefResult,update,fibEntryForP)
            exit(0)     
        
        local_preference_results = addPreferenceToResults(local_preference_results,prefResult)#this one is not fine to add a>b and b>a
    toAdd = [] 
    toRemove = []
    for a1,relation1,b1 in seenResults:
        for a2, relation2,b2 in seenResults:
            if a1==a2 and relation1 == relation2 and b1 ==b2:
                continue
            if a1 == a2 and b1 == b2:
                if relation1 == 'not_as_path':
                    if relation2 == 'as_path_or_lp':
                        res =  (a1,'>',b1)
                        if res not in toAdd:
                            print("adding ",res,'b/c of NOT OR')
                            toAdd.append(res)
                            toRemove.append(a1,'>=',b1)
                        #can add this result 
                        continue
                elif relation2 == 'not_as_path':
                    if relation1 == 'as_path_or_lp':
                        res =  (a1,'>',b1)
                        if res not in toAdd:
                            print("adding ",res,'b/c of NOT OR')
                            toAdd.append(res)
                            toRemove.append(a1,'>=',b1)
    for r in toRemove:
        local_preference_results.remove(r)
    for a in toAdd:
        local_preference_results.append(a)
                        
            
    return local_preference_results        
def resolve_equals_prefs(local_preference_results):
    someDict = {}
    for a,relation,b in local_preference_results:
        if a not in someDict.keys():
            someDict[a] = {}
        if relation not in someDict[a].keys():
            someDict[a][relation] = [] 
        if b not in someDict[a][relation]:
            someDict[a][relation].append(b)
    print('original ')
    print(someDict)
    equalVals = set()
    for a in someDict:
        try:
            for b in someDict[a]['=']:
                equalVals.add(a)
                equalVals.add(b)
        except Exception as e:
            #print(e)
            pass
    toAdd = []
    for i in range(len(equalVals)):
        val1 = list(equalVals)[i]
        for j in range(len(equalVals)):
            
            val2 = list(equalVals)[j]
            if val1 == val2:
                continue
            for a in someDict:
                allBSet = set()
                shouldAdd = False
                for relation in someDict[a]:
                    listOfBs = someDict[a][relation]
                    for b in listOfBs:
                        allBSet.add(b)
                allBs = list(allBSet)
                if val1 in allBs and val2 not in allBs:
                    shouldAdd = True
                elif val2 in allBs and val1 not in allBs:
                    shouldAdd = True    
                if shouldAdd:
                    for relation in someDict[a]:
                        listOfBs = someDict[a][relation]
                        if val1 in listOfBs:
                            if val2 not in listOfBs:
                               
                                toAdd.append((a,relation,val2))
                                break
                        elif val2 in listOfBs:
                            if val1 not in listOfBs:
                                toAdd.append((a,relation,val1))
                                break
    for a in toAdd:
        local_preference_results = addPreferenceToResults(local_preference_results,a,'resolve_equal_prefs')
                                #add val1
    # if len(equalVals) >0:
    #     print('added',toAdd)
    #     print(local_preference_results)
    #     exit(0)

        

    #i'm not sure this actually does anything but i'll leave it here...
    dgraph = construct_digraph(local_preference_results)
    toRemove = [] 
    toAdd = []
    for a, relation, b in local_preference_results:
        if relation != '>':
            continue
        ab_relation = find_local_policy_relation(a,b,dgraph)
        if ab_relation == '=':
            toRemove.append((a,relation,b))
            toAdd.append((a,'=',b))
    for r in toRemove:
        local_preference_results.remove(r)
    for a in toAdd:
        local_preference_results = addPreferenceToResults(local_preference_results,a,'resolve_equal_prefs')
    return local_preference_results
def createInequalityDict(inequalities):
    someDict = {}
    for a,relation,b in inequalities:
        if a not in someDict.keys():
            someDict[a] = {'>':[],'>=':[],'=':[]}
        # if relation not in someDict[a].keys():
        #     someDict[a][relation] = [] 
        if b not in someDict[a][relation]:
            someDict[a][relation].append(b)
    return someDict

def convertDictToTuples(someDict):
    newTuples = []
    for a in someDict:
        for relation in someDict[a]:
            for b in someDict[a][relation]:
                newTuples.append((a,relation,b))
    return newTuples

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
def resolve_inequalities2(inequalities):
   # print(inequalities)
    someDict = createInequalityDict(inequalities)
    # print('original',someDict)
    # for a in someDict:
    #     for relation in someDict[a]:
    #         # if relation != '>':
    #         #     continue
    #         print(a,relation,someDict[a][relation])
    # print("~~~~~~~~~~")
    G = networkx.DiGraph()
    
    # Add inequalities to the graph
    for a, relation, b in inequalities:
        add_inequality(G, a, relation, b)
    
    # Compute the transitive closure
    closure = networkx.transitive_closure(G)
    for nodeA in G.nodes():
        
        for nodeB in G.nodes():
            if nodeA == nodeB:
                continue           
            
            paths = list(networkx.all_simple_paths(G, source=nodeA, target=nodeB))
            alreadyDone = []
            for path in paths:
                # if path not in alreadyDone:
                #     alreadyDone.append(path)
                # else:
                #     print('not doing ',path)
                #     continue
                good = True
                values = []
                wat = []
                valSum = 0
                for i in range(len(path)):
                    u = path[i]
                    #v = path[i+1]
                    try:
                        v = path[i+1]
                    except:
                        break
                    data = G.get_edge_data(u,v)
                    weight = data['weight']
                    valSum+=weight
                    if weight == -1:
                        good = False
                        break
                    values.append(weight)
                    wat.append((u,weight,v)) #rename this
                    #print(data)
                #the path gives me a > b > c = d so i can just follow it!
                #specifically (a>b)(b=c)(c>d) etc. 
                if good:
                    if valSum > 0:
                        equalVals = set()
                        gtVals = set()
                        gtIndicies = []
                        index = 0
                        for a,value,b in wat:
                            if value == 1:
                               relation = '>'
                            elif value ==0:
                               relation = '='
                            else:
                                print('cannot determine relations of non 0 or 1')
                                print(a,value,b)
                                print(wat)
                                exit(0)
                                break
                            #find all a=b
                            if relation =='=':
                                equalVals.add(a)
                                equalVals.add(b)
                            #find all a>b
                            if relation=='>':
                                gtVals.add((a,b))
                                gtIndicies.append(index)
                            index+=1
                        #current point: there exists no a>b=c>d (check on second iteration)
                        # if len(gtVals) <2:
                        #     continue
                        # exit(0)
                        #if a>b and b=c then a>c. 
                        #what happens if we have 
                        #a=b > c=d=e > f=d
                        for a,b in list(gtVals):
                            if a in equalVals and b in equalVals:
                                print("why is a AND b equal when they shouldnt be?")
                                print(equalVals,gtVals,path)
                                exit(0)
                            if b in equalVals:
                                for val in equalVals:
                                    if val ==b:
                                        continue
                                    if val not in someDict[a]['>']:
                                        someDict[a]['>'].append(val)
                        # print('gt parsing needed')
                        # print(path)
                        # print(values)
                        # print(wat)
                        # exit(0)
                        pass
                    elif valSum==0:
                        for p1 in path:
                            for p2 in path:
                                if p1 ==p2:
                                    continue
                                if p2 not in someDict[p1]['=']:
                                    someDict[p1]['='].append(p2)
                        ##print('all are equal')
                        
                    #print(path)
                    #print(values)
                    #print(wat)
    #print(someDict)
    
    #remove things from >= because we have resolved them
    for a in someDict:
        gteqVals = []
        try:
            for b in someDict[a]['>=']:
                gteqVals.append(b)
        except KeyError:
            continue
        for relation in someDict[a]:
            if relation=='>=':
                continue
            remove = []
            for b2 in someDict[a][relation]:
                if b2 in gteqVals:
                    remove.append(b2)
            for r in remove:
                someDict[a][relation].remove(r)
        
    # for a in someDict:
    #     for relation in someDict[a]:
    #         # if relation != '>':
    #         #     continue
    #         print(a,relation,someDict[a][relation])
    #turn it back into tuple form 
    newTuples = convertDictToTuples(someDict)
    
    return newTuples
def resolveaGTcGTb(local_preference_results):

    #a>=b a>c c>b -> a>b
    #a>=b a=c c>b -> a>b
              
    toRemove = [] 
    toAdd = []
    for a, abRelation,b in local_preference_results:
        if abRelation!='>=': continue
        #found a>=b
        for a1, acRelation, c in local_preference_results:
            if a!= a1 or acRelation=='>=':
                continue
            #found a>c or a=c
            for c1, cbRelation, b1 in local_preference_results:
                if b!=b1 or cbRelation!='>' or c!=c1:
                    continue
                #found c>b 
                rem = (a,'>=',b)
                if rem not in toRemove:
                    toRemove.append(rem)
                res = (a,'>',b)
                if res not in toAdd:
                    toAdd.append(res)
                    
    for r in toRemove:
        local_preference_results.remove(r)
    for a in toAdd:
        local_preference_results.append(a)
    return local_preference_results
    

def expand_results(local_preference_results):
    print('expanding results ',local_preference_results)
    local_preference_results = resolve_equals_prefs(local_preference_results)
    local_preference_results = resolveaGTcGTb(local_preference_results)
    someDict = createInequalityDict(local_preference_results)
    #a >=b, b =c, a >c → a > b is not working
    for a in someDict:
        
        ab_gteq = someDict[a]['>=']
        ab_eq = someDict[a]['=']
        ab_gt = someDict[a]['>']
        #a>=b
        for b in ab_gteq:
            if b ==a:
                print("why do we have a=a?")
                exit(0)
            if b not in someDict.keys():
                continue
            #bc_gteq = someDict[b]['>=']
            bc_eq = someDict[b]['=']
            bc_gt = someDict[b]['>']
            
            for c in bc_eq:
                if c in ab_eq:
                    #a=b
                    if b not in someDict[a]['=']:
                        someDict[a]['='].append(b)
                    if b in someDict[a]['>=']:
                        someDict[a]['>='].remove(b)
                if c in ab_gt:
                    if a == '137409' and (b == '6774' or c == '6774'):
                        print('here:~~~~',a,b,c)
                        #continue
                    
                    #a=b
                    if b not in someDict[a]['>']:
                        someDict[a]['>'].append(b)
                    if b in someDict[a]['>=']:
                        someDict[a]['>='].remove(b)                    
            #for c in bc_gt:
            #     if c in ab_eq:
            #         #c>=b a=c b>c -> b>c #should happen later
            #         pass
            #     if c in ab_gt:
            #         #a>=b a>c b>c
            #         #cant do since both a>b and a>c satisfy a>=b>c
            #         pass
    local_preference_results = convertDictToTuples(someDict)
    acResultsToAppend=[]
    # a?b
    for a,relation1,b in local_preference_results:
        #b?c
        for b2,relation2,c in local_preference_results:
            #ignore duplicates since we're iterating over the whole thing twice
            if a== b2 and relation1 == relation2 and b ==c:
                continue
            #easy a>b case first 
            #a > b > c -> a > c 
            #a > b = c -> a > c 
            #a > b >= c -> a > c 
            if a == b2:
                if relation1 == '>':
                    acResultsToAppend.append((b2,relation2,c))
                    continue
                #a >= b > c -> a > c 
                #a >= b = c -> a = c 
                #a >= b >= c -> a >= c 
                #a = b > c -> a > c 
                #a = b = c -> a = c 
                #a = b >= c -> a >= c 
                else:
                    if relation2 == '>':
                        acResultsToAppend.append((a,'>',c))
                        continue
                    if relation2 == '=':
                        acResultsToAppend.append((a,'=',c))
                        continue
                    if relation2 == '>=':
                        acResultsToAppend.append((a,'>=',c))
                        continue
    #ima have to verify this stuff
    for ac_result in acResultsToAppend:
        local_preference_results = addPreferenceToResults(local_preference_results,ac_result,'expanding_results')
   # print("after: ",local_preference_results)
    #exit(0)
    local_preference_results = resolve_equals_prefs(local_preference_results)

    return local_preference_results
        


def find_ac_relation(a,c,results):
    #technically there should only be one, but we dont limit it jic. (needs verification)
    found = []
    for result in results:
        if result[0] == a and result[1]!= '>=' and result[2] == c:
            found.append(result)
    return found
def eliminate_greater_or_equal(local_preference_results):
    print("eliminating >=", local_preference_results)
    #note b=b2 but we cant name them the same var 
    changeTo=[]
    #a?b
    solvedABRelations = []
    abRemove = []
    for a,relation1,b in local_preference_results:
        if relation1 != '<=':
            continue
        #find b?c relations
        bcRelations = []
        for b2,relation2,c in local_preference_results:
            #ignore duplicates since we're iterating over the whole thing twice
            if a== b2 and relation1 == relation2 and b ==c:
                continue    #b>=c    #b=b
            if relation2 != '>=' and b == b2:
                bcRelations.append((b2,relation2,c))
        
        
        for b, bcOp, c in bcRelations:
            if bcOp != '=':
                continue
            acRelations = find_ac_relation(a,c)
            #we can resolve these cases 
            # a>=b b=c a>c -> a > b 
            # a>=b b=c a=c -> a = b 
            for a2,acOp,c2 in acRelations:
                #a>b
                if acOp =='>':
                    abRemove.append((a,relation1,b))
                    solvedABRelations.append((a,'>',b))
                    
                #a=b    
                if acOp =='=':
                    abRemove.append((a,relation1,b))
                    solvedABRelations.append((a,'=',b))
    for r in abRemove:
        print('removeing',r)
        local_preference_results.remove(r)            
    for r in solvedABRelations:
        print('adding',r)
        local_preference_results.append(r)
    #needs verification
    
    print("after eliminating >=", local_preference_results)
    return local_preference_results
def construct_digraph(local_preference_results):
    dgraph = networkx.DiGraph() 
    for result in local_preference_results:
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
    return dgraph


def all_a_b_exist(local_preference_results):
    #create a directed graph with a node for all a, b in the local_preference_results
    #if a>b add a path from a->b 
    #if a=b add a path from a->b and b->a
    dgraph = construct_digraph(local_preference_results)
    
    for nodeA in dgraph.nodes:
        for nodeB in dgraph.nodes:
            if nodeA == nodeB:
                continue
            try:
                #check if a can reach all other nodes 
                sp = networkx.shortest_path(dgraph,nodeA,nodeB)
                #print(sp)
            except networkx.exception.NetworkXNoPath :
                print("no path between ",nodeA,nodeB)
                #if a cannot reach node b, can b reach a?
                #if so this is fine, this implies b>a
                try:
                    sp = networkx.shortest_path(dgraph,nodeB,nodeA)
                except:
                    print("reverse check no path between ",nodeB,nodeA)
                
                    return False
    return True
def check_if_local_policy_done(local_preference_results,minNeighbors):
    print("is local policy done yet?")
    #check if there exists any a >=b relation in local_preference_results. if there is, we are not done.
    neighborsSet = set()
    for a, relation, b in local_preference_results:
        neighborsSet.add(a)
        neighborsSet.add(b)
        if relation =='>=':
            return False
    exit(0)
    #construct a set containing all unique elements (a,b,...,n) that appear in any a ? b. 
    #if the length is not sufficient, then we are not done. 
    #this set represents the number of neighbors we have results for so far. so the question is: do we have results for enough neighbors?
    if len(neighborsSet) < minNeighbors:
        return False
    #check if we have the preferece of all a ? b. if we do not, then we are not done. 
    if not all_a_b_exist(local_preference_results):
        return False
    
    #if we have passed all checks above, we are done.
    return True
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
            #exit(0)
            return True
    print("fib did not change")
    return False
def findPeerNeighbors(tsStart,observerASN,addV4,addV6):
    print('finding peer neighbors')
    return
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
def find_equal_prefs(results):
    equalPrefs = []
    dgraph = construct_digraph(results)
    for nodeA in dgraph.nodes:
        for nodeB in dgraph.nodes:
            aGTb = False 
            bGTa = False
            if nodeA == nodeB:
                continue
            try:
                #if a can reach b
                sp = networkx.shortest_path(dgraph,nodeA,nodeB)
                aGTb = True
            except networkx.exception.NetworkXNoPath :
                print("no path between ",nodeA,nodeB)
                aGTb = False #just to be explicit
                continue
            try:
                sp = networkx.shortest_path(dgraph,nodeB,nodeA)
                bGTa = True
            except:
                print("reverse check no path between ",nodeB,nodeA)
                bGTa = False #just to be explicit
                continue#no reason to keep going since we need both a->b and b->a to get a<->b

            if aGTb and bGTa:
                res = (nodeA,'=',nodeB)
                equalPrefs = addPreferenceToResults(equalPrefs,res,reasonToAdd='equalPrefs')
    return equalPrefs              
def check_if_p_after_done(p_after_preferences,local_pref_results):
    #check if we have the preferece of all a ? b. where LP(a) = LP(b) if we do not, then we are not done.
    #find all instances of a=b
    equal_LP = find_equal_prefs(local_pref_results)
    equal_lp_set = set()
    p_after_set = set()
    for a,_,b in equal_LP:
        equal_lp_set.add(a)
        equal_lp_set.add(b)
    for a,_,b in p_after_preferences:
        p_after_set.add(a)
        p_after_set.add(b)
    if len(equal_lp_set) != len(p_after_set):
        if len(equal_lp_set) > len(p_after_set):
            print('lp>p_after still missing',equal_lp_set-p_after_set)
        else:#theoretically this case shouldnt happen, but print anyway
            #also exit so we can diagnose wtf is going on
            print('p_after>lp ? why is this? still missing',p_after_set-equal_lp_set)
            exit(0)
        return False
    return True
    
def find_local_policy_relation(a,b,dgraph:networkx.DiGraph):
    """inputs: a,b: two neighbors we want the local_preference relation for
    dgraph: the directed policy graph that represents the policy preferences of all neighbors in N
    returns 
        > if a>b
        = if a=b
        < if a<b
        """
    aGTb = False 
    bGTa = False
    for node in dgraph.nodes:
        if node == a:
            nodeA = node
            #print('found node a')
        if node == b:
            nodeB = node
            #print('found node b')
    try:
        #if a can reach b
        sp = networkx.shortest_path(dgraph,nodeA,nodeB)
        aGTb = True
    except networkx.exception.NetworkXNoPath :
        print("no path between ",nodeA,nodeB)
        aGTb = False #just to be explicit
    #if a cannot reach node b, can b reach a?
    #if so this is fine, this implies b>a
    try:
        sp = networkx.shortest_path(dgraph,nodeB,nodeA)
        bGTa = True
    except:
        print("reverse check no path between ",nodeB,nodeA)
        bGTa = False #just to be explicit
    
    if aGTb and bGTa:
        return '=' #a=b
    if aGTb:
        return '>' #a>b
    if bGTa:
        return '<' #a<b

def find_p_after_values(fibEntryForP,updates_for_p, local_pref_results,p_after_preferences):
    
    dgraph = construct_digraph(local_pref_results)
    
    #U = find_inferior_updates(F,updates[t_-1,t0])
    
    #setup so we dont have to do this multiple times
    fibNeighbor = helpers.getNeighborFromUpdate(fibEntryForP)
    fibPathLen = splitAsPathFromUpdate(fibEntryForP)
    fib_origin = fibEntryForP['origin']
    for update in updates_for_p:
        updateNeighbor = helpers.getNeighborFromUpdate(update)
        #p_after results for the same neighbor will be the same.
        #this is also not useful. 
        if fibNeighbor == updateNeighbor:
            continue
        #LP(F) = LP(u)
        lpValue = find_local_policy_relation(updateNeighbor,fibNeighbor,dgraph)
        if lpValue != '=':
            continue
        updatePathLen = splitAsPathFromUpdate(update)
        #|F| = |u|
        if fibPathLen != updatePathLen:
            continue
        update_origin =  update['origin']
        if fib_origin != update_origin:
            continue
        p_a_result = (fibNeighbor,'>',updateNeighbor)
        p_after_preferences = addPreferenceToResults(p_after_preferences,p_a_result)
    return p_after_preferences        

     

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
                tsStart = helpers.subtractTime(tsStart,hours=hoursToAdd)
                tsEnd = helpers.subtractTime(tsEnd,hours=hoursToAdd)
                continue
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
    #print(fibEntriesForP)
    
    pickle.dump(fibEntryForP,open(storageLocation,'wb'))
    return fibEntryForP,tsStart,tsEnd

def getAllNeighbors(local_pref_results):
    allNeighbors = set()
    for w,o,l in local_pref_results:
        allNeighbors.add(w)
        allNeighbors.add(l)
    return allNeighbors
    
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
    if os.path.exists(pickleDir + f'newTestResults3/{collector}-{observerIP}-{prefixP.replace('/','-')}'):
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
#~~~~~ local preference section ~~~~~ #
#<TODO> min neighbors
    updatesToConsider = []
    oldFibForP = {}
    compared = False
    oldFibForP = {}
    inferior_updates = []
    if os.path.exists(pickleDir+f'/pref_results/{collector}-{observerIP}-{prefixP.replace('/','-')}'):
        local_pref_results = pickle.load(open(pickleDir+f'/pref_results/{collector}-{observerIP}-{prefixP.replace('/','-')}','rb'))
        foundEnoughUpdatesForPolicy = True
    while not foundEnoughUpdatesForPolicy:
        foundUpdates = False
        while not foundUpdates:
            
            if cnt >= maxSearch:
                print('could not find enough information in ',maxSearch,'tries')
                with open('failed_simple_tests2.txt','a+') as f:
                    f.write(f"{collector},{observerIP},{observerASN},{prefixP} failed by max Search {maxSearch}")
                    f.write('\n')
                return 
            fibEntryForP,foundStart,foundEnd = findFibEntryForP(tsStart,tsEnd,prefixP,observerIP,collector)
            if fibEntryForP == None:
                print('no FIB found in 10 days ')
                print('or there was a problem with the query')
                with open('failed_simple_tests.txt','a+') as f:
                    f.write(f"{collector},{observerIP},{prefixP} failed by no fib in 6 days or problem with query")
                    f.write('\n')
                return
            #i dunno about foundStart here... verify this
            #inferior_updates = find_inferior_updates(fibEntryForP,foundStart,observerIP,collector,prefixP)
            new_updates = find_inferior_updates_single_pass(fibEntryForP,foundStart,observerIP,collector,prefixP)
            if len(new_updates) > 0 :
                foundUpdates = True
            else:
                tsStart = helpers.subtractTime(foundStart,hours=hoursToAdd)
                tsEnd = helpers.subtractTime(foundEnd,hours=hoursToAdd)
        if cnt %10 == 0 and cnt!=0:
            MIN_NEIGHBORS = MIN_NEIGHBORS-5
        if MIN_NEIGHBORS <=0:#removeforolddata
            MIN_NEIGHBORS = 10
        if didFibChange(oldFibForP,fibEntryForP):
                inferior_updates = []
                oldFibForP = fibEntryForP
        
        for u in new_updates:
            inferior_updates.append(u)
        #allNeighbors = getAllNeighbors(local_pref_results)
        # if len(allNeighbors)>= MIN_NEIGHBORS:
        #     c = False
        #     for a, op, b in local_pref_results:
        #         if op == '>=':
        #             c= True
        #             break
        #     if c:
        #         foundEnoughUpdatesForPolicy = True 
        #     break
            
        cnt+=1 
        print('lpr before everything ',local_pref_results)
        local_pref_results = find_local_preference(fibEntryForP,inferior_updates,local_pref_results)
        print('lpr after find lp',local_pref_results)
        local_pref_results = expand_results(local_pref_results)
        print('lpr after expanding',local_pref_results)        
        local_pref_results = resolve_inequalities2(local_pref_results)
        print('lpr after resolving inequalities',local_pref_results)
        local_pref_results = eliminate_greater_or_equal(local_pref_results)
        print('lpr after eliminating >=',local_pref_results)
        done = check_if_local_policy_done(local_pref_results,MIN_NEIGHBORS)        
        if not done:
            print("nope...")
            #subtract h hours from t0 and t_-1 where h is 2 for route-views collectors or 8 for RIPE collectors.             
            tsStart = helpers.subtractTime(foundStart,hours=hoursToAdd)
            tsEnd = helpers.subtractTime(foundEnd,hours=hoursToAdd)
        else:
            print("lp done!")
            #only because i dont trust while true loops
            foundEnoughUpdatesForPolicy = True 
            break
    print('dumping results')
    exit(0)
    pickle.dump(local_pref_results,open(pickleDir+f'/pref_results/{collector}-{observerIP}-{prefixP.replace('/','-')}','wb'))
    
#~~~~~ p_after section ~~~~~ #
    
    enough_p_after_values = False
    tsStart = originalStart
    tsEnd = originalEnd
    p_after_preferences = []
    cnt =0
    if os.path.exists(pickleDir+f'/p_after_results/{collector}-{observerIP}-{prefixP.replace('/','-')}'):
        p_after_preferences = pickle.load(open(pickleDir+f'/p_after_results/{collector}-{observerIP}-{prefixP.replace('/','-')}','rb'))
        enough_p_after_values = True
    while not enough_p_after_values:
        foundUpdates = False
        while not foundUpdates:
            if cnt >= maxSearch:
                print('could not find enough information in ',maxSearch,'tries')
                with open('failed_simple_tests.txt','a+') as f:
                    f.write(f"{collector},{observerIP},{observerASN},{prefixP} failed by max Search {maxSearch}")
                    f.write('\n')
                return 
            fibEntryForP,foundStart,foundEnd = findFibEntryForP(tsStart,tsEnd,prefixP,observerIP,collector)
            if fibEntryForP == None:
                print('no FIB found in 10 days ')
                print('or there was a problem with the query')
                with open('failed_simple_tests.txt','a+') as f:
                    f.write(f"{collector},{observerIP},{prefixP} failed by no fib in 6 days or problem with query")
                    f.write('\n')
                return
            #assuming local_preference results hold, we should be able to use any update for P to determine p_after prefrerences
            updates_for_p = get_updates_for_p(foundStart, foundEnd,prefixP,observerIP,collector)
            if len(updates_for_p) > 0 :
                foundUpdates = True
            else:
                tsStart = helpers.subtractTime(foundStart,hours=hoursToAdd)
                tsEnd = helpers.subtractTime(foundEnd,hours=hoursToAdd)
            
        p_after_preferences = find_p_after_values(fibEntryForP,updates_for_p, local_pref_results,p_after_preferences)
        p_after_preferences = expand_results(p_after_preferences)
        done = check_if_p_after_done(p_after_preferences,local_pref_results)
        if not done:
            #subtract h hours from t0 and t_-1 where h is 2 for route-views collectors or 8 for RIPE collectors. 
            tsStart = helpers.subtractTime(foundStart,hours=hoursToAdd)
            tsEnd = helpers.subtractTime(foundEnd,hours=hoursToAdd)
        else:
            #only because i dont trust while true loops
            enough_p_after_values = True 
            break
    pickle.dump(p_after_preferences,open(pickleDir+f'/p_after_results/{collector}-{observerIP}-{prefixP.replace('/','-')}','wb'))
#~~~~~hijacking section ~~~~~ #



    #slightly more efficient method 
    #get playbook W+U from t0 to t1 
    #starter_playbook = build_starter_playbook(start_time, end_time,prefixP,observerIP,collector)
    fibEntryForP,foundStart,foundEnd = findFibEntryForP(tsStart,tsEnd,prefixP,observerIP,collector)
    #all updates except W's that dont deal with P e.g. W(q,t0)
    allUpdates = getAllUpdates(foundStart,foundEnd,prefixP,observerIP,collector)
    
    successfulHijackingUpdates = []
    failedHijackings = []#[{'reason':update}]
    hijacking_id = 0
    for update in allUpdates:  
        if fibEntryForP == None:
            if update['prefix'] == prefixP:
                fibEntryForP = updateFIB(update)  
                continue
            else:
                successfulHijackingUpdates.append(update)
                #we do this later
                #storeWhyHwasAccepted(update,'empty_FIB',hijacking_id)
                hijacking_id+=1
                continue

        fib_neighbor = helpers.getNeighborFromUpdate(fibEntryForP)
        fib_path_len = len(splitAsPathFromUpdate(fibEntryForP))
        fib_origin = fibEntryForP['origin_type']

        if update['prefix']!= prefixP:
            wasHijackingUpdate = True
        else:
            wasHijackingUpdate = False
        reasons = []
        #if wasHijackingUpdate:
        foundReason = None
        foundFailReason = None
        shouldUpdate = False
        wasSuccessful = check_LP(update,fibEntryForP,local_pref_results)

        if wasSuccessful != None:
            if wasSuccessful == True:
                shouldUpdate = True
                foundReason = 'local_pref'
            else:
                foundFailReason = 'local_pref'
                #reasons.append('local_pref')
        wasSuccessful = check_as_path_len(update,fibEntryForP)
        if wasSuccessful != None:
            #if this was successful and we dont already have a reason that the update should update or not
            if wasSuccessful == True and foundReason == None:
                shouldUpdate = True
                foundReason = 'as_path'
            else:
                foundFailReason = 'as_path'
        wasSuccessful = check_origin(update,fibEntryForP)
        if wasSuccessful != None:
            if wasSuccessful == True and foundReason == None:
                shouldUpdate = True
                foundReason = 'origin_type'
            else:
                foundFailReason = 'origin_type'
                # reasons.append('origin_type')
        wasSuccessful =check_p_after(update,fibEntryForP,p_after_preferences)
        if wasSuccessful != None:
            if wasSuccessful == True and foundReason == None:
                shouldUpdate = True
                foundReason = 'p_after'
            else:
                foundFailReason = 'p_after'
        if shouldUpdate:
            if wasHijackingUpdate:
                successfulHijackingUpdates.append(update)
              
                if foundReason != None:
                    #storeWhyHwasAccepted(update,r, hijacking_id)
                    #we do this later
                    hijacking_id+=1
                    break
                else:
                    print("why is the reason None?")
                    exit(0)
            else:
                fibEntryForP = updateFIB(update)
        if wasHijackingUpdate and not shouldUpdate:
            #storeWhyHFailed  
            failedHijackings.append((update,foundFailReason))# = []#[{'reason':update}]      
    playbook = build_starter_playbook(foundStart,foundEnd,prefixP,observerIP,collector)
    testPlaybooks = [] 
    pickle.dump(failedHijackings,open(pickleDir+f'failed_hijackings/{collector}-{observerIP}-{prefixP.replace('/','-')}','wb'))
    
    #successful hijacking updates each have a unique ID from 0-N
    #these unique IDs should correspond with their index in testPlaybooks
    for h in successfulHijackingUpdates:
        playbook_with_h = insert_H_into_playbook(playbook,h)
        testPlaybooks.append(playbook_with_h)
    #multithreadding here? 
    resultsDict = {}
    for i,playbook in enumerate(testPlaybooks):
        successfulHijackingUpdate = successfulHijackingUpdates[i]
        origin_asns = successfulHijackingUpdate['origin_asns']
        hijacker_as = origin_asns[0]
        if hijacker_as not in resultsDict:
            resultsDict[hijacker_as] = []
        #if len(origin_asns) ==1:
            #hijacker_as = origin_asns[0]
        #else:
            #hijacker_as =
        print(f"running playbook {i}/{len(testPlaybooks)}")
        playbookResults = runPlaybook_with_successful_hs(playbook,fibEntryForP,local_pref_results,p_after_preferences,hijacking_id=i,hijacking_update=successfulHijackingUpdate)
        resultsDict[hijacker_as].append(playbookResults)
    pickle.dump(resultsDict,open(pickleDir+f'newTestResults3/{collector}-{observerIP}-{prefixP.replace('/','-')}','wb'))

#~~~~hijacking functions section ~~~~#
def updateFIB(update):
    if update['elem_type'] == 'W':
        return None
    else: return update

    #check if H(q,t_h) is successful, (dont insert it into fib)
#unsuccessfull H's are marked as such. 

def build_starter_playbook(start_time, end_time,prefixP,observerIP,collector):
    broker = helpers.createBroker()
    items = helpers.queryBroker(broker,start_time,end_time,collector,'update')
    filters = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='all')
    helpers.addPrefixToFilter(filters,prefix=prefixP)
    playbook = []
    for item in items:
        parser = helpers.parseFileWithParams(item,filters)
        for update in parser:
            playbook.append(update)
    return sorted(playbook,key=lambda update: update['timestamp'],reverse=True)
def getAllUpdates(start_time, end_time,prefixP,observerIP,collector):
    broker = helpers.createBroker()
    items = helpers.queryBroker(broker,start_time,end_time,collector,'update')
    filters = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='all')
    allUpdates = []
    for item in items:
        parser = helpers.parseFileWithParams(item,filters)
        for update in parser:
            #ignore W's that dont deal with P 
            if update['elem_type'] == 'W' and update['prefix']!=prefixP:
                continue
            allUpdates.append(update)
    return allUpdates

def insert_H_into_playbook(playbook:list,hijacking_update):
    hijacking_timestamp = helpers.convertTimeToUnix(hijacking_update['timestamp'])
    #double check off by 1
    insertAt = None
    for i, update in enumerate(playbook):
        update_timestamp = helpers.convertTimeToUnix(update['timestamp'])
        if update_timestamp > hijacking_timestamp:
            insertAt = i
            break
    if insertAt !=None:
        playbook.insert(insertAt,hijacking_update)
    else:
        playbook.append(hijacking_update)
    return playbook

def check_LP(update,fibEntryForP,local_pref_results): 
    dgraph = construct_digraph(local_pref_results)
    fibNeighbor = helpers.getNeighborFromUpdate(fibEntryForP)
    updateNeighbor = helpers.getNeighborFromUpdate(update)
    lpValue = find_local_policy_relation(updateNeighbor,fibNeighbor,dgraph)
    if lpValue == '<':
        #update should not be adopted
        return False
    if lpValue == '=':
        #we need more information in order to determine if the update should be adopted
        return None
    if lpValue == '>':
        #the update should be adopted into the FIB 
        return True 
def check_as_path_len(update,fibEntryForP,):
    fib_path_len = len(splitAsPathFromUpdate(fibEntryForP))
    update_path_len = (len(splitAsPathFromUpdate(update)))
    #|F| > |u| -> u should be adopted
    if fib_path_len > update_path_len:
        return True
    #|F| = |u| -> we dont know if u should be adopted
    if fib_path_len == update_path_len:
        return None
    #|F| < |u| -> u should NOT be adopted
    if fib_path_len < update_path_len:
        return False
    
def check_origin (update,fibEntryForP):
    """checks the origin type returns 
    true if update should be adopted
    false if update should not be adopted 
    none if we dont know at this step. 
    NOTE: typically we say that routers prefer lower origin types, but using integer values with > makes more sense to me.
      though this is likely because we use > or = to represent policy prefernces.
    """
    origin_types_dict = {'IGP':3, 'EGP':2, 'INCOMPLETE':1}
    fib_origin = fibEntryForP['origin_type']
    update_origin = update['origin_type']
    if origin_types_dict[fib_origin] > origin_types_dict[update_origin]:
        return True        
    if origin_types_dict[fib_origin] == origin_types_dict[update_origin]:
        return None        
    if origin_types_dict[fib_origin] < origin_types_dict[update_origin]:
        return False        
def findPAfterPreference(update,fibEntryForP,p_after_preferences):
    
    fibNeighbor = helpers.getNeighborFromUpdate(fibEntryForP)
    updateNeighbor = helpers.getNeighborFromUpdate(update)
    #hopefully we dont see this, but same neighbors will have same preferences
    if fibNeighbor == updateNeighbor:
        return None
    dgraph = construct_digraph(p_after_preferences)
    #we should be able to use the same function, but the graphs will look different.
    return find_local_policy_relation(updateNeighbor,fibNeighbor,dgraph)

def check_p_after(update,fibEntryForP,p_after_preferences):
    p_after_val = findPAfterPreference(update,fibEntryForP,p_after_preferences)
    if p_after_val == '<':
        #update should not be adopted
        return False
    if p_after_val == '=':
        #we need more information in order to determine if the update should be adopted
        return None
    if p_after_val == '>':
        #the update should be adopted into the FIB 
        return True 
def printPlaybookResult(playbookResults:dict):
   
    print('found H was better than',
          len(playbookResults['whyIsBetterThan'],'updates.\n it spent ',
          playbookResults['totalTimeInFib'],'time in the FIB\n'),
          'it was removed by: ',playbookResults['whyRemoved'])
    
def runPlaybook_with_successful_hs(playbook,fibEntryForP,local_pref_results,p_after_preferences,hijacking_id,hijacking_update):
    #we assume the P in the FIB at t0 is legitimate
    #to extend results, simply extend the end time of the playbook
    originalPrefix = fibEntryForP['prefix']
    startTimeOfFib = fibEntryForP['timestamp']
    fibWasChanged = False
    fibEntryForP['hijacker'] = False
    hijackerKickedOut = False
    lastGoodUpdate = ''
    hijackingUpdate = hijacking_update
    playbookResults = {'hijacker_id': hijacking_id,
                       'hijackerUpdate': hijacking_update,#todo
                       'whyAccepted': (),#entry it beat,reason why it won 
                       'whyIsBetterThan': [],#[(update:reason)],
                       'timePutIntoFib': hijacking_update['timestamp'],#we can only do this because we KNOW this update will be accepted at this point in time
                       'timeOutOfFib': 0.0,
                       'totalTimeInFib': 0.0,
                       'whyRemoved': ()#(update,reason)
                    }
    for update in playbook:  
        #if the hijacker was removed then we can stop testing since theres nothing left to learn from this test. 
        if hijackerKickedOut:
            break
        #set a field in the update so we always know if this update is malicious or not
        if update['prefix']!= originalPrefix:
            wasHijackingUpdate = True
            update['hijacker']=True
        else:
            wasHijackingUpdate = False
            update['hijacker']=False
        #if the FIB is empty due to a W message
        if fibEntryForP == None:
            #this update is not malicious
            if update['prefix'] == originalPrefix:
                #did it kick the hijacker out of the FIB?
                if fibEntryForP['hijacker'] == True:
                    hijackerKickedOut = True
                else:
                    hijackerKickedOut = False
                fibEntryForP = updateFIB(update)  
                
                continue
            else:
                lastGoodUpdate = update
                fibEntryForP = updateFIB(update)  
                #fibEntryForP['hijacker']=True
                #storeWhyHwasAccepted(update,'empty_FIB',hijacking_id)
                playbookResults['whyAccepted'] = (update,'empty_fib')
                #hijackingUpdate = update
                continue

  
        reasons = []

        wasSuccessful = check_LP(update,fibEntryForP,local_pref_results)
        if wasSuccessful != None:
            reasons.append('local_pref')
        wasSuccessful = check_as_path_len(update,fibEntryForP)
        if wasSuccessful != None:
            reasons.append('as_path')
        wasSuccessful = check_origin(update,fibEntryForP)
        if wasSuccessful != None:
            reasons.append('origin_type')
        wasSuccessful =check_p_after(update,fibEntryForP,p_after_preferences)
        if wasSuccessful != None:
            reasons.append('p_after')
        #fib should be changed 
        if len(reasons) > 0:
            if wasHijackingUpdate:
                for r in reasons:
                    if r != None:
                        reason = r 
                        break
                fibEntryForP = updateFIB(update)
                #storeWhyHwasAccepted(update,reason,hijacking_id)
                playbookResults['whyAccepted'] = (update,reason)
                hijackingUpdate = update
                continue
            else:
                lastGoodUpdate = update
                #did it kick the hijacker out of the FIB?
                if fibEntryForP['hijacker'] == True:
                    hijackerKickedOut = True
                else:
                    hijackerKickedOut = False

                fibEntryForP = updateFIB(update)
                continue

        #fib did not change, why did it not change? (we only care about H)
        #is the fib entry currently populated by a hijacker?
        if fibEntryForP['hijacker']:
            #in this case, fib_entry is malicious, update is benign
            #storeWhyHIsBetterThanB(fibEntryForP,update,hijacking_id)
            playbookResults['whyIsBetterThan'].append((update,reason))
    #did we get here because the hijacker was kicked?
    #startTimeOfFib
    
    
    endTimeOfPlaybook = playbook[-1]['timestamp']
    endDateTimeOfPlaybook =  datetime.fromtimestamp(endTimeOfPlaybook)
    lastUpdateTimestamp = lastGoodUpdate['timestamp']
    hijackerTimestamp = hijackingUpdate['timestamp']
    lasteBUpdateDateTime = datetime.fromtimestamp(lastUpdateTimestamp)
    hijackerDateTime = datetime.fromtimestamp(hijackerTimestamp)
    #timeHijackerInFib = lasteBUpdateDateTime - hijackerDateTime
    
    #print(tdiff)
    
    
    if hijackerKickedOut:
        #storeHowLongHijackerWasInFib(playbook,lastGoodUpdate)
        playbookResults['timeOutOfFib'] = lastUpdateTimestamp
        playbookResults['totalTimeInFib'] = lasteBUpdateDateTime - hijackerDateTime
        playbookResults['whyRemoved'] = (lastGoodUpdate,reason)
    else:
        playbookResults['timeOutOfFib'] = None
        playbookResults['totalTimeInFib'] = endDateTimeOfPlaybook - hijackerDateTime
        playbookResults['whyRemoved'] = "it was not removed"
        #storeWhyHWasKicked(lastGoodUpdate)
    printPlaybookResult(playbookResults)
    return playbookResults
        #
        #This is where I currently am. <ret here>
        #ima have to marinade on this for a while.
        #i need to know: 1: is the hijacker currently populating the FIB?
        #did an update kick H out of the fib?
        #why was H better than b (for both insertion and why it didnt get kicked out)
        #how long H was in the FIB for, i think that one is the key
        #have two sections, one that tracks H as FIB entry for P and one that just does normal things. 
        #when H is accepted, kick into gear. when it falls out (or we run out of updates) break and be done with this testing.

if __name__ == "__main__":
    print("simple training 2!")
    main()
    #example: route-views.sg 18106 27.111.228.6 103.84.52.0/24 2024-03-30T00:00:00 60
