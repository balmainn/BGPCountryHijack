import pickle
import gzip 
# results = pickle.load(open('supersecretpickles.pickle','rb'))
# for r in results:
#     print(r)
import os
#files = os.listdir('pickles/results/')

with gzip.open('pickles/results/route-views.nwax-tid14-results-0','rb') as f:
    res = pickle.load(f)

def findResult(res):
    if res == None or res == "E":
        return None
    elif res == True:
        return True
    elif res == False:
        return False
    else:
        print("UKNOWN VALUE IN FIND RESULT WTF")
        exit(0)

def parseSuccesses(keyValue,dictResults,result):
    
    # print('parsing successes')
    # print(keyValue)
    # print(dictResults)
    # print(result)
    # result[keyValue]
    # dictResults['policy'][keyValue]
    res = result['result']
    # print(dictResults)
    if res == None or res == "E":
        dictResults['policy']['hijackerTies']+=1
        return None
    elif res == True:
        dictResults['policy']['hijackerWins']+=1
        return True
    elif res == False:
        dictResults['policy']['hijackerLosses']+=1
        return False
    else:
        print("UKNOWN VALUE IN STORE SINGLE RESULT WTF")
        exit(0)
def storeSingleResult(keyValue,dictResults,result):
    #pull value out of result
    #{'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}, 
    # print('storing single result')
    # print(keyValue)
    # print(dictResults)
    # print(result)
    # print('key',keyValue,'dictrestuls',dictResults)
    res = result[keyValue]
    if res == None or res == "E":
        dictResults[keyValue]['hijackerTies']+=1
        return None
    elif res == True:
        dictResults[keyValue]['hijackerWins']+=1
        return True
    elif res == False:
        dictResults[keyValue]['hijackerLosses']+=1
        return False
    else:
        print("UKNOWN VALUE IN STORE SINGLE RESULT WTF")
        exit(0)

def initiailzeDict(mainKey,innerKey):
    normalized ={}
    normalized[mainKey] = {
                innerKey:{
                    'policy' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'asPath' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}
                    }
                }
    return normalized
def dictReady(storeDict,asn1,asn2):
        #storeDict ={}
    try:
        dictHijacker = storeDict[asn1]
    except:
        storeDict[asn1] = {
                    asn2:{
                    'policy' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'asPath' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}
                    }
                }
        #dictHijacker = storeDict[asn1]
    try:
        dictResults = storeDict[asn1][asn2]
    except:
        storeDict[asn1][asn2] = {
                    'policy' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'asPath' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}
                    }
        #dictResults = dictHijacker[asn2]

    return dictResults
    
def filterProcessResults(storeDict,asn1,asn2):    
    # print(result)
    # print(result.keys())
    peer = 6423
    victimASN = result['victimASN']
    hijackerASN = result['hijASN']
    success = result['success']
    # print(success.keys())
    victimOrigin = result['vicOrigin']
    hijackerOrigin = result['hijOrigin']
    sameSenderASN = result['sameSenderASN']
    localPreferenceResult = success['localPref']['result']
    asPathResult = success['asPath']
    originResult = success['originType']
    #storeDict = dictReady(storeDict,asn1,asn2)
    #storeDict ={}
    try:
        dictHijacker = storeDict[asn1]
    except:
        storeDict[asn1] = {
                    asn2:{
                    'policy' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'asPath' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}
                    }
                }
        #dictHijacker = storeDict[asn1]
    try:
        dictResults = storeDict[asn1][asn2]
    except:
        storeDict[asn1][asn2] = {
                    'policy' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'asPath' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}
                    }
        #dictResults = dictHijacker[asn2]
        
    location = storeDict[asn1][asn2]
    #print(result)
    #just add the results to allresults TODO
    res = parseSuccesses('policy',location,success['localPref'])
    if res != None:
        return
    res = storeSingleResult('asPath',location,success)
    if res != None:
        return
    res = storeSingleResult('originType',location,success)
    if res != None:
        return
    return storeDict

