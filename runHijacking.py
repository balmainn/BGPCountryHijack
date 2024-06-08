import os
import gzip 
import pickle
import re 
import policies
#'pickles/ribData/{collectorID}-{startTime}-{endTime}.pickle
updatesFileDir = 'pickles/updateData/'
ribsFileDir = 'pickles/ribData/'

ribsPath = 'pickles/ribData/'
updatesPath = 'pickles/updateData/'

#dictionary with all collectors their peers
masterPeers = policies.getMasterPeers()

def asPathSplit(Dict):
    asPath = Dict.get('as_path', '')  # get the as_path or an empty string if not present
    
    if asPath:  # check if as_path is not empty
        if '{' in asPath: #handle multihome
            a = asPath.split(',')
            pathLen = a[0].replace('{','').replace('}','').split(' ')
            return pathLen
        else:
            return asPath.split(' ')  # split the as_path by spaces and add to the list
    else:
        print('AS PATH NONE?')
        print(asPath)
        return None
    
# This function is used to produce an array of strings from the victim and hij in order to give a 
# path length for comparison.

def calculatePath(Dict):
    # pathASes = []
    asPath = Dict.get('as_path', '')  # get the as_path or an empty string if not present
    
    if asPath:  # check if as_path is not empty
        if '{' in asPath: #handle multihome
            a = asPath.split(',')
            pathLen = len(a[0].replace('{','').replace('}','').split(' '))
            return pathLen
        else:
            return len(asPath.split(' '))  # split the as_path by spaces and add to the list
    else:
        return None#return len(pathASes) #returns the number of ASes in the path 

def isNeighborSame(victim,hij):
    #peer ASN is the last hop of the as_path
    # print(hij)
    vicNeigh = victim['peer_asn']
    hijNeigh = hij['peer_asn']
    # print("comparing ",victim['as_path'], "|",  hij['as_path'])
    if vicNeigh == hijNeigh:
        return True, vicNeigh,hijNeigh
    else:
        return False, vicNeigh,hijNeigh

def asPath(victim, hij):
    # print('applying policy')
    # # print('checking victim',victim)
    
    # print('hijacker:',hij)
    # policyChoice = random.randint(0, 100) 

    # if policyChoice <= 25:
        #This first policy selection is for shortest path. Returns True if the hijack is 
        #successful. This policy would mirror one which does not have any restrictions on 
        #import or export, and has no preferred paths selected 
    #success,vicOrigin,hijOrigin,sameSenderASN
    
    legitPath = calculatePath(victim)
    hijackPath = calculatePath(hij)
    if legitPath == None or hijackPath == None:
        exit(1) #TODO raise error and handle it 
    if legitPath > hijackPath:
        return True
    elif legitPath < hijackPath:
        return False
    else: # if the paths are the same lenght 50/50
        return 'E' #paths are equal, we dont know yet
    
        # coinFlip = random.randint(0, 100)
        # if coinFlip <= 50:
        #     return True
        # else:
        #     return False

