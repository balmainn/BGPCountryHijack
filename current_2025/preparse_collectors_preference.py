import os  
import gzip 
import pickle 
import helpers 
import networkx
observers = pickle.load(open('observers.pickle','rb'))
startTime = '2025-03-26T00:00:00' 
#startTime = '2025-03-30T00:00:00' 
endTime = '2025-03-31T00:00:00'    
testEndTime = '2025-04-01T00:00:00'
test_data = []
# print(observers['rv'][0])
# exit(0)
for collector_type in observers:
    for id in range(len(observers[collector_type])):
        if collector_type == 'rv':
            collector,asn,ip = observers[collector_type][id]
            asn = int(float(asn))
        else:
            collector,asn,ip = observers[collector_type][id]
        d = (collector_type,collector,asn,ip)
        test_data.append(d)
to_rem = []
for d in test_data:
    collector_type,collector,asn,ip = d
    if collector_type =='rv':
        filepath = f'/mnt/research/pickles_2025/main_test/{collector}-{asn}-{ip}.pickle'
        
    if collector_type == 'ripe':
        filepath = f'/mnt/research/pickles_2025/all_ripe/{collector}-{asn}-{ip}.pickle'
    if not os.path.exists(filepath):
        print(collector_type,collector,asn,ip,'does not exist.')
        to_rem.append(d)
print(len(test_data))
for r in to_rem:
    test_data.remove(r)
print(len(test_data))
#exit(0)        
def pre_parse_pref_results(collector_type,collector,asn,ip):

    if collector_type =='rv':
        filepath = f'/mnt/research/pickles_2025/main_test/{collector}-{asn}-{ip}.pickle'
        
    if collector_type == 'ripe':
        filepath = f'/mnt/research/pickles_2025/all_ripe/{collector}-{asn}-{ip}.pickle'
    
    
    double_check = f'/mnt/research/pickles_2025/double_check/{collector}-{asn}-{ip}.pickle'
    #filepath = f'/mnt/research/pickles_2025/poster_test/{collector}-{asn}-{ip}-5day.pickle'
    if not os.path.exists(double_check):  
        
        print('loading...')
        with gzip.open(filepath,'rb') as f:
            neighbor_dict = pickle.load(f)
        if neighbor_dict == {'this is ipv6'}:
            print(collector,asn,'cannot be done on an ipv6 addr rn.')
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
                    with open('errors.txt','a') as f:
                        erline = collector_type + ' '+ collector + ' '+str(asn) + ' '+ip+ '\n'
                        f.write(erline)
                    return
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
        print('double checking results')
        for key in gtres:  
            timedelta = 180 #3 minutes
            a,r,b = key
            #print('double checking ',b)
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
                return
                exit(0)
        print('dumping')
        pickle.dump(prefResults, open(double_check,'wb'))
        #manual clean memory management ;)
        neighbor_dict = {}
        return
    else:
        print('already exists!')
        return
        print('loading pref results')
        # prefResults = []
        # prefResults = pickle.load(open(double_check,'rb'))



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
def pre_parse_pref_results2(collector_type, collector,asn,ip):
    #exit(`0)
    double_check = f'/mnt/research/pickles_2025/double_check/{collector}-{asn}-{ip}.pickle'
    if not os.path.exists(double_check):
        print(double_check,'does not exist!')
        return
    prefResults = pickle.load(open(double_check,'rb'))
    gtres = prefResults['>']
    eqres = prefResults['=']
    #store result of HPP(n2) = HPP(n1) and LPP(n2) > LPP(n1)
    
    both = extract_details(gtres,[])
    both = extract_details(eqres,both)
    both =sorted(both,key=lambda x: (x[4],x[3]),reverse=True)
    # if len(both) > 1500:
    #     print('will do this later')
    #     return
    already_done = set()
    startingHPP = []
    #instead of doing this add one at a time and extend, if contra/cycle dont add!
    
    starting_hpp_path = f'/mnt/research/pickles_2025/main_test/starting_hpp/{collector}-{asn}-{ip}.pickle'
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
        print('dumping starting HPP',collector,asn,ip)
        pickle.dump(startingHPP,open(starting_hpp_path,'wb')) 
        return
    else:
        print('loading starting hpp...')
        startingHPP = []
        return
        #startingHPP = pickle.load(open(starting_hpp_path,'rb')) 
        #helpers.detdectBadChange(startingHPP,'after loading starting HPP')


