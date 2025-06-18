import pickle 
import gzip
import helpers
import graphHelpers
import time as timemodule
#startTime = '2025-03-01T00:00:00' 
startTime = '2025-03-26T00:00:00' 
#startTime = '2025-03-30T00:00:00' 
endTime = '2025-03-31T00:00:00'    
testEndTime = '2025-04-01T00:00:00'
import sys 
#print(sys.argv[1])
#exit(0)
collector_type = 'ripe'
observers = pickle.load(open('observers.pickle','rb'))
# print(len(observers['ripe']))
# exit(0)

#collector,asn,ip = observers['ripe'][3] #orig test
#observerids=[3,8] 
#8 has issues that need to be investigated
#10 wont work on 5 day
#neither will 11-13, but 14,15 are fine ?

# observerids = [11,12,13,14,15]
# for id in observerids:
#     broker = helpers.createBroker()
#     collector,asn,ip = observers['ripe'][id]
#     filepath = f'/mnt/research/pickles_2025/poster_test/{collector}-{asn}-{ip}-5day.pickle'
    
#     print(collector,asn,ip)
#     items = helpers.queryBroker(broker,startTime,endTime,collector,'updates')
# # #ts=0
# # #for item in items:
# #     #ts= ts + item.rough_size
# # #print(ts, ts/1024,'k',ts/1024/1024,'m')    
# # #exit(0)
#     params = helpers.addFiltersNotPrefix(peer_ip=ip,peer_asn=str(asn))
#     neighbor_dict = {}
#     i = 0
#     # max_updates = 10
#     for item in items:
#         parser = helpers.parseFileWithParams(item,params)
#         # if i > max_updates:
#         #     break
#         for elem in parser:
#             # i+=1
#             # if i % 10000 == 0:
#             #     print('parsed ',i,'updates...')
#             #print(elem)

#             # if i > max_updates:
#             #     break 
    
#             prefix = elem['prefix']
#             update_type = elem['elem_type']
#             as_path = elem['as_path']
#             origin_type = elem['origin']
#             timestamp = elem['timestamp']
#             if prefix not in neighbor_dict:
#                 neighbor_dict[prefix] = []
#             neighbor_dict[prefix].append((update_type,as_path,origin_type,timestamp))
#     # #prefix:(update_type,as_path,origin_type,timestamp)
#     print('dumping...')
#     with gzip.open(filepath,'wb') as f:
#         pickle.dump(neighbor_dict,f)
#     #pickle.dump(neighbor_dict,open(filepath,'wb'))
    
# exit(0)
#pickle.dump(neighbor_dict,open('test_dict2.pickle','wb'))
#exit(0)
#give up on 8 T.T
#14 is big
#16 doesnt work
#21 is ipv6 (i'm also assuming 23 is as well)

observer_ID = int(sys.argv[1])# 15
collector,asn,ip = observers[collector_type][observer_ID]
#filepath = f'/mnt/research/pickles_2025/poster_test/{collector}-{asn}-{ip}.pickle'
filepath = f'/mnt/research/pickles_2025/poster_test/{collector}-{asn}-{ip}-5day.pickle'
neighbor_dict_filepath = filepath    
    #pickle.dump(neighbor_dict,f)

#neighbor_dict = pickle.load(open('test_dict2.pickle','rb'))
#print(neighbor_dict)
#exit(0)

import networkx 
import matplotlib.pyplot as plt

def make_dgraph(neighbor_dict,graphType):
    if graphType == 'd':
        dgraph = networkx.DiGraph()
    elif graphType =='n':
        dgraph = networkx.Graph()
    asns = set('root')
    dgraph.add_node('root')
    numprefs = 10
    for prefix in neighbor_dict:
        numprefs-=1
        if numprefs <=0:
            break
        updatesList = neighbor_dict[prefix]
        for i in range(len(updatesList)):             
            update1 = updatesList[i]
            #print(update1)
            update_type1,as_path1,origin_type1,timestamp1 = update1
            as_path1 = helpers.splitASPathFromString(as_path1)
            for asn in as_path1:
                if asn not in asns:
                    asns.add(asn)
                    dgraph.add_node(asn)
            #dgraph.add_nodes_from(as_path1)
            paths = []
            #dgraph.add_edge('root',as_path1[0])
            paths.append(('root',as_path1[0]))
            as_path = list(set(as_path1))
            for i in range(len(as_path)):
                if i+1 >= len(as_path):
                    break
                
                a = as_path[i]
                b = as_path[i+1]
                paths.append((a,b))
            dgraph.add_edges_from(paths)
    return dgraph