def groupFiles(files):
    """groups multipart files together"""

    fileGroups = {}
    normalFiles = {}
    # file = files[0]
    # for file in files:
    # file = files[0]
    # collectorRE = ".*\.(.*?)-"
    
    # startTimeRE = "-2.*-2"
    bothTimesRE = "-2.*-m"
    allf = 1
    mfiles = 1
    for file in files:
        allf+=1
        if 'multipart' in file:
            mfiles+=1
            # print("~~~~",file,'~~~~')
            if 'rrc' in file:
                #RE to find RIPE collectors
                collectorRE = r"rrc\d*-"
            else: #RE to find routeViews collectors
                collectorRE = r"route-(.*?-)"

            m = re.search(collectorRE,file)


            # print(m)
            # print(m[0][:-1])
            collector = m[0][:-1]
            
            m = re.search(bothTimesRE,file)
            # print(m)
            # m =re.search('-2',file)
            span0 = m.span()[0]
            span1 = m.span()[1]
            bothTimes = file[span0+1:span1-2]
            # print(bothTimes)
            parts = bothTimes.split('-')
            # print(parts)
            startTime=parts[0]+'-'+parts[1]+'-'+parts[2]
            endTime=parts[3]+'-'+parts[4]+'-'+parts[5]
            # print(startTime)
            # print(endTime)
            
           
            if collector not in fileGroups.keys():
                fileGroups[collector] = {startTime:{endTime:[file]} }
                continue
                #{'startTime':{'endTime':{'files':[]}} }
            if startTime not in fileGroups[collector].keys():
                fileGroups[collector][startTime] = {endTime:[file]}
                continue    
            if endTime not in fileGroups[collector][startTime].keys():
                fileGroups[collector][startTime][endTime] = [file]
                continue                
                # else:
                #     fileGroups[collector][startTime][endTime]= [file]
            
            fileGroups[collector][startTime][endTime].append(file)
    # print(fileGroups)
    # print(allf)
    # print(mfiles)
    # print(allf+mfiles)
        else:
    #~~~~normal files are just sorted by collector 
            if 'rrc' in file:
                #RE to find RIPE collectors
                collectorRE = r"rrc\d*-"
            else: #RE to find routeViews collectors
                collectorRE = r"route-(.*?-)"
                
            m = re.search(collectorRE,file)
            # print(m)
            # print(m[0][:-1])
            collector = m[0][:-1]
            if collector not in normalFiles.keys():
                normalFiles[collector] = []
            normalFiles[collector].append(file)
        
    return(fileGroups,normalFiles)
    


def getFileGroupArray(fileGroups,collector,startTime,endTime):
    try:
        return fileGroups[collector][startTime][endTime]
    except KeyError as e:
        print('Key error in filegroups. cannot find ', e)
        return None

def findStartTimesForCollector(fileGroups,collector):
    try:
        return fileGroups[collector]
    except KeyError as e:
        print('Key error in filegroups. cannot find ', e)
        return None


def combineRibWithRibs(ribFileGroup,updatesFileGroup,collector):
    combos = []
    for startTimeRib in ribFileGroup[collector]:
        for endTimeRib in ribFileGroup[collector][startTimeRib]:
            ribFilesArray= getFileGroupArray(ribFileGroup,collector,startTimeRib,endTimeRib)
            
            for startTimeUpdate in updatesFileGroup[collector]:
                for endTimeUpdate in updatesFileGroup[collector][startTimeUpdate]:
                    updateFilesArray= getFileGroupArray(updatesFileGroup,collector,startTimeUpdate,endTimeUpdate)
                    for rib in ribFilesArray:
                        for update in updateFilesArray:
                            combos.append((rib,update))

    return combos


def storeResults(collector,results,tid,victimASN,hijackerASNS,shouldPrint=False):
    
    # exit(0)
    # print(results)
    filepath = f'pickles/results/tk-{collector}-tid{tid}-results-0'
    if len(results) ==0:
        return #dont store empty things
    if shouldPrint:
        print(f'tid {tid} storing {len(results)} results!')
        # print(f'tid {tid} storing results in!',filepath,len(results))
    #find the next available filepath
    if os.path.exists(filepath):
        dashLoc= filepath.rfind('-')
        fileNum = int(filepath[dashLoc+1:].strip()) +1
        filepath = f'pickles/results/tk-{collector}-tid{tid}-results-{fileNum}'
        
    #compress with gzip to save some space
    #NOTE: MUST use gzip to load this picklefile
    with gzip.open(filepath,'wb') as f:
        pickle.dump(results,f)
    # pickle.dump(results,open(filepath,'wb'))
    


# if legitPath > hijackPath:
#         return True
from datetime import datetime,timedelta
def timeDiffSkip(lastTime,update):
    lastdt = datetime.fromtimestamp(lastTime)
    currentdt = datetime.fromtimestamp(update['timestamp'])
    if currentdt > lastdt + timedelta(minutes=3): 
        # print(True)
        return True
    else:
        # print(False)
        return False