def expand_hpp(collector_type,collector,asn,ip):
    starting_hpp_path = f'/mnt/research/pickles_2025/main_test/starting_hpp/{collector}-{asn}-{ip}.pickle'
    if not os.path.exists(starting_hpp_path):
        print('does not exist')
        return
    print('loading starting hpp...')
    startingHPP = []
    for _ in range(100):
        startingHPP = pickle.load(open(starting_hpp_path,'rb')) 
        
        badchange, reason =helpers.detectBadChange_noexit(startingHPP,'after loading starting HPP')
        if not badchange:
            break
    if len(startingHPP) == 0:
        print("cannot perform test, not enough data on",collector,asn,ip)
        exit(0)
    #helpers.print_cycles(startingHPP)

    # badchange, reason =helpers.detectBadChange_noexit(startingHPP,'creating starting lpp line 512')
    # if badchange:
    #     return
    toadd =[]
    print('good to go from loading')

    #have_contra, reason = helpers.detectBadChange_noexit(startingHPP,'starting hpp') 
    #badchange, reason =helpers.detectBadChange_noexit(startingHPP,'starting hpp') 
    if badchange:
        return
        # if not have_contra:
        #     break
    print('all good :) on load')  

    madeCycle, cycles = helpers.detectCycles_ignore_eq(startingHPP)
    if madeCycle:
        print('made a cycle =( ',cycles)
        return
    graph_extension = f'/mnt/research/pickles_2025/main_test/extended/{collector}-{asn}-{ip}.pickle'
    
    if not os.path.exists(graph_extension):
        output = helpers.infer_inequalities(startingHPP)
        print("Inferred Inequalities and Equalities:")
        # for item in output:
        #     print(item)    

        badchange, reason =helpers.detectBadChange_noexit(output,'extend infer inequalities')
        if badchange:
            return
        print('all good :)')  
        madeCycle, cycles = helpers.detectCycles_ignore_eq(output)
        if madeCycle:
            print('made a cycle =( ',cycles)
            return

        else:
            print('storing extended hpp')
            extendedHPP = startingHPP
            pickle.dump(extendedHPP,open(graph_extension,'wb'))
            return
    else:
        print('loading extended HPP')
        extendedHPP = []
        return
        #extendedHPP = pickle.load(open(graph_extension,'rb'))    

def parse_and_extend(collector_type, collector,asn,ip):
    #exit(`0)
    double_check = f'/mnt/research/pickles_2025/double_check/{collector}-{asn}-{ip}.pickle'
    if not os.path.exists(double_check):
        print(double_check,'does not exist!')
        return
    prefResults = pickle.load(open(double_check,'rb'))
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
    both = extract_details(gtres,[])
    both = extract_details(eqres,both)
    both =sorted(both,key=lambda x: (x[4],x[3]),reverse=True)
    # if len(both) > 2500:
    #     print('will do this later')
    #     return
    already_done = set()
    startingHPP = []
    #instead of doing this add one at a time and extend, if contra/cycle dont add!
    
    starting_hpp_path = f'/mnt/research/pickles_2025/main_test/starting_hpp/{collector}-{asn}-{ip}.pickle'
    graph_extension = f'/mnt/research/pickles_2025/main_test/extended/{collector}-{asn}-{ip}.pickle'

    if not os.path.exists(graph_extension):
    #if not os.path.exists(starting_hpp_path):
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
        print('dumping starting HPP',collector,asn,ip)
        pickle.dump(startingHPP,open(starting_hpp_path,'wb')) 
        #return
    # else:
    #     print('loading starting hpp...')
    #     startingHPP = []
    #     return
        #startingHPP = pickle.load(open(starting_hpp_path,'rb')) 
        #helpers.detdectBadChange(startingHPP,'after loading starting HPP')



    starting_hpp_path = f'/mnt/research/pickles_2025/main_test/starting_hpp/{collector}-{asn}-{ip}.pickle'
    if not os.path.exists(starting_hpp_path):
        print('does not exist')
        return
    print('loading starting hpp...')
    #startingHPP = []
    #startingHPP = pickle.load(open(starting_hpp_path,'rb')) 
    badchange, reason =helpers.detectBadChange_noexit(startingHPP,'after loading starting HPP')
    if badchange:
        return
    if len(startingHPP) == 0:
        print("cannot perform test, not enough data on",collector,asn,ip)
        exit(0)
    #helpers.print_cycles(startingHPP)

    badchange, reason =helpers.detectBadChange_noexit(startingHPP,'creating starting lpp line 512')
    if badchange:
        return
    toadd =[]
    print('good to go from loading')

    #have_contra, reason = helpers.detectBadChange_noexit(startingHPP,'starting hpp') 
    badchange, reason =helpers.detectBadChange_noexit(startingHPP,'starting hpp') 
    if badchange:
        return
        # if not have_contra:
        #     break
    print('all good :) on load')  

    madeCycle, cycles = helpers.detectCycles_ignore_eq(startingHPP)
    if madeCycle:
        print('made a cycle =( ',cycles)
        return
    graph_extension = f'/mnt/research/pickles_2025/main_test/extended/{collector}-{asn}-{ip}.pickle'

    if not os.path.exists(graph_extension):
        output = helpers.infer_inequalities(startingHPP)
        print("Inferred Inequalities and Equalities:")
        # for item in output:
        #     print(item)    

        badchange, reason =helpers.detectBadChange_noexit(output,'extend infer inequalities')
        if badchange:
            return
        print('all good :)')  
        madeCycle, cycles = helpers.detectCycles_ignore_eq(output)
        if madeCycle:
            print('made a cycle =( ',cycles)
            return

        else:
            print('storing extended hpp')
            extendedHPP = startingHPP
            pickle.dump(extendedHPP,open(graph_extension,'wb'))
            return
    else:
        print('loading extended HPP')
        extendedHPP = []
        return
        #extendedHPP = pickle.load(open(graph_extension,'rb'))    

