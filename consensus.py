import helpers
import bgpkit
import networkx
from datetime import datetime, timedelta
from random import shuffle
import pickle 

def getComboList(update):
    as_path = helpers.splitASPathFromUpdate(update)
    sumMinus = []
    for as1 in as_path:
        for as2 in as_path:
            if as1 == as2:
                continue
            dif = int(as1)-int(as2) 
            if dif > 0:
                sumMinus.append(dif)
            sumMinus.append(int(as1)+int(as2))
    communities = update['communities']
    communityActions = []
    for com in communities:
        if 'lg' in com: #ignore large communities (for now)
            continue
        splitCom = com.split(':')
        instructingAS = splitCom[0]
        action = splitCom[1]
        communityActions.append(action)
    return sumMinus,communityActions
def getTimeDiff(update1,update2):
    dt1 = datetime.fromtimestamp(update1['timestamp'])
    dt2 = datetime.fromtimestamp(update2['timestamp'])
    td = dt2-dt1
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = td.microseconds
    # Format the output based on non-zero values
    parts = []
    if hours > 0:
        parts.append(f"{hours}hs")
    if minutes > 0 or hours > 0:  # Include minutes if there's an hour or minute
        parts.append(f"{minutes}min")
    if seconds > 0 or not parts:  # Always include seconds if no other part
        parts.append(f"{seconds}sec")
    parts.append(f"{microseconds}ms")
    timestr =  ' '.join(parts)
    #sumMinus1,communityActions1 =getComboList(update1)
    #sumMinus2,communityActions2 =getComboList(update2)
    
    return timestr
def whatChanged(update1,update2):
    for key in update1.keys():
        if key == 'timestamp':
            continue
        if key =='as_path':
            if update2[key] != update1[key]:
            # print("fib changed!")
            #exit(0)
                return key
        if key =='communities':
            oldCom = update2[key]            
            newCom = update1[key]
            if oldCom != None and newCom!=None:
              
                if set(oldCom) == set(newCom):
                    same = True 
                else:
                    same = False
                    # print(helpers.splitASPathFromUpdate(update1),helpers.convertUpdateToTimestring(update1),update1['prefix'])#update1['timestamp'],)
                    # print(helpers.findNeighborInUpdate(update1))
                    # print(set(oldCom)-set(newCom),update1['timestamp'])
                    # print(set(newCom)-set(oldCom),update2['timestamp'])
                    # timeStr = getTimeDiff(update1,update2)
                    # print(timeStr)
                
                    #find time difference between update 1 and update 2
                    # print(oldCom)
                    # print(newCom)
                    return f'communities'# {set(oldCom) - set(newCom)}'
            else:
                if oldCom == newCom:
                    same = True

                else:
                    same = False
                    return 'communities'
                
            continue
        if update2[key] != update1[key]:
            # print("fib changed!")
            #exit(0)
            return key
    # print("fib did not change")
    return 'timestamp'

def exitUpdate(update):
    if update['elem_type']=='W':
        return
    if update['local_pref']!=0:
        print(update)
        exit(0)
    if update['med']!=0:            
        print(update)
        exit(0)

def getResult(a,b,prefDict,testPrefixes):
    print('finding result for ',a,b)
    found = 0
    allRes = []
    for prefix in testPrefixes:
        allUpdates = prefDict[prefix]
        sUpdates = sorted(allUpdates,key=lambda x: x['timestamp'])
        # if len(sUpdates) > 10:
        #     continue
        #print(len(sUpdates))
        for i in range(len(sUpdates)):    
            update1 = sUpdates[i]
            try:
                update2 = sUpdates[i+1]
            except:
                break
            
            update1Neighbor = helpers.findNeighborInUpdate(update1)
            update2Neighbor = helpers.findNeighborInUpdate(update2)
            if update1Neighbor != a and update1Neighbor!=b:
                continue
            if update2Neighbor != a and update2Neighbor!=b:
                continue
            if update1Neighbor == update2Neighbor:
                continue
            
            update1Path = helpers.splitASPathFromUpdate(update1)
            update2Path = helpers.splitASPathFromUpdate(update2)
            if len(update1Path)< len(update2Path):
                res = (update2Neighbor,'>',update1Neighbor)
            else:
                res = (update2Neighbor,'>=',update1Neighbor)
            allRes.append(res)
    return allRes
def findEqualityOfGTEQ(results):
    print('finding equality gteq')
    remove = [] 
    change = []
    for a1,r1,b1 in results:
        originalRes = (a1,r1,b1)
        for a2,r2,b2 in results: 
            #weird = False  
            newRes = (a2,r2,b2) 
            if a1== b1 and a2==b2 and r1 ==r2:
                continue
            if a1 == b2 and b1 == a2:
                if r1 =='>=' and r2 ==">=":
                    if (a2,r2,b2) not in remove:
                        remove.append((a2,r2,b2))
                        remove.append((a1,r1,b1))
                        change.append((a1,'=',b1))
                        change.append((a2,'=',b2))
   
    for r in remove:
        results.remove(r)
    for a in change:
        results.append(a)
    return results