def find_root(dgraph:networkx.DiGraph):
    root = list(dgraph['root'].keys())[0]
    print('found root:',root)

    return root
    #print()

from random import choice, shuffle
def get_next_direction(directions):
    return choice(directions)
def random_walk(graph:networkx.Graph, start_node, walk_length):
    walk = [start_node]
    current = start_node
    # adj = graph.adjacency()
    # for node in adj:
    #     print(node)
    #exit(0)
    walks = {}  # Dictionary to store walks per neighbor
    #print(start_node,type(start_node))
    #exit(0)
    try:
        neighbors = graph.neighbors(start_node)
    except:
        print(start_node, "not in graph!")
        return []
    for neighbor in neighbors:
        path = [start_node, neighbor]  # Start at N and move to the neighbor
        current_node = neighbor

        for _ in range(walk_length - 1):  # Already took 1 step to neighbor
            next_nodes = list(graph.neighbors(current_node))
            if not next_nodes:
                break  # Dead end
            current_node = choice(next_nodes)
            # while current_node in path:
            #     current_node = choice(next_nodes)
            path.append(current_node)

        walks[neighbor] = path
    hij = set()
    for key in walks:
        values = walks[key]
        for value in values:
            hij.add(value)
    while 'root' in hij:
        hij.remove('root')
    #print(walks)
    #print(hij)
    return hij

    for _ in range(walk_length):
        neighbors = list(graph.neighbors(start_node))
        if forCollector:
            neighbors = list(graph.successors(current))
        # else:
        #     neighbors = list(dgraph.predecessors(current))
        if not neighbors:
            break  # Stop if no further neighbors (dead end)
        current = choice(neighbors)
        walk.append(current)

    return walk
def root_directions(dgraph:networkx.DiGraph):
    root = find_root(dgraph)
    directions = []
    for r, n in dgraph.edges(root):
        directions.append(n)
    return directions        
#     print('found directions:',directions)
#     for direction in directions:
#         print(direction)
#         for _ in range(9):
#             next_edges = dgraph.edges(direction)
#             next_directions = [t[1] for t in next_edges]
#             direction=get_next_direction(next_directions)
#             print(direction)
#         exit(0)
        #for _ in range(9):
            
            #for r,next in :
             #   get_next_direction(dgraph.edges(next))
              #  print('\t',n)

    #pass
#print(neighbor_dict)

# for key in neighbor_dict:
#     print(key)

def get_hijackers(neighbor_dict,victims,observerASN,all_known_neighbors):
    
    dgraph = make_dgraph(neighbor_dict,'n')
    #graphHelpers.show_graph(dgraph,1,0)
    root = find_root(dgraph)
    print('hijackers root: ',root)
    hijackers = set()
    hijackers = random_walk(dgraph,root,10)
    print(hijackers)
    for v in victims:
        victim_hijackers = random_walk(dgraph,v,10) 
        #print(v)
        #print(victim_hijackers)       
        hijackers = hijackers.union(victim_hijackers)        
        #print(len(hijackers))
    if str(observerASN) in hijackers:        
        hijackers.remove(str(observerASN))
    
    print("selected hijackers: ",hijackers)        
    #print(observerASN,list(hijackers)[:4])
    #exit(0)
    return hijackers