def parse_lpp(collector_type, collector,asn,ip):
    graph_extension = f'/mnt/research/pickles_2025/main_test/extended/{collector}-{asn}-{ip}.pickle'
    starting_lpp_path = f'/mnt/research/pickles_2025/main_test/starting_lpp/{collector}-{asn}-{ip}.pickle'
    double_check = f'/mnt/research/pickles_2025/double_check/{collector}-{asn}-{ip}.pickle'
    if os.path.exists(starting_lpp_path):
        return
    if not os.path.exists(double_check) or not os.path.exists(graph_extension):
        print('cant do, one dont exist')
        return
    prefResults = pickle.load(open(double_check,'rb'))
    gtres = prefResults['>']
    eqres = prefResults['=']
    LPPRes = {}
    for key in eqres:        
        # print(key,resdict[key])
            a,r,b = key
            time = eqres[key]['timestamp']
            count =eqres[key]['count']
            LPPRes[a,'>',b] = {'timestamp':time,'count':count}
    extendedHPP = pickle.load(open(graph_extension,'rb'))    
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
            if counterpart1 == None and counterpart2 == None:
                print('no LPP counterpart! for ',hppRes)
                startingLPP.append(possibleKey2)
                return
                #t =(a2,'>',b2)
                #find_later.append(hppRes)
                continue
                #exit(0)
            if counterpart1 == None: 
                startingLPP.append(possibleKey2)
            elif counterpart2 == None:
                startingLPP.append(possibleKey1)
            elif counterpart1['count'] > counterpart2['count']:
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
                    #if both a>b and b>a with the same probability, then they're equally likely
                    # return
                    # exit(0)
        
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
        return
    else:
        print('loading starting lpp ')
        #startingLPP = pickle.load(open(starting_lpp_path,'rb'))
        return

def get_starting_lpp(collector,asn,ip):
    starting_lpp_path = f'/mnt/research/pickles_2025/main_test/starting_lpp/{collector}-{asn}-{ip}.pickle'
    starting_lpp = pickle.load(open(starting_lpp_path,'rb'))
    return starting_lpp
def get_test_updates(collector_type, collector,asn,ip):
    test_updates_file = f'/mnt/research/pickles_2025/main_test/test_neighbor_updates/{collector}-{asn}-{ip}.pickle'
    if os.path.exists(test_updates_file):
        print('already have test updates for ',collector,asn,ip)
        return #pickle.load(open(test_updates_file,'rb'))    
    broker = helpers.createBroker()
    
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
def get_test_updates_from_file(collector_type, collector,asn,ip):
    test_updates_file = f'/mnt/research/pickles_2025/main_test/test_neighbor_updates/{collector}-{asn}-{ip}.pickle'
    test_neighbor_updates = pickle.load(open(test_updates_file,'rb'))
    return test_neighbor_updates


