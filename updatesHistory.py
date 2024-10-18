#TODO find out why i get a contradiction, e.g
import helpers
import bgpkit
import networkx
from datetime import datetime, timedelta
# collector = 'route-views2'
collector = 'rrc04'
startTime = '2024-05-30T00:00:00' 
# observerIP = '37.139.139.17'
observerIP = '192.65.185.3'
prefixP = '103.232.225.0/24'
endTime = startTime
#endTime = helpers.addTime(startTime,minutesToAdd=200)#30,15 doesnt work
endTime = helpers.addTime(startTime,minutesToAdd=30)#30,15 doesnt work
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
      #  allUpdates.append(elem)
# # otherTime = helpers.addTime(startTime,hoursToAdd=2)
# # allUpdates = helpers.get_all_updates_for_p(otherTime,observerIP,collector,prefixP)        
# for update in sorted(allUpdates,key=lambda x: x['timestamp']):
#     updateTime = helpers.convertUpdateToTimestring(update)
#     updatePath = helpers.splitASPathFromUpdate(update)
#     print(len(helpers.splitASPathFromUpdate(update)),'-',update['as_path'],helpers.convertUnixToTimeString(update['timestamp']))#,lengthOfStay)
import pickle 
# pickle.dump(prefDict,open('pickles/doubleUpdateTest.pickle','wb'))
# prefDict = pickle.load(open('pickles/singleRibTest.pickle','rb'))
# prefDict = pickle.load(open('pickles/singleUpdateTest.pickle','rb'))
# prefDict = pickle.load(open('pickles/doubleUpdateTest.pickle','rb'))
from itertools import product
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
# allUpdates = []
# allres = []
# prefDict = {} 

# for prefix in prefDict:
#     #print(prefix)
#     #for update in prefDict[prefix]:
#     allUpdates = prefDict[prefix]
#     sUpdates = sorted(allUpdates,key=lambda x: x['timestamp'])    
#     for i in range(len(sUpdates)):
#         update1 = sUpdates[i]
#         try:
#             update2 = sUpdates[i+1]
#         except:
#             break
#         update1Neighbor = helpers.findNeighborInUpdate(update1)
#         update2Neighbor = helpers.findNeighborInUpdate(update2)
#         if update1Neighbor == update2Neighbor:
            
#             #reason = whatChanged(update1,update2)
#             #print(reason)
            
#             # if reason == 'timestamp':
#             print(update1,update2)
#                 # exit(0)

def exitUpdate(update):
    if update['elem_type']=='W':
        return
    if update['local_pref']!=0:
        print(update)
        exit(0)
    if update['med']!=0:            
        print(update)
        exit(0)

def getResult(a,b,prefDict,testPrefixes,skipctr):
    print('finding result for ',a,b)
    found = 0
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
            
            if found == skipctr:    
                return res
            else:
                found+=1
    return None
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

neighborDict = {}
prefToRemove = []
testPrefixes = []
for prefix in prefDict:
    testPrefixes.append(prefix)
from random import shuffle
#shuffle(testPrefixes)    
neighbors = set()
for prefix in testPrefixes:
    #print(prefix)
    for update in prefDict[prefix]:
        neighbor = helpers.findNeighborInUpdate(update)
        if neighbor == None:
            continue
        neighbors.add(neighbor)
neighbors = set(shuffle(list(neighbors)))        
needResults = {}
for n1 in list(neighbors):
    if n1 not in needResults:
        needResults[n1]= {'?':[],'<':[],'>':[],'=':[],'>=':[],'<=':[]}
    for n2 in list(neighbors):
        if n1 ==n2:
            continue
        needResults[n1]['?'].append(n2)
print(needResults)
print(len(neighbors))
#i want to find the relation of a to b in needResults
#do we already have a result? if yes, skip.
#if no, find it and change it. 


allResults = []
for a in needResults:
    for b in needResults[a]['?']:
        skipctr = 0
        result = getResult(a,b,prefDict,testPrefixes,skipctr)        
        if result == None:
            pass
            #print(a,b,'relation needs to be extrapolated or time extended')
        else:
            if result not in allResults:
                allResults.append(result)
                badChange = helpers.detectBadChange_noexit(allResults,'allres')
                
                while badChange:
                    if skipctr > 10:
                        print('skipping > 10')
                        exit(0)
                #if badChange:
                    skipctr +=1
                    allResults.remove(result)
                    result = getResult(a,b,prefDict,testPrefixes,skipctr)  
                    if result == None:
                        break
                    else:
                        allResults.append(result)
                        badChange = helpers.detectBadChange_noexit(allResults,'allres')
