import helpers
def is_hijacker(update):
    if update['hijacker']:
        return True 
    else:
        return False
def opposite_relation(relation):
    if relation == '>':
        return '<'
    if relation == '<':
        return '>'
    if relation == '=':
        return '='
def createFullPrefList(inequalities):
    """from a list of inequalities  create a dictionary of all values
    example:[(a>b), (c=d)] -> 
        {a: {>: b}, 
        b: {<: a}, 
        c:{=:d},
        d:{=:c} }
    input: inequalities, a list of tuples, each tuple element is a string e.g. ('a','>','b')
    output: see above"""
    #print('create full pref list')
    allPrefs = set()
    for a,r,b in inequalities:
        res = (a,r,b)
        if res not in allPrefs:
            allPrefs.add(res)
        if r == '>':
            allPrefs.add((b,'<',a))
        if r =='=':
            allPrefs.add((b,'=',a))
    someDict = {}
    for pref in list(allPrefs):
        a,relation,b = pref
        if a not in someDict.keys():
            someDict[a] = {'>':[],'<':[],'=':[]}
        if b not in someDict.keys():
            someDict[b] = {'>':[],'<':[],'=':[]}
        # if relation not in someDict[a].keys():
        #     someDict[a][relation] = [] 
        if b not in someDict[a][relation]:
            someDict[a][relation].append(b)
        o = opposite_relation(relation)
        if a not in someDict[b][o]:
            someDict[b][o].append(a)
    print(someDict)
    allNeighbors = set()
    for pref in list(allPrefs):
        a,_,b = pref
        allNeighbors.add(a)
        allNeighbors.add(b)
    return someDict
    for neighbor in list(allNeighbors):
        secondSet = set()
        secondSet.add(neighbor)
        for op in someDict[neighbor]:
            for b in someDict[neighbor][op]:
                secondSet.add(b)
        if secondSet!= allNeighbors:
            #if this doesnt pass, there is a missing neighbor
            print("sets not eq")
            print(neighbor)
            print(secondSet)
            print(allNeighbors)
            print(allNeighbors-secondSet)
            exit(0)
    return someDict
def findRelation(someDict,a,b):
    """finds the relationship between a and b, e.g. >, =, or <"""
    try:
        for op in someDict[a]:
            if b in someDict[a][op]:
                return op
    except KeyError:
        return None
    
def should_continue_path_selection(success):
    """if two values are the same, bgp best path selection should continue
    this function represents this so we dont have to type it in many times
    input: success 
        success = True, False, or None
    returns: 
        True when success = None, 
        False when success = True or False"""
    if success == None:
        return True
    if success:
        return False
    if not success:
        return False
def test_HPP(hijacker_update,benign_update,hpp_dict):
    assert(hijacker_update['hijacker'] ==1)
    hijacking_neighbor = helpers.findNeighborInUpdate(hijacker_update)
    benign_neighbor = helpers.findNeighborInUpdate(benign_update)
    if str(benign_neighbor) not in hpp_dict.keys():
            print('unknown neighbor we have no results for')
            #exit(0)
            return 'error', f'could not find HPP relation for {hijacking_neighbor},{benign_neighbor}'
            #return 'unknown_neighbor',None
    if hijacking_neighbor == benign_neighbor:
        return None,None
    relation = findRelation(hpp_dict,hijacking_neighbor,benign_neighbor)
    if relation == None:
        
        print("~~~~~~~~")
        print('could not find relation for ',hijacking_neighbor,benign_neighbor)
        #print(hpp_dict)
        print("~~~~~~~~")
        return 'error', f'could not find HPP relation for {hijacking_neighbor},{benign_neighbor}'
    if relation == '>':
        return True,None
    if relation == '<':
        return False,None
    if relation == '=':
        return None,None
    
def test_AS_Path(hijacker_update,benign_update):
    assert(hijacker_update['hijacker'] ==1)
    hijacker_path_len = len(helpers.splitASPathFromUpdate(hijacker_update))
    update_path_len = (len(helpers.splitASPathFromUpdate(benign_update)))
    #|H| > |u| -> u should NOT be adopted
    if hijacker_path_len > update_path_len:
        return False
    #|H| = |u| -> we dont know if u should be adopted
    if hijacker_path_len == update_path_len:
        return None
    #|H| < |u| -> u should be adopted
    if hijacker_path_len < update_path_len:
        return True
    
def test_Origin_Type(hijacker_update,benign_update):
    """checks the origin type returns 
    true if update should be adopted
    false if update should not be adopted 
    none if we dont know at this step.
    NOTE: BGP prefers LOWER origin types     
    """
    
    print(hijacker_update)
    print(benign_update)
    assert(hijacker_update['hijacker'] ==1)
    origin_types_dict = {'IGP':0, 'EGP':1, 'INCOMPLETE':2}
    hijacker_origin = hijacker_update['origin']
    update_origin = benign_update['origin']
    if origin_types_dict[hijacker_origin] < origin_types_dict[update_origin]:
        return True        
    if origin_types_dict[hijacker_origin] == origin_types_dict[update_origin]:
        return None        
    if origin_types_dict[hijacker_origin] > origin_types_dict[update_origin]:
        return False     
    
def test_LPP(hijacker_update,benign_update,lpp_dict):
    assert(hijacker_update['hijacker'] ==1)
    hijacking_neighbor = helpers.findNeighborInUpdate(hijacker_update)
    benign_neighbor = helpers.findNeighborInUpdate(benign_update)
    if hijacking_neighbor == benign_neighbor:
        return None,f'inconclusive LPP from same neighbor {hijacking_neighbor},{benign_neighbor} '
    relation = findRelation(lpp_dict,hijacking_neighbor,benign_neighbor)
    if relation == None:
        return 'error',f'could not find LPP relation {hijacking_neighbor},{benign_neighbor}'
    if relation == '>':
        return True, None
    if relation == '<':
        return False, None
    if relation == '=':
        return None, f'lpp is the same? {hijacking_neighbor},{benign_neighbor}'