#pool.starmap(pre_parse_pref_results,test_data)
#pool.close() 
#the big ones are still left, but lets see which ones get done
# pool.starmap(pre_parse_pref_results2,test_data)
# pool.close() 
#ct,c,a,i = test_data[0]
#expand_hpp(ct,c,a,i)
#parse_and_extend(ct,c,a,i)
# pool.starmap(expand_hpp,test_data)
# pool.join()
# pool.close() 
#'route-views.gixa' 30997 196.201.2.1
# pool.starmap(parse_and_extend,test_data)
# pool.join()
# pool.close() 

# pool.starmap(parse_lpp,test_data)
# pool.close() 
# pool.join()

def get_info_from_file(filename:str):
    parts = filename.split('-')
    ip = parts[-1].replace('.pickle','')
    if parts[0] =='route':
        collector_type = 'rv'
        collector = parts[0]+'-'+parts[1]
        asn = parts[2]
    else:
        collector_type = 'ripe'
        collector = parts[0]
        asn = parts[1]
    return (collector_type,collector,asn,ip)
files = os.listdir('/mnt/research/pickles_2025/main_test/starting_lpp')
restricted_data = []
for file in files:
    info = get_info_from_file(file)
    restricted_data.append(info)
#uncomment later asdf <todo> <rethere>    
# for info in restricted_data:
#     collector_type,collector,asn,ip = info 
#     get_test_updates(collector_type,collector,asn,ip)
def make_dgraph_from_rib(rib_updates):
    dgraph = networkx.Graph()
    asns = set('root')
    dgraph.add_node('root')
    numprefs = 10

def make_dgraph(neighbor_dict,graphType):
    if graphType == 'd':
        dgraph = networkx.DiGraph()
    elif graphType =='n':
        dgraph = networkx.Graph()
    asns = set('root')
    dgraph.add_node('root')
    numprefs = 10
    paths = set()
    for prefix in neighbor_dict:
        #numprefs-=1
        # if numprefs <=0:
        #     break
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
            paths = set()
            #dgraph.add_edge('root',as_path1[0])
            paths.add(('root',as_path1[0]))
            as_path = list(set(as_path1))
            for i in range(len(as_path)):
                if i+1 >= len(as_path):
                    break
                
                a = as_path[i]
                b = as_path[i+1]
                paths.add((a,b))
            dgraph.add_edges_from(paths)
    return dgraph

def find_root(dgraph:networkx.DiGraph):
    root = list(dgraph['root'].keys())[0]
    print('found root:',root)

    return root
    #print()

def create_hijacking_updates(hijackers,neighbor_dict):
    #OBSERVER <TODO> build this from that ew
    dgraph = make_dgraph(neighbor_dict,'n')    
    root = find_root(dgraph)
    created_updates = []
    for h in hijackers:
        update_type = 'A'
        prefix='fill_me_in'
        # if not networkx.has_path(dgraph,root,h):
        #     continue
        try:
            path = networkx.shortest_path(dgraph,root,h)
        except:
            fake_update = {'fill_me_in':f'hijacker {h} does not have path to {root}'}
            created_updates.append(fake_update)
            continue
        pathstr = ""
        for asn in path:
            pathstr = pathstr +' '+asn
        origin_type='IGP'
        timestamp = helpers.convertTimeToUnix(endTime)
        fake_update = {'fill_me_in':(update_type,pathstr[1:],origin_type,timestamp),'asn':h}
        created_updates.append(fake_update)
    #print(created_updates)
    return created_updates
