import helpers 
import statistics 
from datetime import datetime
import networkx
from random import shuffle



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
def extendWithGraphs(inequalities,useShortestPath=True):
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
                if useShortestPath:
                    paths = networkx.all_shortest_paths(G,node_A,node_B)
                else:
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
    #print(inequalities)
    for newR in newRes:
        inequalities,isNewRes = addPreferenceToResults_new(inequalities,newR)
        madeCycle, cycles = helpers.detectCycles(inequalities)
        if madeCycle:
            inequalities.remove(newR)
        inequalities = helpers.removeInferiorResults(inequalities)
        #print(inequalities)
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

def findGreatestDiff(allUpdates):
    tdiffs = []
    for i in range(len(allUpdates)):
        update1 = allUpdates[i]
        try:
            update2 = allUpdates[i+1]
        except:
            # bucket.append(update2)
            # neighbors.add(helpers.findNeighborInUpdate(update2))
            # buckets.append((bucket,neighbors))
            break
        tdiff = update2['timestamp']-update1['timestamp']
        if tdiff not in tdiffs:
            tdiffs.append(tdiff)
            #tdiffs.append(update2['timestamp']-update1['timestamp'])
    return sorted(tdiffs,reverse=True)
    
def splitUpdates(allUpdates):  
    print('spliting updates')
    allUpdates = sorted(allUpdates,key=lambda x:x['timestamp'])        
    # print('start ts',allUpdates[0]['timestamp'])
    # print('end ts',allUpdates[-1]['timestamp'])
    # print('is end > start? it should be. ', allUpdates[-1]['timestamp'] > allUpdates[0]['timestamp'])
    # exit(0)
    tdiffs = findGreatestDiff(allUpdates)
    #tdiff = tdiffs[0]
    print('tdiff',tdiffs[0],tdiffs[-1])
    for tdiff in tdiffs:
        for i in range(len(allUpdates)):
            update1 = allUpdates[i]
            try:
                update2 = allUpdates[i+1]
            except:
                break
            updateDiff = update2['timestamp']-update1['timestamp']
            if updateDiff >6.0 and updateDiff < 8.0:
                print('ud',updateDiff)
            if updateDiff == tdiff:
                if i == 0:#len(allUpdates)-1:
                    continue
                return allUpdates[:i], allUpdates[i:]
        print(tdiff,'not found, trying next')
    if len(allUpdates)==2:
        return [],[]
    print('cant find tdiff')
    exit(0)
def findActiveNeighbors(updates):
    neighbors = set()
    for update in updates:
        neighbors.add(helpers.findNeighborInUpdate(update))
    return neighbors
def getPrefDict(updates):
    prefDict = {}
    for update in updates:
        prefix = update['prefix']
        if prefix not in prefDict.keys():
            prefDict[prefix] = [] 
        prefDict[prefix].append(update)
    return prefDict
def testBucket(bucketUpdates):
    print('testing bucket')
    bucketRes = []
    neighbors = findActiveNeighbors(bucketUpdates)
    print(neighbors)
    prefDict = getPrefDict(bucketUpdates)
    prefList = []
    for prefix in prefDict:
        prefList.append(prefix)
    shuffle(prefList)
    for prefix in prefList:
        someUpdates = sorted(prefDict[prefix],key=lambda x:x['timestamp'],reverse=True)
        if len(prefDict[prefix])<=1:
            continue
        #print(prefix,len(prefDict[prefix]))
        for i in range(len(someUpdates)):  

            update1 = someUpdates[i]
            try:
                update2 = someUpdates[i+1]
            except:
                break  
            if update1['elem_type'] == 'W' or update2['elem_type']=='W':
                continue
            update1Neighbor = helpers.findNeighborInUpdate(update1)
            update2Neighbor = helpers.findNeighborInUpdate(update2)
            if update1Neighbor == update2Neighbor:
                continue
            update1Path = helpers.splitASPathFromUpdate(update1)
            update2Path = helpers.splitASPathFromUpdate(update2)
            
            if update1Path == None:
                update1Path = []
            if update2Path == None:
                update2Path = []
            if update1Neighbor not in neighbors:
                continue 
            if update2Neighbor not in neighbors:
                continue 
            res = None
            if len(update2Path) > len(update1Path):
                res = (update2Neighbor,'>',update1Neighbor)
            # else:
            #     res = (update2Neighbor,'>=',update1Neighbor)
            if res not in bucketRes and res != None:
                #print(prefix,'adding res',res)
                # print(update2)
                # print(update1)
                # input()
                bucketRes.append(res)

    if len(bucketRes)==0:
        return True, []
    #print('before contra',bucketRes)            
    contras = helpers.findContradictions(bucketRes)            
    if len(contras) == 0:
        print('no contras found')
        return True,bucketRes
        allRes.append(bucketRes)
        
        #print(bucketRes)
        bucketRes = []
    else:
        print('contras found')
        return False, ''
        newBuckets.append(bucketUpdates)
        bucketRes = []
def areUpdatesSame(update1,update2):
    
    for key in update1.keys():
        # if key == 'timestamp':
        #     print(update1[key])
        #     print(update2[key])
        if key =='communities':
            oldCom = update2[key]            
            newCom = update1[key]
            if oldCom != None and newCom!=None:
              
                if set(oldCom) == set(newCom):
                    same = True 
                else:
                    same = False
                    
                    return False
            else:
                if oldCom == newCom:
                    same = True
                else:
                    same = False
                    return False
                
            continue
        
        if update2[key] != update1[key]:
            return False
    return True
        