def create_hijacking_updates(hijackers,neighbor_dict):
    #OBSERVER <TODO> build this from that ew
    dgraph = make_dgraph(neighbor_dict,'n')    
    root = find_root(dgraph)
    created_updates = []
    for h in hijackers:
        update_type = 'A'
        prefix='fill_me_in'
        path = networkx.shortest_path(dgraph,root,h)
        pathstr = ""
        for asn in path:
            pathstr = pathstr +' '+asn
        origin_type='IGP'
        timestamp = helpers.convertTimeToUnix(endTime)
        fake_update = {'fill_me_in':(update_type,pathstr[1:],origin_type,timestamp),'asn':h}
        created_updates.append(fake_update)
    #print(created_updates)
    return created_updates

def find_hijacker_updates(hijackers,neighbor_dict):
    prefixes = list(neighbor_dict.keys())
    hijacking_updates = []
    create = []
    for h in hijackers:
        print('trying to find update for hijacker',h)
        shuffle(prefixes)
        for prefix in prefixes:
            prefixList = neighbor_dict[prefix]
            shuffle(prefixList)
            found = False
            for update in prefixList:
                if update[0] == 'W':
                    continue
                path = update[1]
                path = helpers.splitASPathFromString(path)
                #print(path[-1],h)
                if h == path[-1]:
                    print('found')
                    hijacking_updates.append({prefix:update,'asn':h})
                    # print(update)
                    # exit(0)
                    found = True
                    break
            if found:
                break
        if not found:
            print('not found')
            create.append(h)
            #hijacking_updates.append(f'{h} create')
    created = create_hijacking_updates(create,neighbor_dict)
    for u in created:
        hijacking_updates.append(u)
    #print(hijacking_updates)
    return(hijacking_updates)

#prefix = prefixes[0]
#print(neighbor_dict[prefix][0][1])

#print(path)  
#exit(0)
#sinks = [node for node in dgraph.nodes if dgraph.out_degree(node) == 0]

#print(sinks)

import os 
double_check = f'/mnt/research/pickles_2025/poster_test/double_check{observer_ID}.pickle'