from random import shuffle
def find_hijacker_updates(hijackers,hijackers_cc,collector_type,collector,asn,ip):
    if collector_type =='rv':
        filepath = f'/mnt/research/pickles_2025/main_test/{collector}-{asn}-{ip}.pickle'
        
    if collector_type == 'ripe':
        filepath = f'/mnt/research/pickles_2025/all_ripe/{collector}-{asn}-{ip}.pickle'
    if not os.path.exists(filepath):
        print('cant do does not exist')
        return
    hijacking_updates_path = f'/mnt/research/pickles_2025/main_test/hijacking_updates/{hijackers_cc}-{collector}-{asn}-{ip}.pickle'
    if os.path.exists(hijacking_updates_path):
        #print('already did')
        return
    with gzip.open(filepath,'rb') as f:
        neighbor_dict = pickle.load(f)
    
    prefixes = list(neighbor_dict.keys())
    hijacking_updates = []
    create = []
    for h in hijackers:
        print('trying to find update for hijacker',h, 'for' ,collector,asn,ip)
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
    
    pickle.dump(hijacking_updates,open(hijacking_updates_path,'wb'))
    return
    #return(hijacking_updates)

# pool.starmap(get_test_updates,restricted_data)
# pool.close() 
# pool.join()
cdir = 'country_information.pickle'
countryinfo = pickle.load(open(cdir,'rb'))
hijackers_cc = 'rs'
hijackers = countryinfo[hijackers_cc]['asn']
new_data = []

victim_prefixes = []
victim_prefixes = countryinfo['ua']['ipv4']
#victim_prefixes.extend(countryinfo['ua']['ipv6'])
victim_test_data = []
#<TODO this thing>
from random import sample,choice
if not os.path.exists('uk_sample.pickle'):
    sampled_prefixes = sample(victim_prefixes,100)
    to_rem = [] 
    to_add = []
    for prefix in sampled_prefixes:
        if '-' in prefix:
            choose = choice(set(victim_prefixes) - set(sampled_prefixes))
            to_add.append(choose)
            to_rem.append(prefix)
    for r in to_rem:
        sampled_prefixes.remove(r)
    for a in to_add:
        sampled_prefixes.append(a)
    print(len(sampled_prefixes))
    for p in sampled_prefixes:
        print(p)
    #exit(0)
    pickle.dump(sampled_prefixes,open('uk_sample.pickle','wb'))
else:
    sampled_prefixes = pickle.load(open('uk_sample.pickle','rb'))

collectors = set()
cnt=0
for data in restricted_data:
    collector_type,collector,asn2,ip2 = data 
    #collectors.add(ip2)
    #for fib entries
    for victim_prefix in sampled_prefixes:
        path = '/mnt/research/pickles_2025'+f'/fib_entry_for_p/{victim_prefix.replace('/','-')}{collector}{ip2}{endTime}.pickle'
        #print(path)
        if not os.path.exists(path):
            cnt +=1
        if victim_prefix == '31.128.68.0-31.128.95.255':
            victim_prefix = '31.128.68.0/19'
        #print(victim_prefix)
        if '-' in victim_prefix:
            continue
        # if int(victim_prefix.split('/')[1]) < 24:
        #     continue
        victim_test_data.append((endTime,victim_prefix,collector,ip2,asn2)) 
print(len(victim_test_data))
print(len(restricted_data))
print(len(victim_prefixes))
print(len(sampled_prefixes))
print('there are ',cnt,'remaining')
#exit(0)
# pool.starmap(helpers.get_fib_entry_for_p_new,victim_test_data)
# pool.close()
# pool.join()
# exit(0)
#helpers.get_fib_entry_for_p_new(endTime,victim_prefix,collector,ip2,asn2)
#if something bugs it'll probably be this file 
#https://archive.routeviews.org/route-views7/bgpdata/2025.03/RIBS/rib.20250331.0000.bz2        

# endTime,victim_ip,collector,observerIP,observerASN = victim_test_data[-1]
# print(endTime,victim_ip,collector,observerIP,observerASN)
# helpers.get_fib_entry_for_p_new(endTime,victim_ip,collector,observerIP,observerASN)
#                                 #someTime,prefixP,collector,observerIP,observerASN

#exit(0)
for data in restricted_data:
    collector_type,collector,asn,ip = data 
    #new_data.append((hijackers,hijackers_cc,collector_type,collector,asn,ip))
    find_hijacker_updates(hijackers,hijackers_cc,collector_type,collector,asn,ip)
#exit(0)
def get_hijacker_updates(hijackers_cc,collector,asn,ip):
    hijacking_updates_path = f'/mnt/research/pickles_2025/main_test/hijacking_updates/{hijackers_cc}-{collector}-{asn}-{ip}.pickle'
    hijacking_updates = pickle.load(open(hijacking_updates_path,'rb'))
    return hijacking_updates