allResults = helpers.removeInferiorResults(allResults)
allResults = findEqualityOfGTEQ(allResults)
contras = helpers.findContradictions(allResults)
for res in allResults:
    print(res)
print('~~~~')
for c in contras:
    print(c)
haveNewResults = True 
innercnt = 0    
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
print(helpers.all_a_b_exist(allResults))
exit(0)
for _ in range(9):
        # if update['atomic']!= 'NAG' or update['aggr_asn']!= None or update['aggr_ip']!=None:
        #     if prefix not in prefToRemove:
        #         prefToRemove.append(prefix)
        
        exitUpdate(update)
        neighbor = helpers.findNeighborInUpdate(update)
        if neighbor not in neighborDict:
            neighborDict[neighbor] = []
        path = helpers.splitASPathFromUpdate(update)
        #print(neighbor,len(path))
        if len(path) not in neighborDict[neighbor]:
            neighborDict[neighbor].append(len(path))
print(len(neighborDict))
for prefix in prefToRemove:
    prefDict[prefix] = []
def whyDidUpdateReplace(prevUpdate,replacingUpdate):
    if prevUpdate['elem_type'] =='W':
        return 'empty FIB'
    if replacingUpdate['elem_type'] =='W':
        return 'withdraw'
    tdiff = getTimeDiff(prevUpdate,replacingUpdate)
    prevUpdateNeighbor = helpers.findNeighborInUpdate(prevUpdate)
    replacingUpdateNeighbor = helpers.findNeighborInUpdate(replacingUpdate)
    nString = f"{helpers.convertUpdateToTimestring(prevUpdate)} {prevUpdateNeighbor} -> {replacingUpdateNeighbor} @ {tdiff}"
    
    prevUpdateTime = helpers.convertUpdateToTimestring(prevUpdate)
    replacingUpdateTime = helpers.convertUpdateToTimestring(replacingUpdate)
    
    #print(update1,update2)
    prevUpdatePath = helpers.splitASPathFromUpdate(prevUpdate)
    replacingUpdatePath = helpers.splitASPathFromUpdate(replacingUpdate)

    
    
    if len(prevUpdatePath) < len(replacingUpdatePath):
        return 'likely p_before - as_path'+ nString

    if len(prevUpdatePath) > len(replacingUpdatePath):
        return 'as_path'+ nString
    #implicit |U1| = |U2| 

    prevUpdateOrigin =  prevUpdate['origin']
    replacingUpdateOrigin = replacingUpdate['origin']
    origin_types_dict = {'IGP':1, 'EGP':2, 'INCOMPLETE':3}
    if origin_types_dict[prevUpdateOrigin] <  origin_types_dict[replacingUpdateOrigin]:
        return 'origin'+ nString
    if origin_types_dict[prevUpdateOrigin] >  origin_types_dict[replacingUpdateOrigin]:
        return 'likely p_before - origin'+ nString
    #implicit origin(U1) = origin(U2)
    reasonChanged = whatChanged(prevUpdate,replacingUpdate)
    return 'unknown'+ nString +' '+ reasonChanged

           

# for neighbor in neighborDict:
#     print(neighbor,max(neighborDict[neighbor]))
# print(len(neighborDict))    
# exit(0)
#for _ in range(1):
def changeResults(prefix,neighbor,preferencesDict):
    for i in range(len(preferencesDict[prefix])):
        oldRes = preferencesDict[prefix][i]
        a,r,b = oldRes
        if a == neighbor or b == neighbor:
            preferencesDict[prefix][i] = (a,'?',b)
    return preferencesDict      