def processResult(storeDict,result,asn1,asn2):
    # print(result)
    # print(result.keys())
    peer = 6423
    victimASN = result['victimASN']
    hijackerASN = result['hijASN']
    success = result['success']
    # print(success.keys())
    victimOrigin = result['vicOrigin']
    hijackerOrigin = result['hijOrigin']
    sameSenderASN = result['sameSenderASN']
    localPreferenceResult = success['localPref']['result']
    asPathResult = success['asPath']
    originResult = success['originType']
    storeDict = dictReady(storeDict,asn1,asn2)
        
    location = storeDict[asn1][asn2]
    #print(result)
    #just add the results to allresults TODO
    parseSuccesses('policy',location,success['localPref'])
    storeSingleResult('asPath',location,success)
    storeSingleResult('originType',location,success)
    return storeDict
allVictimResults = {}
allHijackerResults = {}
normalizedVictimResults = {}
print(normalizedVictimResults)
normalizedHijackerResults = {}
ct = 0
# for result in res:
#     print(result)
    
#     victimASN = result['victimASN']
#     hijackerASN = result['hijASN']
    
#     filterProcessResults(normalizedVictimResults,victimASN,hijackerASN,hijASN)
#     filterProcessResults(normalizedHijackerResults,hijackerASN,victimASN)
#     processResult(allVictimResults,result,victimASN,hijackerASN)
#     processResult(allHijackerResults,result,hijackerASN,victimASN)

def doNeighborThings(storeDict,asn1,asn2):
    try:
        dictHijacker = storeDict[asn1]
    except:
        storeDict[asn1] = {
                    asn2:{
                    'thisHijackersSuccess' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    }
                }
        #dictHijacker = storeDict[asn1]
    try:
        dictResults = storeDict[asn1][asn2]
    except:
        storeDict[asn1][asn2] = {
                    'thisHijackersSuccess' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                    }
        #dictResults = dictHijacker[asn2]
        
    location = storeDict[asn1][asn2]
    success = result['success']
    # print(success.keys())
    victimOrigin = result['vicOrigin']
    hijackerOrigin = result['hijOrigin']
    sameSenderASN = result['sameSenderASN']
    localPreferenceResult = success['localPref']['result']
    asPathResult = success['asPath']
    originResult = success['originType']
    
    #res = parseSuccesses('thisHijackersSuccess',location,success['localPref'])
    res = localPreferenceResult
    # print(dictResults)
    if res == None or res == "E":
        location['thisHijackersSuccess']['hijackerTies']+=1
        #return None
    elif res == True:
        location['thisHijackersSuccess']['hijackerWins']+=1
       # return True
    elif res == False:
        location['thisHijackersSuccess']['hijackerLosses']+=1
       # return False
    else:
        print("UKNOWN VALUE IN STORE SINGLE RESULT WTF")
        #exit(0)

vicNeighborDict = {}
hijNeighborDict = {}
for result in res:    
    victimNeighbor = result['success']['localPref']['victim_neighbor']
    hijackerNeighbor = result['success']['localPref']['hijacker_neighbor']
    victimASN = result['victimASN']
    hijackerASN = result['hijASN']
    doNeighborThings(vicNeighborDict,victimNeighbor,hijackerNeighbor)
    doNeighborThings(hijNeighborDict,hijackerNeighbor,victimNeighbor)
print(vicNeighborDict)
print("~~~~~~~")
print(hijNeighborDict)
    # if ct > 10:
    #     break
print("~~~~~~~")
# print(len(normalizedHijackerResults))
# print(len(normalizedVictimResults))
# print(len(allVictimResults))
# print(len(allHijackerResults))
# pickle.dump(normalizedHijackerResults,open('pickles/results/normalizedHijackerResults.pickle','wb'))
# pickle.dump(normalizedVictimResults,open('pickles/results/normalizedVictimResults.pickle','wb'))
# pickle.dump(allVictimResults,open('pickles/results/allVictimResults.pickle','wb'))
# pickle.dump(allHijackerResults,open('pickles/results/allHijackerResults.pickle','wb'))
# # for v in normalizedVictimResults:
#     for h in normalizedVictimResults[v]:
#         print(h, normalizedVictimResults[v][h]['asPath'])
# print(normalizedVictimResults)
    #processResult(allHijackerResults,hijackerASN,victimASN)
    
        

# print(result)
# print(len(res))