if not os.path.exists(double_check):  
    print('loading...')
    with gzip.open(filepath,'rb') as f:
        neighbor_dict = pickle.load(f)
    if neighbor_dict == {'this is ipv6'}:
        print(observer_ID,'cannot be done on an ipv6 addr rn.')
    print('done loading')
    prefResults = {'>':{},'=':{}}
    #for _ in range(0):
    gtset = set() 
    eqset = set()
    for prefix in neighbor_dict:
    # print(prefix)
        results =  []
        updatesList = neighbor_dict[prefix]
        #print(updatesList)
        updatesList = sorted(neighbor_dict[prefix],key=lambda x: x[-1])
        # if len(updatesList) > 1:
        #     for l in updatesList:
        #         print(l,helpers.convertUnixToTimeString(l[-1]))
        #     #print(updatesList)
        #     exit(0)
        # continue
        
        for i in range(len(updatesList)):
            if i+1 >= len(updatesList):
                break
            
            update1 = updatesList[i]
            #print(update1)
            update_type1,as_path1,origin_type1,timestamp1 = update1
            update2 = updatesList[i+1]
            update_type2,as_path2,origin_type2,timestamp2 = update2
            if update_type1 == "W" or update_type2 == "W":
                continue
            as_path1 = helpers.splitASPathFromString(as_path1)
            as_path2 = helpers.splitASPathFromString(as_path2)
            
            if as_path1 == None or as_path2 == None:
                continue
            if len(as_path2) > len(as_path1):
                n1 = helpers.findNeighborASPath(as_path1)
                n2 = helpers.findNeighborASPath(as_path2)            
                if n2 != n1:
                    res = (n2,'>',n1)
                    if res in gtset:
                        oldcount = prefResults['>'][res]['count']
                        newcount = oldcount+1
                        prefResults['>'][res]={'timestamp':timestamp2,'count':newcount}
                    else:
                        gtset.add(res)
                        prefResults['>'][res]={'timestamp':timestamp2,'count':1}
    # print(prefResults)
        #exit(0)
        eqs = []
        for i in range(len(updatesList)):
            if i+2 >= len(updatesList):
                break
            update1 = updatesList[i]
            update_type1,as_path1,origin_type1,timestamp1 = update1
            update2 = updatesList[i+1]
            update_type2,as_path2,origin_type2,timestamp2 = update2
            update3 = updatesList[i+2]
            update_type3,as_path3,origin_type3,timestamp3 = update3
            if update_type1 == "W" or update_type2 == "W" or update_type3 == "W":
                continue
            as_path1 = helpers.splitASPathFromString(as_path1)
            as_path2 = helpers.splitASPathFromString(as_path2)
            as_path3 = helpers.splitASPathFromString(as_path3)
            #if len(as_path2) > len(as_path1):
            try:
                n1 = helpers.findNeighborASPath(as_path1)
                n2 = helpers.findNeighborASPath(as_path2)
                n3 = helpers.findNeighborASPath(as_path3)
                
            except:
                print(n1)
                print(n2)
                print(n3)
                exit(0)
            if n1 == n3 and n1 != n2:
                    
                    if origin_type1 == origin_type2 and origin_type1 == origin_type3:
                        res = (n1,'=',n2)
                    #results.append()
                        if res in eqset:
                            oldcount = prefResults['='][res]['count']
                            newcount = oldcount+1
                            prefResults['='][res]={'timestamp':timestamp2,'count':newcount}
                        else:
                            eqset.add(res)
                            prefResults['='][res]={'timestamp':timestamp2,'count':1}
                #results.append((n1,'=',n2))
        # if len(results)>0:
        #     prefResults[prefix] = results        
    #     if len(results)>0:
    #         prefResults[prefix] = results
    #print(prefResults)
    gtres = prefResults['>']
    #ensure link is not down between O, n1 and O, n2
    rem = []
      
    for key in gtres:  
        timedelta = 180 #3 minutes
        a,r,b = key
        print('double checking ',b)
        time = gtres[key]['timestamp']
        count =gtres[key]['count']
        mintime = time-timedelta
        maxtime = time+timedelta
        found = False
        for prefix in neighbor_dict:
            updatesList = neighbor_dict[prefix]    
            updatesList = sorted(neighbor_dict[prefix],key=lambda x: x[-1])
            for update in updatesList:
                update_type,as_path,origin_type,timestamp = update
                as_path = helpers.splitASPathFromString(as_path)
                #print(mintime,timestamp,maxtime, timestamp-mintime,maxtime-mintime)
                if timestamp - mintime >=timedelta and maxtime - time <=timedelta:
                #if mintime >= timestamp and maxtime <= timestamp:
                    neighbor = helpers.findNeighborASPath(as_path)
                    #print(neighbor)
                    if neighbor == b:
                        found=True 
                        break 
            if found:
                break
        if not found:  
            rem.append(key)
            print('could not validate ',key)  
            #exit(0) 
    print('need to rem ',rem) 
    print(prefResults['>'].keys())
    for r in rem:
        #del(prefResults['>'][r])
        prefResults['>'].pop(r)
        if r in prefResults['>'].keys():
            print('why is ',r,'still there?')
            exit(0)
    pickle.dump(prefResults, open(double_check,'wb'))
else:
    print('loading pref results')
    prefResults = []
    prefResults = pickle.load(open(double_check,'rb'))
print(prefResults['>'].keys())

#exit(0)
gtres = prefResults['>']
eqres = prefResults['=']
#store result of HPP(n2) = HPP(n1) and LPP(n2) > LPP(n1)
LPPRes = {}
for key in eqres:        
       # print(key,resdict[key])
        a,r,b = key
        time = eqres[key]['timestamp']
        count =eqres[key]['count']
        LPPRes[a,'>',b] = {'timestamp':time,'count':count}

def extract_details(resdict,both):
    print('extracting details')
    for key in resdict:
       # print(key,resdict[key])
        a,r,b = key
        time = resdict[key]['timestamp']
        count =resdict[key]['count']
        t = (a,r,b,time,count)
        both.append(t)
    return both