reasonsDict = {}
sameNeighsDict = {}
sameNeighs = []
preferencesDict = {}
for prefix in prefDict:
    if prefix not in reasonsDict:
        reasonsDict[prefix] = []
        sameNeighsDict[prefix] = []
        preferencesDict[prefix] = []
    allUpdates = prefDict[prefix]
    sUpdates = sorted(allUpdates,key=lambda x: x['timestamp'])
    # if len(sUpdates) > 10:
    #     continue
    for i in range(len(sUpdates)):    
        update1 = sUpdates[i]
        try:
            update2 = sUpdates[i+1]
        except:
            break
        update1Neighbor = helpers.findNeighborInUpdate(update1)
        update2Neighbor = helpers.findNeighborInUpdate(update2)
        whyReplace = whyDidUpdateReplace(update1,update2)
        # if update1Neighbor == update2Neighbor:
        #     sameNeighsDict[prefix].append(reason)
        reasonsDict[prefix].append((whyReplace,update1,update2))
        update1Path = helpers.splitASPathFromUpdate(update1)
        update2Path = helpers.splitASPathFromUpdate(update2)
        if len(update1Path)< len(update2Path):
            res = (update2Neighbor,'>',update1Neighbor)
        else:
            res = (update2Neighbor,'>=',update1Neighbor)
        if update1Neighbor == None or update2Neighbor == None:
            continue                
        if update1Neighbor == update2Neighbor:
            reason = whatChanged(update1,update2)
            if reason =='communities':
                if update1Neighbor not in sameNeighs:
                    sameNeighs.append(update1Neighbor)
                for pref2 in preferencesDict:
                    preferencesDict = changeResults(pref2,neighbor,preferencesDict)
            continue
        if res not in preferencesDict[prefix]:
            preferencesDict[prefix].append(res)
merged = []            
for prefix in prefDict:                        
    if len(preferencesDict[prefix])==0:
        continue
    print(prefix)
    for i in range(len(preferencesDict[prefix])):
        reason = preferencesDict[prefix][i]
        print(reason)
# exit(0)        
       # print(reason) 
#         a,r,b = reason 
#         for neighbor in sameNeighs:
            
#             if a == neighbor or b == neighbor:
#                 preferencesDict[prefix][i] = (a,'?',b)
                
            # if neighbor == '174':
            #     print(reason)
            #     print(preferencesDict[prefix][i])
            #     input()    
        #     exit(0)
for prefix in prefDict:                        
    if len(preferencesDict[prefix])==0:
        continue
    #print(prefix)      
    for i in range(len(preferencesDict[prefix])):
        reason = preferencesDict[prefix][i]
        a,r,b = reason
        if a == '174' or b =='174':
          pass#  print(reason) 
        a,r,b = reason 
        if r != '?':
            if reason not in merged:
                merged.append(reason) 
print(sameNeighs)
print(merged)

helpers.removeInferiorResults(merged)        

#helpers.detectBadChange(merged,'merged1')

merged = findEqualityOfGTEQ(merged)
contras = helpers.findContradictions(merged)   
print('contras',contras)
helpers.detectBadChange(merged,'merged2')    
total = 0
sumReasons = {'p_before-as_path':0,'p_before-origin':0,'as_path':0,'origin':0,'unknown':0}
unknownReason = {}
for prefix in reasonsDict:
    if prefix not in unknownReason:
        unknownReason[prefix] = []
    if len(reasonsDict[prefix])==0:
        continue
    print(prefix)
    for reason,update1,update2 in reasonsDict[prefix]:
        total+=1
        print(reason)
        if 'p_before' in reason:
            if 'as_path' in reason:
                sumReasons['p_before-as_path']+=1
            else:
                sumReasons['p_before-origin']+=1
            continue
        if 'as_path' in reason:
            sumReasons['as_path']+=1
            continue
        if 'origin' in reason :
            sumReasons['origin']+=1
            continue
        if 'unknown' in reason:
            sumReasons['unknown']+=1
            unknownReason[prefix].append((update1,update2))
            continue
def listMostChanges(update1,update2):
    difString = ""
    # if update1['elem_type'] == 'W':
    #     return 
    # if update2['elem_type']=='W':
    #     return
    for key in update1.keys():
        if key == 'timestamp':
            continue
        if key == 'communities':
            continue
        if update1[key]!=update2[key]:
            difString= difString + key + ' '+str(update1[key])+'->'+str(update2[key])+' '
    return difString