from random import uniform,randint
def randomPolicy(collector):
    numPeers = masterPeers[collector]['numPeers']
    vicLP = randint(0,numPeers) #victim
    hijLP = randint(0,numPeers) #hijacker
    if hijLP < vicLP:
        return False
    elif hijLP > vicLP: 
        return True
    else:
        return None

def doLocalPrefCalc(preferenceN):
    t = preferenceN*preferenceN
    bothRange = ((preferenceN*preferenceN -preferenceN ) / 2)
    i = uniform(0,1) #off by 1 figure this out 
    # print(bothRange,i)
    leRange = bothRange/t
    gtRange = leRange+leRange
    #eqRange = preferenceN/t #implied by the else
    # print(leRange,gtRange,eqRange, i)
    if i <= leRange:
        # print('less')
        return False #victim had higher local pref 
    elif i > leRange and i <= gtRange:
        return True #hijacker had higher local pref
    else:
        return 'E' #we dont know
        # print('equal')
        eq+=1
def compareLocalPreference(sameSenderASN,collector):
    #TODO DONE"""need to consider preference 3, 5, random, and uniform random"""
    
    #if the same ASN sent both updates theres no reason to do any of the below
    #since they have the same LP
    if sameSenderASN:
        policyResults = {3:None,5:None,12:None,
                        20:None,50:None,'random':None}
        return policyResults
    
    policy3Result = doLocalPrefCalc(3)
    policy5Result = doLocalPrefCalc(5)
    policy12Result = doLocalPrefCalc(12)
    policy20Result = doLocalPrefCalc(20)
    policy50Result = doLocalPrefCalc(50)
    randomPolicyResult = randomPolicy(collector)
    policyResults = {3:policy3Result,5:policy5Result,12:policy12Result,
                     20:policy20Result,50:policy50Result,'random':randomPolicyResult}
    return policyResults


def originType(vicUpdate,hijUpdate):
    #preferred in this order: IGP- EGP- Incomplete
    originPrefTable = {'IGP':3,'EGP':2,'INCOMPLETE':1}
    
    vicTypeVal = originPrefTable[vicUpdate['origin']]
    hijTypeVal = originPrefTable[hijUpdate['origin']]
    if vicTypeVal < hijTypeVal:
        return True
    elif vicTypeVal > hijTypeVal:
        return False
    else:
        return 'E' #we dont know
def testForUnknown(hijacker,victim):
    if hijacker == '6461' and victim == '20055':
        return False, hijacker,victim
    if hijacker == '20055' and victim == '6461':
        return True,hijacker,victim
    
    return None, None,None
        
def singleLocalPrefTest(update,ribUpdate):
    #manual encoding of this
    #20055 > 7922 > 2044 > 6939
    #20055 > 6461 #handled in unknown test
    prefVals = {20055:10,7922:8,2044:6,6939:4}
  
    updatePath = asPathSplit(update)
    ribPath = asPathSplit(ribUpdate)
   
    if len(updatePath) == 1 or len (ribPath) == 1:#early gtfo if we have 2 that are the same
        return {"hijacker_neighbor":updatePath[0],"victim_neighbor":ribNeighbor[0],'result':'E'} 
    updateNeighbor = int(updatePath[1])
    ribNeighbor = int(ribPath[1])
    #print('type of neighbor', type(updateNeighbor))
    unknownTest,unkHij,unkVic = testForUnknown(updateNeighbor,ribNeighbor)
    #print('after test unknown')
    if unknownTest != None:
        return {"hijacker_neighbor":unkHij,"victim_neighbor":unkVic,'result':unknownTest}
    if ribNeighbor not in prefVals.keys() or updateNeighbor not in prefVals.keys():
        return None
    updateVal = prefVals[updateNeighbor]
    ribVal = prefVals[ribNeighbor]
    if updateVal > ribVal:
        return {"hijacker_neighbor":ribNeighbor,"victim_neighbor":updateNeighbor,'result':True} 
    if updateVal < ribVal:
        return {"hijacker_neighbor":ribNeighbor,"victim_neighbor":updateNeighbor,'result':False} 
    else:
        return {"hijacker_neighbor":ribNeighbor,"victim_neighbor":updateNeighbor,'result':'E'} 
    