both = extract_details(gtres,[])
both = extract_details(eqres,both)
both =sorted(both,key=lambda x: (x[4],x[3]),reverse=True)
already_done = set()
startingHPP = []
#instead of doing this add one at a time and extend, if contra/cycle dont add!
starting_hpp_path = f'/mnt/research/pickles_2025/poster_test/starting_hpp{observer_ID}.pickle'
if not os.path.exists(starting_hpp_path):
    print("examining results! we have ",len(both),'to go through...')
    #progress = len(both) //10
    for i in range(len(both)):
        #if i % progress == 0 or i ==0:
        print("examining results ",i, 'of ',len(both),'hpp len: ',len(startingHPP))
        a,r,b,timestamp,count = both[i]
        t = (a,r,b)
        #if len(startingLPP)==0:
        
        startingHPP.append(t)
        

        haveCycles, cycles = helpers.detectCycles_ignore_eq(startingHPP,False)
        if haveCycles:
            print('removing due to cycle')
            startingHPP.remove(t)
            continue
        foundContras = helpers.detectContradictions(startingHPP)
        if foundContras:
            print('skipping contra')
            startingHPP.remove(t)
            continue
    #time.sleep(1)
    haveCycles, cycles = helpers.detectCycles_ignore_eq(startingHPP,False)
    if haveCycles:
        print('cycles detected what went wrong? ',cycles)
    foundContras = helpers.detectContradictions(startingHPP)
    if foundContras:
        print('found contras something went wrong')
    helpers.detectBadChange(startingHPP,'before dumping starting HPP')
    print('dumping starting HPP')
    pickle.dump(startingHPP,open(starting_hpp_path,'wb')) 
else:
    print('loading starting hpp...')
    startingHPP = []
    startingHPP = pickle.load(open(starting_hpp_path,'rb')) 
    helpers.detectBadChange(startingHPP,'after loading starting HPP')

if len(startingHPP) == 0:
    print("cannot perform test, not enough data on",observer_ID)
    exit(0)
#helpers.print_cycles(startingHPP)

helpers.detectBadChange(startingHPP,'creating starting lpp line 512')
toadd =[]
print('good to go from loading')

# for t in startingLPP:
#     a,r,b = t 
#     if r == '=':
#         toadd.append((b,r,a))
# for t in toadd:
#     startingLPP.append(t)
# for t in startingLPP:
#     print(t)

# def pres2(results):
#     #results = list(resdict.keys())
#     for i in range(len(results)):
#         result1 =results[i]
#         a1,r1,b1 = result1
#         print(result1)
#         for j in range(len(results)):
#             if i == j:
#                 continue
            
#             result2 = results[j]
#             a2,r2,b2 = result2 
#             if a1 == a2:
#                 print(result2)
#pres2(startingHPP)
#haveCycles, cycles = helpers.detectCycles_ignore_eq(startingHPP,False)
# if haveCycles:
#     print('cycles:',cycles)
#helpers.plotTuplesWithWeight(startingHPP,True,False)
graph_extension = f'/mnt/research/pickles_2025/poster_test/graph_extension_{observer_ID}.pickle'
#for _ in range(10):
#startingHPP = pickle.load(open(starting_hpp_path,'rb')) 
# all_neighbors = set() 
# for a,r,b in startingHPP:
#     all_neighbors.add(a)
#     all_neighbors.add(b)
# for n in all_neighbors:
#     for a,r,b in startingHPP:
#         if a == n:
#             print(a,r,b)
#         elif b==n:
#             print(b,r,a)

#have_contra, reason = helpers.detectBadChange_noexit(startingHPP,'starting hpp') 
helpers.detectBadChange(startingHPP,'starting hpp') 
    # if not have_contra:
    #     break
print('all good :) on load')  

madeCycle, cycles = helpers.detectCycles_ignore_eq(startingHPP)
if madeCycle:
    print('made a cycle =( ',cycles)
    exit(0)