print(total)
print(sumReasons)
# print(unknownReason)
allReasons = {}
for prefix in unknownReason:
    
    if len(unknownReason[prefix])==0:
        continue
    #print(prefix)
    for updateTuple in unknownReason[prefix]:
        update1,update2 = updateTuple
        thingChanged = whatChanged(update1,update2)
        if thingChanged not in allReasons:
            allReasons[thingChanged]=0
        allReasons[thingChanged]+=1    
        #print(thingChanged)
        changes = listMostChanges(update1,update2)
        if changes !="":
            print(prefix,changes)
        continue
        if thingChanged != 'communities':
            print(prefix,thingChanged,update1[thingChanged],update2[thingChanged])
            if thingChanged == 'aggr_ip':
                if update1['aggr_asn'] != update2['aggr_asn']:
                    print('aggrasn',update1['aggr_asn'],update2['aggr_asn'])
            if thingChanged == 'aggr_asn':
                if update1['aggr_ip'] != update2['aggr_ip']:
                    print('aggrip',update1['aggr_ip'],update2['aggr_ip'])
        # print(update1)
        # print(update2)

print(allReasons)
#helpers.detectBadChange(merged,'merged2')    
exit(0)
haveNewResults = True
innercnt =0
print(merged)
#helpers.plotTuplesWithWeight(merged,True,False)    

while haveNewResults:
    
    merged, haveNewResults = extendWithGraphs(merged)
    if innercnt > 10:
        input('this seems to be taking a while...?')
    innercnt+=1 


print(merged)
exit(0)                    
# print(reasonsDict)
# exit(0)

for prefix in prefDict:
    allUpdates = prefDict[prefix]
    #allUpdates = prefDict['162.244.222.0/24']
    sUpdates = sorted(allUpdates,key=lambda x: x['timestamp'])
    for i in range(len(sUpdates)):    
        update1 = sUpdates[i]
        try:
            update2 = sUpdates[i+1]
        except:
            break
        update1Neighbor = helpers.findNeighborInUpdate(update1)
        update2Neighbor = helpers.findNeighborInUpdate(update2)
        if update1Neighbor == update2Neighbor:
            reason = whatChanged(update1,update2)    
            print(reason)
#prev total 8365
#ignoring same neighbors (n1=n1)
#5839
exit(0)
for _ in range(0):        
    for _ in range (0):
        update1Time = helpers.convertUpdateToTimestring(update1)
        update2Time = helpers.convertUpdateToTimestring(update2)
        
        #print(update1,update2)
        update1Path = helpers.splitASPathFromUpdate(update1)
        update2Path = helpers.splitASPathFromUpdate(update2)
        if len(update1Path)==0 or len(update2Path)==0:
            continue
        update1Neighbor = helpers.findNeighborInUpdate(update1)
        update2Neighbor = helpers.findNeighborInUpdate(update2)
        if update1Neighbor == update2Neighbor:
            continue
        print(update1Time,update2Time,update1['timestamp']==update2['timestamp'])
        if len(update1Path)< len(update2Path):
            res = (update2Neighbor,'>',update1Neighbor)
        else:
            res = (update2Neighbor,'>=',update1Neighbor)
        
        if res not in allres:
            # a2,r2,b2 = res
            # for a1,r1,b1 in allres:
            #     if a1
            allres.append(res)
    # if res not in prefixRes[prefix]:
    #     prefixRes[prefix].append(res)   
    # update1 = allUpdates[i]
    # try:
    #     update2 = allUpdates[i+1]
    # except:
    #     break
    # update1Time = helpers.convertUpdateToTimestring(update1)
    # update2Time = helpers.convertUpdateToTimestring(update2)
helpers.removeInferiorResults(allres)
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
allNeighbors = helpers.getAllNeighborsFromResults(allres)
for n in allNeighbors:
    for res in allres:
        if n == res[0]:
            print(res)
contras = findContradictions(allres)
print('contras?')
for c in contras:
    contra1,contra2 = c
    if contra1[1]!=contra2[1]:
        print(c)
toRemove = []
toAdd = []
for res1 in allres:
    a1,r1,b1 = res1
    for res2 in allres:
        a2,r2,b2 = res2
        if res1 == res2:
            continue
        if a1 == b2 and a2 == b1:
            if r1 != '=' and r2 != '=':
                if (a1,'=',b1) not in toAdd:
                    toAdd.append((a1,'=',b1))
                    toAdd.append((a2,'=',b2))
                    toRemove.append(res1)
                    toRemove.append(res2)
for a in toAdd:
    allres.append(a)
for r in toRemove:
    allres.remove(r)
for r in allres:
    print(r)
print(allres)