def doTheThingGandalf(update,ribUpdate,ribASN,updateASN,collector):
    #print('DO THE THING GANDALF1!')
    #apply things in this order
    # Local preference (highest, local AS)
    # Locally originated (no idea, so we skip)
    # AS Path (shortest)
    # Origin type ( i < e < ?) preferred in this order: IGP- EGP- Incomplete 
    #^how i heard about a number from the update 
    sameSenderASN, victimSender,hijackSender = isNeighborSame(ribUpdate,update)    
    #localPrefResults = compareLocalPreference(sameSenderASN,collector)
    #print('DO THE THING GANDALF0.5555!')
    localPrefResults = singleLocalPrefTest(update,ribUpdate)
    if localPrefResults == None:
        return None     
    #print('DO THE THING GANDALF2!')
    #ultimateReason='localPref'
    
    asPathSuccess = asPath(victim=update,hij=ribUpdate)
    # ultimateReason='asPath'
    #print('DO THE THING GANDALF3!')
    originTypeSuccess = originType(ribUpdate,update)
    #print('DO THE THING GANDALF4!')
    #if all of the following are true, we have no idea.
    if sameSenderASN and asPathSuccess == "E" and originTypeSuccess == "E":
        determined = False 
    else:
        determined = True
        
    #store the results
    vicOrigin = ribUpdate['origin']
    hijOrigin = update['origin']
    vicASN = ribASN
    hijASN = updateASN
    successDict ={'localPref': localPrefResults, 'asPath':asPathSuccess,'originType':originTypeSuccess,'determined':determined}
    storeDict = {'victimASN':vicASN, 'hijASN':hijASN,
            'success':successDict,'vicOrigin':vicOrigin, #technically we dont care about origin, but we'll leave it 
            'hijOrigin':hijOrigin,'sameSenderASN':sameSenderASN,
            'vicSender':victimSender, 'hijackSender': hijackSender }
    # print('storedict ',storeDict)
    return storeDict
def gogomagicfunctionTheSequal(ribEnd,updateEnd,tid):
    MAXNUM = 10000
    ribCollector = getCollector(ribEnd)
    updateCollector = getCollector(updateEnd)
    if ribCollector!=updateCollector:
        #scream a big error but dont actually exit.
        print('COLLECTORS DONT MATCH')
        print('COLLECTORS DONT MATCH')
        print('COLLECTORS DONT MATCH')
        print('COLLECTORS DONT MATCH')
        print('COLLECTORS DONT MATCH')
        return
    print("LOADING RIB")
    with gzip.open(ribsPath+ribEnd,'rb') as f:
        ribUpdates = pickle.load(f)
    print("LOADING UPDATE")
    updates=pickle.load(open(updatesPath+updateEnd,'rb'))
    results = []
    ribMonitorASN =6423 #manually limited for this test #peer asn
    count = 1
    print(ribUpdates.keys())
    for ribPeerIP in ribUpdates[ribMonitorASN]:
        count +=1
        victimASNS= set()
        count2 = 1
        print(f'tid {tid} is working on rib peer ip {count}/{len(ribUpdates[ribMonitorASN].keys())}')
        for ribASN in ribUpdates[ribMonitorASN][ribPeerIP]:
            print(f'tid {tid} is working on rib ASN {count2}/{len(ribUpdates[ribMonitorASN][ribPeerIP].keys())}')
            count2+=1
            victimASNS.add(ribASN)
            if MAXNUM != None:
                if count2 >=MAXNUM:
                    break
            for ribUpdate in ribUpdates[ribMonitorASN][ribPeerIP][ribASN]:
                                                        
                results,hijackerASNS = sendRibsToMagic(ribMonitorASN,ribUpdate,ribCollector,updates,ribASN)
                
                
                #MEM BE FREE!
    #<---pushed too far will crash when storeResults is there
        if len(hijackerASNS) == 0:
            hijackerASNS = 'unknown'
        #print('STORING RESUTLS (but not really)')
        #pickle.dump(results ,open('supersecretpickles.pickle','wb'))
        # print(results)
        storeResults(ribCollector,results,tid,victimASN=victimASNS,hijackerASNS=hijackerASNS, shouldPrint=True)
        # print("~~~~normal store mem be free! ~~~")
        results = []
    #percentages                                
                # print('hij wins!',hijWins,"percent", hijWins/(hijWins+partials+vicWins)*100)
                # print('partials?',partials, "percent",partials/(hijWins+partials+vicWins)*100)
                # print('origPath',vicWins,"percent",vicWins/(hijWins+partials+vicWins)*100)
            
                                    
    # print('hij wins!',hijWins)
    # print('partials?',partials)
    # print('origPath',vicWins)
    
    #memory be FREE!
    updates = ""
    ribUpdates = ""
    for _ in range(3):
        print("~~~~~~~~~DONE~~~~~~~~~")