if not os.path.exists(graph_extension):
    output = helpers.infer_inequalities(startingHPP)
    print("Inferred Inequalities and Equalities:")
    # for item in output:
    #     print(item)    

    helpers.detectBadChange(output,'extend infer inequalities')  

    print('all good :)')  
    madeCycle, cycles = helpers.detectCycles_ignore_eq(output)
    if madeCycle:
        print('made a cycle =( ',cycles)


        
    else:
        print('storing extended hpp')
        extendedHPP = startingHPP
        pickle.dump(extendedHPP,open(graph_extension,'wb'))
else:
    print('loading extended HPP')
    extendedHPP = []
    extendedHPP = pickle.load(open(graph_extension,'rb'))    

# if not os.path.exists(graph_extension):
#     haveNewResults = True
#     innercnt = 0
#     while haveNewResults:
#         print("extending with graphs, on run ",innercnt,'/max 10')
#         print("HPP length is now:",len(startingHPP))
#         helpers.expand_with_dict(startingHPP)
#         startingHPP, haveNewResults = graphHelpers.extendWithGraphs(startingHPP)
#         helpers.detectBadChange(startingHPP,'extend with graphs')
#         if innercnt > 10:
#             input('this seems to be taking a while...?')
#         innercnt+=1
#     pres2(startingHPP)  
#     pickle.dump(startingHPP,open(graph_extension,'wb'))
# else:
#     print('loading extended HPP')
#     startingHPP = pickle.load(open(graph_extension,'rb'))

  
#graphHelpers.extendWithGraphs(startingLPP)
#helpers.plotTuplesWithWeight(startingHPP,True,False)
starting_lpp_path = f'/mnt/research/pickles_2025/poster_test/starting_lpp_{observer_ID}.pickle'
if not os.path.exists(starting_lpp_path):
    startingLPP = []
    find_later = []
  
    for hppRes in extendedHPP:
        a2,r2,b2 = hppRes
        found = False
        if r2 !='=':
            continue 
        else:
            print('examining ',hppRes, 'for lpp counterpart')
        possibleKey1 = (a2,'>',b2)
        possibleKey2 = (b2,'>',a2)
        try:
            counterpart1 = LPPRes[possibleKey1]
        except KeyError:
            counterpart1 = None
        try:
            counterpart2 = LPPRes[possibleKey2]
        except KeyError:
            counterpart2 = None 
        if counterpart1 and counterpart2 == None:
            print('no LPP counterpart! for ',hppRes)
            startingLPP.append(possibleKey2)
            #t =(a2,'>',b2)
            #find_later.append(hppRes)
            continue
            #exit(0)
        if counterpart1 == None: 
            startingLPP.append(possibleKey2)
        if counterpart2 == None:
            startingLPP.append(possibleKey1)
        if counterpart1['count'] > counterpart2['count']:
            startingLPP.append(possibleKey1)
        elif counterpart1['count'] < counterpart2['count']:
            startingLPP.append(possibleKey2)
        else:
            if counterpart1['timestamp'] > counterpart2['timestamp']:
                startingLPP.append(possibleKey1)
            elif counterpart1['timestamp'] > counterpart2['timestamp']:
                startingLPP.append(possibleKey2)
            else:
                print('both are equal?',counterpart1,counterpart2,possibleKey1)
                startingLPP.append(possibleKey2)
                #<PROBABLE BUG> <FIXME>
                #exit(0)
    
        #remove duplicates just in case 
        torem = []
        for i in range (len(startingLPP)):
            for j in range (len(startingLPP)):
                if i==j: 
                    continue            
                res1 = startingLPP[i]
                res2 =startingLPP[j]
                if res1 == res2:
                    torem.append(res1)
        for r in torem:
            startingLPP.remove(r)
        print('removed duplicates',r)                    
        print(startingLPP)
        print(LPPRes.keys())
        #exit(0)                
        #startingLPP = helpers.infer_inequalities(startingLPP)
    print('dumping starting lpp ')
    pickle.dump(startingLPP,open(starting_lpp_path,'wb'))
else:
    print('loading starting lpp ')
    startingLPP = pickle.load(open(starting_lpp_path,'rb'))