def get_starting_hpp(collector,asn,ip):
    graph_extension = f'/mnt/research/pickles_2025/main_test/extended/{collector}-{asn}-{ip}.pickle'
    extendedHPP = pickle.load(open(graph_extension,'rb'))
    return extendedHPP
victim_prefixes = sampled_prefixes
def get_hijacker_and_observer_asn_from_no_path(hijacker_no_res):
    #result matches this format
    #{'fill_me_in': 'hijacker 51629 does not have path to 48297'}
    #print(hijacker_no_res)
    no_string = hijacker_no_res['fill_me_in']
    parts = no_string.split()
    hijacker_asn = parts[1]
    observer_asn = parts[-1]
    return hijacker_asn,observer_asn

import playbook as Playbook
def launch_hijack_test(hijackers_cc,collector_type,collector,observerASN,observerIP,victim_ips):
    if os.path.exists(f'/mnt/research/pickles_2025/main_test/rs_ukrain_test/{hijackers_cc}-{collector}-{observerASN}-{observerIP}.pickle'):
        print('already exists')
        return
    startingHPP = get_starting_hpp(collector,observerASN,observerIP)
    startingLPP = get_starting_lpp(collector,observerASN,observerIP)
    all_known_neighbors = set()
    for a,r,b in startingHPP:
        all_known_neighbors.add(a)
        all_known_neighbors.add(b)
    #container for win/loss results
    all_results = []
    #container for results we dont know about for some reason
    unknown_results = []
    print('observer Asn is: ',observerASN)
    #exit(0)
    hijacking_updates = get_hijacker_updates(hijackers_cc,collector,observerASN,observerIP)
    
    print(hijacking_updates[0])

    non_default_hijackers = set()
    a =  []
    to_rem = []
    for h in hijacking_updates:  
        if list(h.keys())[0] =='fill_me_in':            
            continue
        #print(h,h.keys()) 
        hijacker_asn = h['asn']
        if hijacker_asn in all_known_neighbors:
            non_default_hijackers.add(hijacker_asn)
    #print(all_results)
    print(non_default_hijackers)
    #exit(0)
    test_neighbor_updates = get_test_updates_from_file(collector_type,collector,observerASN,observerIP)    
    numprefs = 2
    vpctr = 0
    for victim_prefix in victim_ips:
        vpctr +=1 
        if vpctr %10 ==0:
            print(f'on {vpctr}/{len(victim_ips)}')
        # print(numprefs,len(hijacking_updates))
        # numprefs-=1
        # if numprefs <=0:
        #     break
        fib_entry_for_p = helpers.get_fib_entry_for_p_new(endTime,victim_prefix,collector,observerIP,observerASN)
        observer_has_path = does_observer_have_path_to_P(collector_type,collector, observerASN, observerIP,fib_entry_for_p,test_neighbor_updates,victim_prefix)
        
        for h in hijacking_updates: 
            

            some_result = None
            prefixP = victim_prefix        
            #current path 
            
            #dont count "self hijackers" i.e. the benign origin. they can do what they want. its their prefix after all. 
            if fib_entry_for_p != None: 
                fib_origin_asns = helpers.get_origin_asns_from_update(fib_entry_for_p)        
                if isinstance(fib_origin_asns,list):
                    if hijacker_asn in fib_origin_asns:
                        print("you cant hijack yourself!")
                        continue
                elif hijacker_asn == fib_origin_asns:
                    print("you cant hijack yourself!")
                    continue
            hijacker_has_path = does_hijacker_have_path_to_O(h)
            #print('does hijacker has path: ',hijacker_has_path)
            
            #print('does observer has path: ',observer_has_path)
            #auto win / auto loss section 
            #there is no path to P, so we cant test this.
            #print(h,'1')
            if not observer_has_path and not hijacker_has_path:
                hijacker_asn,observer_asn = get_hijacker_and_observer_asn_from_no_path(h)
                why = 'no path observer and no path hijacker'
                some_result = Playbook.store_auto_unknown(hijacker_asn,observerASN,observerIP,victim_prefix,why,hijacker_update=None)
                unknown_results.append(some_result)
                continue
            #observer has a path but hijacker does not, hijacker loses  
            #print(h,'2')          
            if observer_has_path and not hijacker_has_path:
                hijacker_asn,observer_asn = get_hijacker_and_observer_asn_from_no_path(h)
                some_result = Playbook.store_auto_loss(hijacker_asn,victim_prefix)
                all_results.append(some_result)
                continue

            #create a fake hijacking update to test against           
            #at this point we know hijacker has a path
            hijacker_benign_ip = list(h.keys())[0]
            hijacker_update_type,hijacker_path,hijacker_origin_type,hijacker_timestamp = h[hijacker_benign_ip]
            hijacker_asn = h['asn']
            hijacker_asn_path = helpers.splitASPathFromString(hijacker_path)
            hijacker_neighbor = helpers.findNeighborASPath(hijacker_asn_path)
            hijacking_update = {'hijacker':1,'elem_type':'A','type':hijacker_update_type,'as_path':hijacker_path,
                        'origin':hijacker_origin_type,'prefix':victim_prefix,'timestamp':hijacker_timestamp,'origin_asns':[hijacker_asn]}
            #print(hijacking_update)
            #we got an update through a neighbor we dont know about
            #so we cant test
            if hijacker_neighbor in non_default_hijackers:
                why = f'hijacking from unknown neighbor, {hijacker_neighbor}'
                some_result = Playbook.store_auto_unknown(hijacker_asn,observerASN,observerIP,victim_prefix,why,hijacker_update=hijacking_update)
                unknown_results.append(some_result)
                continue
            #observer does not have a path but hijacker does, hijacker wins            
            if not observer_has_path and hijacker_has_path:
                
                some_result = Playbook.store_auto_win(hijacker_asn,hijacking_update,victim_prefix)
                all_results.append(some_result)
                continue
            
            
            #implies we did not hear an update about this prefix during "testing"
            if victim_prefix not in test_neighbor_updates:
                test_neighbor_updates[victim_prefix] = []
            #implicit both have a path (H->O and O->P)
            #sort benign updates by time into a "playbook"
            playbook = sorted(test_neighbor_updates[victim_prefix],key=lambda x:x['timestamp'])
            #if the 0th update we heard is the fib entry, dont add it again
            if fib_entry_for_p != None:
                if len(playbook) > 0:
                    if playbook[0] != fib_entry_for_p:
                        playbook.insert(0,fib_entry_for_p)
                #if the playbook is empty, add the fib entry
                else:
                    playbook.insert(0,fib_entry_for_p)
            #print(h,h.keys()) 
            #somehow we reached this with the playbook being empty
            #this implies no updates were see
            if len(playbook)==0:
                some_result = Playbook.store_auto_win(hijacker_asn,hijacking_update,victim_prefix)
                all_results.append(some_result)
                continue
            
            #launch hijackability here <TODO>
            result,errors = Playbook.launch_playbook(playbook,startingHPP,startingLPP,hijacking_update)
            
            # if result == None:
            #     print("could not find result for ",h)
            #     why = f'testing {error}'
                
            #     continue
                
            # else:
            for error in errors:
                why=error
                some_result = Playbook.store_auto_unknown(hijacker_asn,observerASN,observerIP,victim_prefix,why,hijacker_update=hijacking_update)
                unknown_results.append(some_result)
            all_results.append(result)
            #print(result)
            #exit(0)
        #print(h)
    #pickle.dump(all_results,open('simple_result.pickle','wb'))
    print('this is where we store updates.')
    print('found ',len(all_results), 'results')
    print('found ',len(unknown_results),'unknowns')
    num_hpp = 0
    # for u in unknown_results:
    #     print('hijacker:',u['hijacker_asn'],'prefix',u['prefix_hijacked'],'why')
    #     why = u['why']
    #     print('\t',why)
    #     if 'HPP' in why:
    #         num_hpp +=1
    #print(num_hpp,'unknowns', len(unknown_results), num_hpp/len(unknown_results))
    #print(len(unknown_results)/len(all_results), '% percentage of unknown' )
    with open ('stats.txt','a') as f:
        f.write(f"{collector} {observer_asn} {observerIP}\n")
        if len(all_results) != 0:
            line = '\t'+str(len(unknown_results))+'/'+str(len(all_results))+'='+str(len(unknown_results)/len(all_results)) + '% percentage of unknown\n'
        else:
            line = '\t'+str(len(unknown_results))+'/'+str(len(all_results))+'\n'
        f.write(line)
             
    # for result in all_results:
    #     print(result)
    # print("not storing")
    # exit(0)
    
    pickle.dump(all_results,open(f'/mnt/research/pickles_2025/main_test/rs_ukrain_test/{hijackers_cc}-{collector}-{observerASN}-{observerIP}.pickle','wb'))
    pickle.dump(unknown_results,open(f'/mnt/research/pickles_2025/main_test/rs_ukrain_test/unknown_{hijackers_cc}-{collector}-{observerASN}-{observerIP}.pickle','wb'))
    # for result in all_results:
    #     print(result)