def sendRibsToMagic(ribPeerAsn,ribUpdate,ribCollector,updates,ribASN):
    results = []
    victimASNs = set()
    # print(updates)
    # for ip in updates:
    #     for peer_asn in updates[ip]:
    #         print(ip,peer_asn)#,updates[ip][peer_asn])
    
    # print(ribPeerAsn,ribUpdate,ribCollector,ribASN,updates[ribPeerAsn])
    # exit(0)
    #print("ribs to magic ",ribPeerAsn,type(ribPeerAsn))
    try:
        for updatePeerIP in updates[ribPeerAsn]:
            #print('update peer ip' , updatePeerIP)
            for updateASN in updates[ribPeerAsn][updatePeerIP]:
                #print(updateASN)
                if updateASN != ribASN:#dont check things that are the same
                
                    victimASNs.add(updateASN)
                    for update in updates[ribPeerAsn][updatePeerIP][updateASN]:
                        #print('update is large')
                        result = doTheThingGandalf(update,ribUpdate,ribPeerAsn,updateASN,ribCollector)
                        if result != None:
                            #print('result: ',result)
                            results.append(result)
                                    
        
    except Exception as e:
        #print(results)
        print("exception in magic Ribs ", e.with_traceback())
        exit(0)
        pass
    return results, victimASNs


def getCollector(file):
    if 'rrc' in file:
        #RE to find RIPE collectors
        collectorRE = r"rrc\d*-"
    else: #RE to find routeViews collectors
        collectorRE = r"route-(.*?-)"
    m = re.search(collectorRE,file)
    # print(file,m)
    collector = m[0][:-1]
    return collector
#~~~~~MAIN~~~~~~#

#get all preparsed Ribs and Updates 
updateFiles = os.listdir(updatesFileDir)
ribFiles = os.listdir(ribsFileDir)

numProcesses = 8
combos = []
i = 0

resultsFiles =os.listdir('pickles/results/')
collectorsSoFar = set()
badFiles = []
cnt = 0

allCollectors ={}
#pick N files 
N = 20
collectorCounts = {}
for ribFile in ribFiles:
    ribCollector = getCollector(ribFile)
    if 'nwax' not in ribCollector: #filter the collector to nwax 
        continue
    # if ribCollector in collectorsSoFar:
    #     continue
    for updateFile in updateFiles:
        updateCollector = getCollector(updateFile)
        if 'nwax' not in updateCollector: #hack, only do this collector 
            continue
        
        # if updateCollector in collectorsSoFar:
        #     continue
        if ribCollector == updateCollector:
            combos.append((ribFile,updateFile, i))
            i+=1
            

c = combos

# print(c,len(c))
for c in combos:
    print(c)
print(len(combos))
#gogomagicfunctionTheSequal(combos[1][0],combos[1][1],combos[1][2]) #test a single thing before yolo multiprocessing
#GO GO GADGET MAGIC FUNCTION DO THE THING GANDALF!
print("GO GO GADGET DO THE THING")
print("this is going to take a while...")
from multiprocessing import Pool
pool = Pool(processes=numProcesses)
pool.starmap(gogomagicfunctionTheSequal,combos)
pool.close()

print("DONE! run processResultsFromHijacking.py now")