def instantiate_observer(neighbor_dict):
    print("instantiating observer...")
    observer_dict = {}
    for prefix in neighbor_dict:
        updatesList = sorted(neighbor_dict[prefix],key=lambda x: x[-1])        
        for update in updatesList:
            print(update)
        update1 = updatesList[0]
        if len(updatesList) == 1:
            observer_dict[prefix] = update2
            continue
        
        update_type1,as_path1,origin_type1,timestamp1 = neighbor_dict[prefix][0]        
        update_type2,as_path2,origin_type2,timestamp2 = neighbor_dict[prefix][-1]
        
        if update1==update2:
            observer_dict[prefix] = update2
        else:
            if timestamp1 < timestamp2:
                observer_dict[prefix] = update2    
            elif timestamp1 > timestamp2:
                observer_dict[prefix] = update1
            else:
                print('same times?')
                print(update1)
                print(update2)
                exit(0)
            #break
        #print(neighbor_dict[prefix][0])
        #print(neighbor_dict[prefix][-1])
    return observer_dict


lppset = set(startingLPP)
startingLPP = list(lppset)
for lpp in startingLPP:
    print(lpp)
    #print(counterpart1)
    #print(counterpart2)
print('~~~~~~getting test updates~~~~~~~')
print('loading neighbor dict')
print(neighbor_dict_filepath,filepath)
with gzip.open(neighbor_dict_filepath,'rb') as f:
    neighbor_dict = pickle.load(f)
#neighbor_dict = pickle.load(open(neighbor_dict_filepath,'rb'))
observers = pickle.load(open('observers.pickle','rb'))

collector,observerASN,observerIP = observers[collector_type][observer_ID]    
import os 
def get_test_updates(observers,collector_type, observerID):
    test_updates_file = f'test_neighbor_updates_{collector_type}.pickle'
    if os.path.exists():
        return pickle.load(open(test_updates_file,'rb'))    
    broker = helpers.createBroker()
    collector,asn,ip = observers[collector_type][observer_ID]
    print(collector,asn,ip)
    items = helpers.queryBroker(broker,endTime,testEndTime,collector,'updates')
    params = helpers.addFiltersNotPrefix(peer_ip=ip,peer_asn=str(asn))

    test_neighbor_updates = {}
    for item in items:
        parser = helpers.parseFileWithParams(item,params)
        for elem in parser:
            elem['hijacker'] = 0
            prefix = elem['prefix']
            neighbor = helpers.findNeighborInUpdate(elem)
            if prefix not in test_neighbor_updates:
                 test_neighbor_updates[prefix] = []
            test_neighbor_updates[prefix].append(elem)
    #save for observer too! <TODO>
    print('dumping...')
    pickle.dump(test_neighbor_updates,open(test_updates_file,'wb'))
    return test_neighbor_updates
test_neighbor_updates = get_test_updates(observers,collector_type,observer_ID)
print(len(test_neighbor_updates))
#test_neighbor_updates = pickle.load(open('test_neighbor_updates.pickle','rb'))

#victims=['4800','6939','174','268746'] #random test victims
#victims=['54113','3582']
startingHPP = extendedHPP
victim_asn_ips = [('184.171.0.0/17','3582'), #Uoregon
                  ('141.193.213.0/24','209242'),# SOU
                  ('52.24.0.0/14','16509'),# OSU
                  ('129.123.0.0/16','26046'),# USU
                  ('151.101.128.0/22','54113') #Oxford
                  ]
all_known_neighbors = set()
for a,r,b in startingHPP:
    all_known_neighbors.add(a)
    all_known_neighbors.add(b)
victim_asns = []
victim_ips = []
for ip,asn in victim_asn_ips:
    victim_asns.append(asn)
    victim_ips.append(ip)
hijacking_updates_path = f'/mnt/research/pickles_2025/poster_test/hijacking_updates{observer_ID}.pickle'
if not os.path.exists(hijacking_updates_path):
    hijackers = get_hijackers(neighbor_dict,victim_asns,observerASN,all_known_neighbors) 
    if observers[collector_type][observer_ID][1] in hijackers:
        hijackers.remove(observers[collector_type][observer_ID][1])
    print(len(hijackers))