def discardKnownResults(hiconf_lp,startingLp):
    discard = []
    for a,r,b in hiconf_lp:
        for new_a,new_r,new_b in startingLp:
            new_res = (new_a,new_r,new_b)
            #we know this result already so discard it
            if a == new_a and r ==new_r and new_b ==b:
                if new_res not in discard:
                    discard.append(new_res)
                continue
            if a == new_a and new_b == b:
                #if we have a more specific result, discard it
                if r !='>=':
                    if new_res not in discard:
                        discard.append(new_res)
                    continue
            if a == new_b and new_a == b:
                #if we have a more specific result, discard it (but for b?a)
                if r !='>=':
                    if new_res not in discard:
                        discard.append(new_res)
                    continue
    for d in discard:
        startingLp.remove(d)
    return startingLp
def addPreferenceToResults_new(local_preference_results:list,prefResult,reasonToAdd='update'):
    # print('should we add',prefResult,'to ',local_preference_results,'?')
    
    #good i think?
    newResult = prefResult
    new_a = prefResult[0]
    new_relation= prefResult[1]
    new_b=prefResult[2]
    #dont add a ? a 
    if new_a == new_b:
        return local_preference_results,False
    shouldAdd = True
    shouldReplace = False
    for prev_result in local_preference_results:
        prev_a = prev_result[0]
        prev_relation= prev_result[1]
        prev_b=prev_result[2]
        #dont add results we've already seen
        if prev_a == new_a and prev_b == new_b and prev_relation ==new_relation:
            return local_preference_results,False
        #dont add results of b ? a unless we have a>=b and b>=a  
        if prev_b == new_a and prev_a == new_b:
            #dont add new results when we already have a specific one
            if new_relation != '>=' and prev_relation != '>=':
              return local_preference_results,False
            if new_relation != '>=' and prev_relation =='>=':
                shouldReplace = True
                removeIndex= prev_result 
            shouldAdd = False
        if prev_a == new_a and prev_b == new_b:
            if new_relation =='>' and prev_relation =='>':
                print("a>b b>a addprefnew")
                exit(0)
            if new_relation != '>=' and prev_relation != '>=':
                return local_preference_results,False
            
            shouldAdd = False
            #a >= b and a = b or a > b 
            if prev_relation == '>=' and new_relation!='>=':  
          
                shouldReplace = True
                removeIndex= prev_result                
                break
            
    if shouldReplace:
        #print("replacing ",removeIndex,' with',prefResult)
        local_preference_results.remove(removeIndex)
        local_preference_results.append(prefResult)
        return local_preference_results,True
    
    if shouldAdd:
        #print('adding',prefResult)
        local_preference_results.append(prefResult)
    return local_preference_results, True
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
def extendWithGraphs(inequalities):
    print('extending with graphs!')
    
    if inequalities  == None:
        return inequalities, False
    G = networkx.DiGraph()    
    # Add inequalities to the graph
    shouldContinue = False
    for x, relation, y in inequalities:
        add_inequality(G, x, relation, y)
    #no reason to extend if we're done.
    # basically if we have a >= then we can extend, if we dont then we shouldnt.         
        if relation == '>=':
            shouldContinue = True
    if not shouldContinue:
        return inequalities, False
    found = []
    for node_A in G.nodes():
        for node_B in G.nodes():
            if node_A == node_B:
                continue
            if networkx.has_path(G,node_A,node_B):
                # paths = networkx.all_shortest_paths(G,node_A,node_B)
                paths = networkx.all_simple_paths(G,node_A,node_B)
                for path in paths:
                    if len(path)<=2:
                        continue
                    isZeroPath = False
                    pathWeights = []
                    for i in range(len(path)):
                        u = path[i]
                        try:
                            v = path[i+1]
                        except:
                            break
                        data = G.get_edge_data(u,v)
                        weight = data['weight']
                        pathWeights.append(weight)
                    if all (w==0 for w in pathWeights):
                        if (node_A,'=',node_B) not in found:
                            found.append((node_A,'=',node_B))
                            found.append((node_B,'=',node_A))
                        break
                    if 1 in pathWeights:

                        if (node_A,'>',node_B) not in found:
                            found.append((node_A,'>',node_B))
                   
    newResults = []
    for f in found:
        if f not in inequalities:
            newResults.append(f)
                
    newRes = discardKnownResults(inequalities,newResults)
    haveNewRes = False
    oldInequalities = inequalities
    for newR in newRes:
        inequalities,isNewRes = addPreferenceToResults_new(inequalities,newR)
        madeCycle, cycles = helpers.detectCycles(inequalities)
        if madeCycle:
            inequalities.remove(newR)
        inequalities = helpers.removeInferiorResults(inequalities)
        helpers.detectBadChange(inequalities,'inner extend graphs')
        if isNewRes:
            haveNewRes = True
    if haveNewRes:
        pass
        # print('before')
        # print(oldInequalities)
        # print("adding",newRes) 
        # print('after')
        # print(inequalities)
    return inequalities, haveNewRes