def does_observer_have_path_to_P(collector_type,collector, observer_asn, observer_ip,fib_entry_for_P,test_neighbor_updates,prefixP):
    """finds if the observer has a path to the prefix P
    if the observer does not have a path, then they are very likely to lose."""
    #print('does observer have an update about P?')
    if fib_entry_for_P != None:
        return True 
    #test_neighbor_updates[prefix].append(elem)
    if prefixP in set(test_neighbor_updates.keys()):
        return True
    #last resort, check updates we heard
    if collector_type =='rv':
        filepath = f'/mnt/research/pickles_2025/main_test/{collector}-{observer_asn}-{observer_ip}.pickle'
        
    if collector_type == 'ripe':
        filepath = f'/mnt/research/pickles_2025/all_ripe/{collector}-{observer_asn}-{observer_ip}.pickle'
    with gzip.open(filepath,'rb') as f:
        neighbor_dict = pickle.load(f)
    keyset = set(neighbor_dict.keys())
    if prefixP in keyset:
        #manual memory management 
        neighbor_dict = {}
        return True
    neighbor_dict = {}
    #print('nope')
    return False
    exit(0)
    updates_past #neighbor_dict
    updates_now #fib_entry
    updates_future #test_neighbor_updates -> playbook
    pass


def does_hijacker_have_path_to_O(h):
    """finds if the hijacker has a path to the observer
    if the hijacker does not have a path to the observer, then they can't win."""
    #hijacking_updates = get_hijacker_updates(hijackers_cc,collector,#observerASN,observerIP)
    #rs route-views7 48297 193.148.248.220    
    
    #ip to hijack,                                                    time                hijacker's asn
    #{'194.106.176.0/20': ('A', '48297 200132 49127 8400 6700', 'IGP', 1743028015.365965), 'asn': '6700'}
    #print('does hijacker have a path to O?')
    # for ip_to_hijack in hijacking_updates:
    if list(h.keys())[0] =='fill_me_in':
        value = h['fill_me_in']
        if isinstance(value,tuple):
          #  print('yes')
            return True
        #print('no')
        return False
    else:    
       # print('yes')
        return True