# collector = 'route-views2'
collector = 'rrc04'
startTime = '2024-05-30T00:00:00' 
# observerIP = '37.139.139.17' #routeviews2
# observerIP = '192.65.185.3' #rrc04
observerIP = '192.65.185.130' #rrc04
#observerIP = '202.93.8.242' #rv2 573 prefixes
# observerIP ='144.228.241.130' #rv2 46076
ripePeers = helpers.getRipePeers()
numFiles = 5 #(30 mins for rv 10 for rrc)
endTime = helpers.addTime(startTime,minutesToAdd=helpers.get_minutesForFile(collector)*numFiles)#(8*15)*cnt) #15*cnt
def helperFunc(args):
    #print(args)
    arg = args[0]
    startTime,endTime,collector,observerIP = arg
    helpers.getMergedCleanUpdates(startTime,endTime,collector,observerIP)
# import arbMultiProcessing
# args = []
# for peer_asn,peer_ip in ripePeers['rrc04']['peers']:
#     args.append((startTime,endTime,collector,peer_ip))
    
# arbMultiProcessing.goManageArgs(helperFunc,args,10)
# print(ripePeers['rrc04']['peers'])

allUpdates = []
maxUpdates = -1
#depricated
burstLength = 100# .0002#.0005 #.00000000015 #waaaaaay too small
cnt = 1
numFiles = 5 #(30 mins for rv 10 for rrc)
endTime = helpers.addTime(startTime,minutesToAdd=helpers.get_minutesForFile(collector)*numFiles)#(8*15)*cnt) #15*cnt
cnt+=1
allUpdates = helpers.getMergedCleanUpdates(startTime,endTime,collector,observerIP)
    


print('found',len(allUpdates),'updates')

#exit(0)
allUpdates = sorted(allUpdates,key=lambda x: x['timestamp'])
tdiffs = []
#burstLength = .5
#burstLength = .00001 #too small
# burstLength = .0000125 #too small

buckets = [] 
buckets.append(allUpdates)
allRes = []
bucketRes = []
recurse = True
newBuckets = []
rec = 0 
splitBuckets = buckets
while recurse:
    rec +=1 
    print('recursing ',rec)
    if rec > 50:
        break
    b = 1
    #input('continue recurse?')
    if len(newBuckets)>0:
        buckets = newBuckets
    for singleBucket in buckets:
        #print(type(singleBucket[0]),type(buckets[0]),'types')
        if len(newBuckets)>0:
            newBuckets.remove(singleBucket)
        #exit(0)
    #for b in range(len(buckets)):
        print(f'working on {b}/{len(buckets)} with len',len(singleBucket))
        b+=1
        if len(singleBucket) ==0:
            continue
    # print(bucketUpdates[0])
        #print(len(splitBuckets[0]),len(splitBuckets[1]))
        # exit(0)
        #for bucketUpdates in singleBucket:
        noContras,values = testBucket(singleBucket)
        if noContras:
            if len(values)>0:
                combined = []
                for resList in allRes:
                    for res in resList:
                        # print(res)
                        # print('~~~')
                        if res not in combined:
                            combined.append(res)
                valsToCheck = combined                            
                for i in range(len(values)):
                    res = values[i]
                    if res not in valsToCheck:
                        valsToCheck.append(res)
                    badChange = helpers.detectBadChange_noexit(valsToCheck,'internal combine')                        
                    if badChange:
                        valsToCheck.remove(res)
                for res in valsToCheck:
                    if res not in combined:
                        combined.append(res)                            
                #this only includes results that wont cause contradiction#throws out all results even if we find a new one. 
                badChange = helpers.detectBadChange_noexit(combined,'internal combine')
                if not badChange:
                #if len(helpers.findContradictions(combined)) ==0:
                    allRes.append(valsToCheck)
                else:
                    splitBuckets = splitUpdates(singleBucket)
                    print(len(splitBuckets[0]),len(splitBuckets[1]))
                    newBuckets.append(splitBuckets[0])
                    newBuckets.append(splitBuckets[1])
        else:
            splitBuckets = splitUpdates(singleBucket)
            print(len(splitBuckets[0]),len(splitBuckets[1]))
            newBuckets.append(splitBuckets[0])
            newBuckets.append(splitBuckets[1])
    #buckets = newBuckets
    if len(newBuckets) ==0:
        break
    else:
        print('go again!',len(buckets))
        #print(buckets)
    # for res in allRes:
    #     print(res)
    #     print('~~~')
combined = []
for resList in allRes:
    for res in resList:       
        if res not in combined:
            print(res)
            combined.append(res)
helpers.detectBadChange(combined,'combined')

innercnt = 0    
haveNewResults = True
while haveNewResults:
    combined, haveNewResults = extendWithGraphs(combined,useShortestPath=False)
    if innercnt > 10:
        input('this seems to be taking a while...?')
    innercnt+=1     
done = helpers.all_a_b_exist(combined)
print('are we SUPER done? ',done)
print(combined)


exit(0)            