#exit(0)
    hijacking_updates = find_hijacker_updates(hijackers,neighbor_dict)
    observer_dict = {} #this... doesnt do anything?
    #observer_dict = instantiate_observer(neighbor_dict)
    pickle.dump((hijacking_updates,observer_dict),open(hijacking_updates_path,'wb'))
else:
    hijacking_updates,observer_dict = pickle.load(open(hijacking_updates_path,'rb'))

import playbook as Playbook

all_results = []
print('observer Asn is: ',observerASN)
#exit(0)
print(hijacking_updates[0])

non_default_hijackers = []
for h in hijacking_updates:   
    hijacker_asn = h['asn']
    if hijacker_asn in all_known_neighbors:
        non_default_hijackers.append(hijacker_asn)
    
for victim_ip in victim_ips:
    # victim_ip ="184.171.0.0/17" #uo 1
    # victim_ip ="23.185.0.0/24" #uo 2
    #sou 141.193.213.0/24, asn 209242
    #oregon state 52.24.0.0/14 16509
    #victim_ip = "69.24.118.0/24"#rando
    #USU: 129.123.0.0/16 26046
    #oxford 151.101.128.0/22 54113
    for h in hijacking_updates:
    
        hijacker_ip = list(h.keys())[0]
        fib_entry_for_p = helpers.get_fib_entry_for_p_new(endTime,victim_ip,collector,observerIP,observerASN)
        
        update_type,path,origin_type,timestamp = h[hijacker_ip]
        hijacker_asn = h['asn']
        #print('fib entry for p:',fib_entry_for_p)
        if fib_entry_for_p != None:
            fib_origin_asns = helpers.get_origin_asns_from_update(fib_entry_for_p)        
            if isinstance(fib_origin_asns,list):
                if hijacker_asn in fib_origin_asns:
                    print("you cant hijack yourself!")
                    continue
            elif hijacker_asn == fib_origin_asns:
                print("you cant hijack yourself!")
                continue
        #exit(0)
        hijacking_update = {'hijacker':1,'elem_type':'A','type':update_type,'as_path':path,
                    'origin':origin_type,'prefix':victim_ip,'timestamp':timestamp,'origin_asns':[hijacker_asn]}
        print(hijacking_update)
        if victim_ip not in test_neighbor_updates and fib_entry_for_p == None:
            print(fib_entry_for_p)
            print('new prefix, hij automatically wins')
            some_result = Playbook.store_auto_win(hijacker_asn,hijacking_update,victim_ip)
            if some_result != None:
                all_results.append(some_result)

            continue
        #print(path,type(path))
        hijacker_asn_path = helpers.splitASPathFromString(path)
        hijacker_neighbor = helpers.findNeighborASPath(hijacker_asn_path)
        
        if hijacker_neighbor not in non_default_hijackers:
            continue
        if victim_ip not in test_neighbor_updates:
            test_neighbor_updates[victim_ip] = []    
        
        #test_neighbor_updates[victim_ip].append(bad_update)
        
        #DOUBLE CHECK TIMESTAMP ORDERING <TODO>
        playbook = sorted(test_neighbor_updates[victim_ip],key=lambda x:x['timestamp'])
        #insert the FIB entry at index 0, its not hijacked yet ;)
        if fib_entry_for_p != None:
            playbook.insert(0,fib_entry_for_p)
        #launch hijackability here <TODO>
        result = Playbook.launch_playbook(playbook,startingHPP,startingLPP,hijacking_update)
        
        if result == None:
            print("could not find result for ",h)
        else:
            all_results.append(result)
        #print(result)
        #exit(0)
    #print(h)
#pickle.dump(all_results,open('simple_result.pickle','wb'))
pickle.dump(all_results,open(f'test{observer_ID}.pickle','wb'))
for result in all_results:
    print(result)

# for result in all_results:
#     #print(result)    
#     print(f"{result['hijacker_asn']},{result['first_reason_won']}")]