collector = 'route-views2'
# collector = 'rrc04'
startTime = '2024-04-30T00:00:00' 
observerIP = '37.139.139.17' #routeviews
# observerIP = '192.65.185.3' #rrc04
prefixP = '103.232.225.0/24'
endTime = startTime
#endTime = helpers.addTime(startTime,minutesToAdd=200)#30,15 doesnt work
if 'rrc' in collector:
    fileDelta = 5
else:
    fileDelta = 15
for run in range(200):
    print('working on run ',run)
    endTime = helpers.addTime(startTime,minutesToAdd=fileDelta*(run+1))#30,15 doesnt work
    broker = helpers.createBroker()
    items = broker.query(startTime,endTime,collector,data_type='update')
    filters = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='all')
    #helpers.addPrefixToFilter(filters,prefix=prefixP)\
    prefDict = {}
    for item in items:
        parser = helpers.parseFileWithParams(item,filters)
        for elem in parser:
            prefix = elem['prefix']
            if prefix not in prefDict:
                prefDict[prefix] = [] 
            prefDict[prefix].append(elem)


    neighborDict = {}
    prefToRemove = []
    testPrefixes = []
    for prefix in prefDict:
        testPrefixes.append(prefix)

    #shuffle(testPrefixes)    
    neighbors = set()
    for prefix in testPrefixes:
        #print(prefix)
        for update in prefDict[prefix]:
            neighbor = helpers.findNeighborInUpdate(update)
            if neighbor == None:
                continue
            neighbors.add(neighbor)

    print(len(neighbors))
    #i want to find the relation of a to b in needResults
    #do we already have a result? if yes, skip.
    #if no, find it and change it. 


    allResults = []
    consensus = {}
    for a in neighbors:
        for b in neighbors:
            if a == b:
                continue
            if a not in consensus:
                consensus[a] = {} 
            consensus[a][b] = {'>':0,'>=':0}
    #print(consensus)        
    for a in consensus:
        for b in consensus[a]:
            skipctr = 0
            results = getResult(a,b,prefDict,testPrefixes)        
            if len(results) == 0:
                continue
            for res in results:
                a,r,b = res
                # if a not in consensus:
                #     consensus[a] = {}
                # if b not in consensus[a]:
                #     consensus[a][b] = {'>':0,'>=':0}
                consensus[a][b][r]+=1    
            
                #print(a,b,'relation needs to be extrapolated or time extended')
    greatest = []
    possiblyEQ = []
    allRes = []
    for a in neighbors:
        for b in neighbors:
            if a == b:
                continue
            #consensus[a][b] = {'>':0,'>=':0}
            GTres = None
            if consensus[a][b]['>'] > consensus[b][a]['>']:
                GTres = (a,'>',b)
            elif consensus[a][b]['>'] == consensus[b][a]['>']:
                if consensus[a][b]['>'] == 0 and consensus[b][a]['>'] == 0:
                    pass
                else:
                    print(a,b,'are equal ? they have same consensus of >',consensus[a][b]['>'])
                    possiblyEQ.append((a,'=',b))
                    #GTres = (a,'=',b)
                #exit(0)
            else:
                GTres = (b,'>',a)
            gtEQres = None
            if consensus[a][b]['>='] > consensus[b][a]['>=']:
                gtEQres = (a,'>=',b)
            elif consensus[a][b]['>='] == consensus[b][a]['>=']:
                if consensus[a][b]['>='] == 0 and consensus[b][a]['>=']==0:
                    pass
                else:
                    print(b,a,'are equal ? they have same consensus of >=',consensus[a][b]['>='],)
                    #gtEQres = (a,'=',b)
                #exit(0)
            else:
                gtEQres = (b,'>=',a)
            if gtEQres == None and GTres == None:
                continue
            if gtEQres != None:
                a2,r2,b2 = gtEQres
                gtEQSum = consensus[a2][b2][r2]
            else:
                gtEQSum = 0
            if GTres != None:
                
                a3,r3,b3 = GTres
                GTSum = consensus[a3][b3][r3]
                #print(gtEQres,GTres,)
            else:
                GTSum = 0 
            if gtEQSum > GTSum:
                allRes.append(gtEQres)
            elif gtEQSum < GTSum:
                allRes.append(GTres)
            elif gtEQSum == GTSum and gtEQSum ==0:
                continue
            else:
                allRes.append((a2,'=',b2))
                #print(gtEQres,GTres)   
                #          
    print(allRes)
    helpers.detectBadChange(allRes,'allres1')
    contras = helpers.findContradictions(allRes)
    print(contras)
    haveNewResults = True 
    innercnt = 0    
    allResults = allRes
    while haveNewResults:
        allResults, haveNewResults = extendWithGraphs(allResults)
        if innercnt > 10:
            input('this seems to be taking a while...?')
        innercnt+=1 
    contras = helpers.findContradictions(allResults)
    for res in allResults:
        print(res)
    print('~~~~')
    for c in contras:
        print(c)    
    print('~~~')
    print(allResults)
    done = helpers.all_a_b_exist(allResults)
    if done:
        print("DONE")
        exit(0)

exit(0)