# victim_prefixes = []
# victim_prefixes = countryinfo['ua']['ipv4']
# #victim_prefixes.extend(countryinfo['ua']['ipv6'])
victim_test_data = []
#<TODO this thing>


for data in restricted_data:
    collector_type,collector,asn,ip = data 
    #for fib entries
    if '-' in ip:
        print(ip)
    victim_test_data.append((hijackers_cc,collector_type,collector,asn,ip,victim_prefixes))
    # launch_hijack_test(hijackers_cc,collector_type,collector,asn,ip,victim_prefixes)
    # continue
    # for victim_prefix in sampled_prefixes:
    #     if '-' in victim_prefix:
    #         print('i thought we fixed this')
    #         print(victim_prefix)
        #victim_test_data.append((endTime,victim_prefix,collector,asn,ip))
#exit(0)        
        #launch_hijack_test(hijackers_cc,collector_type,collector,asn,ip,victim_prefixes)
        #exit(0)
from multiprocessing import Pool 
numprocs = 3
pool = Pool(processes=numprocs)
pool.starmap(launch_hijack_test,victim_test_data)
pool.close()
pool.join()
#endTime,victim_ip,collector,observerIP,observerASN = victim_test_data[0]
#print(endTime,victim_ip,collector,observerIP,observerASN)
#helpers.get_fib_entry_for_p_new(endTime,victim_ip,collector,observerIP,observerASN)
    #for launch hijack attacks 
    #victim_test_data.append((hijackers_cc,collector_type,collector,asn,ip,victim_prefixes))

#(hijackers_cc,collector_type,collector,observerASN,observerIP,victim_ips)