def check_time(hijacker_update,benign_update):
    t1 = hijacker_update['timestamp']
    t2 = benign_update['timestamp']
    if t1 < t2:
        return True 
    elif t1 > t2:
        return False
    else:
        return None

def test_origin_hijacking(hijacker_update,benign_update,hpp_dict,lpp_dict):
    success,error_reason = test_HPP(hijacker_update,benign_update,hpp_dict)
    reason = 'HPP'
    if success == 'unknown_error':
        print('found error')
        #exit(0)
        return False, 'unknown_neighbor'
    if success == 'error':
        return None, error_reason
    if success != None:
        if success:
            return True, reason
        else:
            return False, reason
    success = test_AS_Path(hijacker_update,benign_update)
    reason = 'AS_Path'
    if success != None:
        if success:
            return True, reason
        else:
            return False, reason
    success = test_Origin_Type(hijacker_update,benign_update)
    reason = 'Origin_Type' 
    if success != None:
        if success:
            return True, reason
        else:
            return False, reason
    success, error_reason = test_LPP(hijacker_update,benign_update,lpp_dict)
    reason = 'LPP'
    if success == 'error':
        return None, error_reason
        
    if success != None:
        if success:
            return True, reason
        else:
            return False, reason
    #we should never reach here
    success = check_time(hijacker_update,benign_update)
    reason = 'time'
    if success != None:
        if success:
            return True, reason
        else:
            return False, reason
    print("no result?")
    print(hijacker_update)
    print(benign_update)
    return None,'testing inconclusive. all things equal. hijacker probably loses or the updates are the same'
    exit(0)
def store_auto_unknown(hijacker_asn,observer_asn,observer_ip,prefixP,why,hijacker_update=None):
    playbook_results = {'hijacker_asn': hijacker_asn,
        'hijacker_update':hijacker_update,#None,#hijacker_update,
        'prefix_hijacked':prefixP,
        'observer_asn': observer_asn,
        'observer_ip': observer_ip,
        'why':why
        }
    return playbook_results
def store_auto_loss(hijacker_asn,prefix):
    playbook_results = {'hijacker_asn': hijacker_asn,
        'hijacker_update':None,#None,#hijacker_update,
        'prefix_hijacked':prefix,
        'num_benign_updates' : 0,
        'hijacker_path_len':0,
        'origin_results_won':{'HPP':[],'AS_Path':[],'Origin_Type':[],'LPP':[],'time':[],'default':[],'unknown_neighbor':[]},
        'origin_results_lost':{'HPP':[],'AS_Path':[],'Origin_Type':[],'LPP':[],'time':[],'default':[(1,[])],'unknown_neighbor':[]}
        }
    return playbook_results
def store_auto_win(hijacker_asn,hijacking_update,prefix):
    playbook_results = {'hijacker_asn': hijacker_asn,
        'hijacker_update':hijacking_update,#None,#hijacker_update,
        'prefix_hijacked':prefix,
        'num_benign_updates' : 0,
        'hijacker_path_len':len(helpers.splitASPathFromUpdate(hijacking_update)),
        'origin_results_won':{'HPP':[],'AS_Path':[],'Origin_Type':[],'LPP':[],'time':[],'default':[(1,[])],'unknown_neighbor':[]},
        'origin_results_lost':{'HPP':[],'AS_Path':[],'Origin_Type':[],'LPP':[],'time':[],'default':[],'unknown_neighbor':[]}
        }
    return playbook_results
def launch_playbook(playbook:list,HPP,LPP,hijacking_update):
    
    #print("launching playbook")
    # for p in playbook:
    #     print(p)
    # print(len(playbook),type(playbook),type(p))
    # exit(0)
    hpp_dict = helpers.infer_inequalities(HPP,1)
    lpp_dict = helpers.infer_inequalities(LPP,1)
    #hpp_dict = createFullPrefList(HPP)
    #lpp_dict = createFullPrefList(LPP)    
    #{'hpp_count':0,'as_path_count':0,'origin_type_count':0,'lpp_count':0}
    
    playbook_results = {'hijacker_asn': helpers.get_origin_asns_from_update(hijacking_update),
        'hijacker_update':hijacking_update,#None,#hijacker_update,
        'hijacker_path_len':len(helpers.splitASPathFromUpdate(hijacking_update)),
        'prefix_hijacked':hijacking_update['prefix'],
        'num_benign_updates' : len(playbook),
        'origin_results_won':{'HPP':[],'AS_Path':[],'Origin_Type':[],'LPP':[],'time':[],'default':[],'unknown_neighbor':[]},
        'origin_results_lost':{'HPP':[],'AS_Path':[],'Origin_Type':[],'LPP':[],'time':[],'default':[],'unknown_neighbor':[]}
        }     
    try:        
        if 'hijacker' not in playbook[0].keys():
            playbook[0]['hijacker']=0
    except:
        print(playbook)
        print(playbook[0])
        print(playbook[-1])
        exit(0)
    errors = []
    for benign_update in playbook:

        #print("test hijacking!")
        victim_as_path_len = len(helpers.splitASPathFromUpdate(benign_update))
        
        success,reason, = test_origin_hijacking(hijacking_update,benign_update,hpp_dict,lpp_dict)
        if success == None:
            errors.append(reason)
            continue
            #return None,reason
        if success:
            playbook_results['origin_results_won'][reason].append((1,victim_as_path_len))
        else:
            playbook_results['origin_results_lost'][reason].append((1,victim_as_path_len))

    return playbook_results,errors