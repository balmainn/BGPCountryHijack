import os
import gzip 
import pickle
import re 
#'pickles/ribData/{collectorID}-{startTime}-{endTime}.pickle
updatesFileDir = 'pickles/updateData/'
ribsFileDir = 'pickles/ribData/'

ribsPath = 'pickles/ribData/'
updatesPath = 'pickles/updateData/'

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

def applyPolicy(victim, hij):
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
        return "Equal"
    
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


def storeResults(collector,results,tid,victimASN,shouldPrint=False):
    if len(results) ==0:
        return #dont store empty things
    if shouldPrint:
        print(f'tid {tid} storing results!',len(results))
    # exit(0)
    # print(results)
    filepath = f'pickles/results/{collector}-{victimASN}-tid{tid}-results-0'
    #find the next available filepath
    if os.path.exists(filepath):
        dashLoc= filepath.rfind('-')
        fileNum = int(filepath[dashLoc+1:].strip()) +1
        filepath = f'pickles/results/{collector}-{victimASN}-tid{tid}-results-{fileNum}'
        
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
    
def doTheThingGandalf(update,ribUpdate,ribASN,updateASN):
                                    
    storeDict = {}
    success = applyPolicy(ribUpdate,update)
    # if success == 'Equal':
    #     partials+=1
    # elif success:
    #     hijWins+=1
    # else:
    #     vicWins +=1
    vicOrigin = ribUpdate['origin']
    hijOrigin = update['origin']
    sameSenderASN, victimSender,hijackSender = isNeighborSame(ribUpdate,update)
    vicASN = ribASN
    hijASN = updateASN
    if success == True:
        success = 1
    if success == False:
        success = 0
    if success == 'Equal':
        success = 'E' #reduce the amount of stored data 
    
    storeDict = {'victimASN':vicASN, 'hijASN':hijASN,
            'success':success,'vicOrigin':vicOrigin,
            'hijOrigin':hijOrigin,'sameSenderASN':sameSenderASN,
            'vicSender':victimSender, 'hijackSender': hijackSender }
    return storeDict

def gogogadgetmagicfunction2(ribEnd,updateEnd,tid):
    #number of hijacker ASNs to consider 
    num_hijacker_asns_to_consider_updates = 20
    #number of victim ASNs to consider 
    num_victim_asns_to_consider_ribs = 20
    #number of victim updates to consider
    num_victim_updates_to_consider = 20
    #number of hijacking updates to compare against the rib (victim) (will do at most this many)
    number_hijack_updates_to_consider_at_most = 5 
    
    print(f"tid {tid} is working on {ribEnd}\n \
                  and {updateEnd}")

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
    ribTestCount = 2 
    updateTestCount = 2
    print("LOADING RIB")
    with gzip.open(ribsPath+ribEnd,'rb') as f:
        ribUpdates = pickle.load(f)
    print("LOADING UPDATE")
    updates=pickle.load(open(updatesPath+updateEnd,'rb'))
    results = []
    count0 = 1
    for ribMonitorASN in ribUpdates:
        print(f'tid {tid} is working on rib monitor asn {count0}/{len(ribUpdates.keys())}')
        count0+=1
        count = 1
        for ribPeerIP in ribUpdates[ribMonitorASN]:
            print(f'tid {tid} is working on rib peer ip {count}/{len(ribUpdates[ribMonitorASN].keys())}')
            count +=1
            # count = 0
            ribASNCTR = 0
            ribasns = []
            for ribASN in ribUpdates[ribMonitorASN][ribPeerIP]:
                ribasns.append(ribASN)
                if ribASNCTR > num_victim_asns_to_consider_ribs:
                    # print('ribASNCTR break')
                    break
                ribASNCTR+=1
                # print(f'tid {tid} is working on rib asn {count}/{len(ribUpdates[ribMonitorASN][ribPeerIP][ribASN])}')
                # count +=1
                hijWins = 0
                partials=0
                vicWins = 0
                for ribUpdate in ribUpdates[ribMonitorASN][ribPeerIP][ribASN][:num_victim_updates_to_consider]:
                    # print(f'tid {tid} is working on rib update {count}/{len(ribUpdate)}')
                    # exit(0)
                    # print(ribUpdate)
                    try:
                        printed = True
                        for updateMonitorASN in updates:
                            if(printed):
                                # print(f'updates: {tid}',len(updates))
                                printed = False
                            printed2 = True
                            for updatePeerIP in updates[updateMonitorASN]:
                                if printed2:
                                    # print(f'updatePeerIP: {tid}',len(updates[ribMonitorASN]))
                                    printed2 = False
                                printed3 = True
                                updateASNCTR = 0
                                for updateASN in updates[updateMonitorASN][updatePeerIP]:
                                    if updateASNCTR > num_hijacker_asns_to_consider_updates:
                                        # print('update asn ctr break')
                                        break
                                    if updateASN!=ribASN:   
                                        updateASNCTR+=1 
                                        # if printed3:
                                        #     print(f'updateASN: {tid}',len(updates[updateMonitorASN][updatePeerIP]))
                                        #     printed3 = False 
                                        
                                        printed4 = True
                                        for update in updates[updateMonitorASN][updatePeerIP][updateASN][:number_hijack_updates_to_consider_at_most]:#[:updateTestCount]:
                                            results.append(doTheThingGandalf(update,ribUpdate,ribASN,updateASN))
                                        # for update in 
                                        # if printed4:
                                        #     print(f'update, {tid}',len(updates[updateMonitorASN][updatePeerIP][updateASN]))
                                            
                                        #     printed4 = False
                                        
                                        
                                        # print(update)
                                    # exit(1)
                                        # prefix = update['prefix']
                                        # if prefix not in prefixes: #have not already looked at it
                                        #     prefixes.append(prefix)
                                        #     prevTime = update['timestamp']
                                        
                                            
                                        # else:#prefix already seen 
                                        #     if timeDiffSkip(prevTime,update): #and theres a time difference of > 3 min
                                        #         prevTime = update['timestamp']
                                        #         results.append(doTheThingGandalf(update,ribUpdate,ribASN,updateASN))                                                    
                                        #     else:#there is < a 3 min timediff
                                        #         break   
                                            #its getting TOO BIG
                                        # if len(results) >= 1000000:
                                        #     # storeResults(ribCollector,results,tid,victimASN=ribASN)
                                        #     #MEM BE FREE!
                                        #     print("MEM BE FREE~~~~~ from length")
                                        #     # results = []            
                                            # print(success)
                  
                    except Exception as e:
                            print("exception in gogomagic ", e)
                            pass
                
                #MEM BE FREE!
    #<---pushed too far will crash when storeResults is there
        storeResults(ribCollector,results,tid,victimASN=ribasns,shouldPrint=True)
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
    for i in range(10):
        print("~~~~~~~~~DONE~~~~~~~~~")
    # if isZero:
    #     for i in range(20):
    #         print("~~ZERO~~~~ZERO~~~DONE~~ZERO~~~~ZERO~~~")
# def gogogadgetmagicfunction(ribEnd,updateEnd,tid):
#     #compares for a single monitor
#     #used for testing
#     ribTestCount = 2 
#     updateTestCount = 2
#     print("LOADING RIB")
#     with gzip.open(ribsPath+ribEnd,'rb') as f:
#         ribUpdates = pickle.load(f)
#     print("LOADING UPDATE")
#     updates=pickle.load(open(updatesPath+updateEnd,'rb'))
#     results = []
#     for ribMonitorASN in ribUpdates:
#         for ribPeerIP in ribUpdates[ribMonitorASN]:
#             for ribASN in ribUpdates[ribMonitorASN][ribPeerIP]:
#                 hijWins = 0
#                 partials=0
#                 vicWins = 0
#                 for ribUpdate in ribUpdates[ribMonitorASN][ribPeerIP][ribASN][:ribTestCount]:
#                     # print(ribUpdate)
#                     try:
#                         for updateASN in updates[ribMonitorASN][ribPeerIP]:
#                             if updateASN!=ribASN:     
#                                 for update in updates[ribMonitorASN][ribPeerIP][updateASN][:updateTestCount]:
                                    
#                                     storeDict = {}
#                                     success = applyPolicy(ribUpdate,update)
#                                     if success == 'Equal':
#                                         partials+=1
#                                     elif success:
#                                         hijWins+=1
#                                     else:
#                                         vicWins +=1
#                                     vicOrigin = ribUpdate['origin']
#                                     hijOrigin = update['origin']
#                                     sameSenderASN = isNeighborSame(ribUpdate,update)
#                                     vicASN = ribASN
#                                     hijASN = updateASN
#                                     if success == True:
#                                         success = 1
#                                     if success == False:
#                                         success = 0
#                                     if success == 'Equal':
#                                         success = 'E' #reduce the amount of stored data 
                                    
#                                     storeDict = {'victimASN':vicASN, 'hijASN':hijASN,
#                                             'success':success,'vicOrigin':vicOrigin,
#                                             'hijOrigin':hijOrigin,'sameSenderASN':sameSenderASN}
#                                     results.append(storeDict)
                                    
#                                 # exit(0)
#                                     # print(success)
#                         #store here 
                        

#                     except Exception as e:
#                             print("exception in gogomagic ", e)
#                             pass
#                 storeResults(results,tid)
#                 #MEM BE FREE!
#                 results = []
#     #percentages                                
#                 print('hij wins!',hijWins,"percent", hijWins/(hijWins+partials+vicWins)*100)
#                 print('partials?',partials, "percent",partials/(hijWins+partials+vicWins)*100)
#                 print('origPath',vicWins,"percent",vicWins/(hijWins+partials+vicWins)*100)
            
                                    
#     # print('hij wins!',hijWins)
#     # print('partials?',partials)
#     # print('origPath',vicWins)
    
#     #memory be FREE!
#     updates = ""
#     ribUpdates = ""

def getCollector(file):
    if 'rrc' in file:
        #RE to find RIPE collectors
        collectorRE = r"rrc\d*-"
    else: #RE to find routeViews collectors
        collectorRE = r"route-(.*?-)"
    m = re.search(collectorRE,file)
    collector = m[0][:-1]
    return collector
#~~~~~MAIN~~~~~~#

updateFiles = os.listdir(updatesFileDir)
ribFiles = os.listdir(ribsFileDir)

numProcesses = 8
combos = []
i = 0

# if numProcesses %2 == 0:
#     mod = numProcesses+1
# else:
#     mod = numProcesses

for ribFile in ribFiles:
    ribCollector = getCollector(ribFile)

    for updateFile in updateFiles:
        updateCollector = getCollector(updateFile)
        if ribCollector == updateCollector:
            # print("rib ",ribCollector, "update: ",updateCollector)
            
            combos.append((ribFile,updateFile, i))
            i +=1

c = combos
# print(combos[:10])
#wtf even is this name....
# gogogadgetmagicfunction2(combos[0][0],combos[0][1],combos[0][2])
from multiprocessing import Pool
pool = Pool(processes=numProcesses)
pool.starmap(gogogadgetmagicfunction2,c)
pool.close()

            # print(m)
            # print(m[0][:-1])
                        

# rib = ribFiles[0]
# print(rib)

# ribFileGroup, ribNormalFiles = groupFiles(ribFiles)
# updatesFileGroup, updatesNormalFiles= groupFiles(updateFiles)
# # c = 'rrc26'
# startTime = '2024-03-31T02:00:00'
# endTime = '2024-03-31T02:00:00'
# allStats = []

# #time is irrelevent, we just need to load from the same collector file for both updates and ribs 

# collectorSet = set()


# for c in ribFileGroup:
#     collectorSet.add(c)
# for c in ribNormalFiles:
#     collectorSet.add(c)

# print(collectorSet,len(collectorSet))


# #normal files first
# normalFileCombos = []
# for collector in collectorSet:
#     try:
#         for ribFile in ribNormalFiles[collector]:
#             for updateFile in updatesNormalFiles[collector]:
#                 normalFileCombos.append((ribFile,updateFile))
#                 # print(ribFile,updateFile)
#     except KeyError as e:
#         print("collector ", collector, "not found.", e)
#         continue

# multipartFileCombos = []
 
# for collector in collectorSet:
#     try:
#         for ribStartTimes in ribFileGroup[collector]:
#             for updateStartTimes in updatesFileGroup[collector]:
#                 multipartFileCombos = combineRibWithRibs(ribFileGroup,updatesFileGroup,collector)
                
#     except KeyError as e:
#         print("collector ", collector, "not found.", e)
#         continue




# allCombos = normalFileCombos    
# for multipart in multipartFileCombos:
#     allCombos.append(multipart)

# for c in normalFileCombos:
#     print(c)

# # for combo in combos:
# ribEnd = allCombos[0][0]
# updateEnd = allCombos[0][1]
# print(ribsPath+ribEnd)
# # print("LOADING RIB")
# # with gzip.open(ribsPath+ribEnd,'rb') as f:
# #     ribUpdates = pickle.load(f)
# updates = []

# i = 0
# newcombos = []
# for combo in allCombos:
#     newcombos.append((combo[0],combo[1],i%6))
#     i+=1
# print (ribEnd, updateEnd)
# # print(newcombos)

#~~~~END MAIN ~~~~~$

# gogogadgetmagicfunction(ribEnd,updateEnd,1)
#<TODO> store if the neighbor that sent was different as well as the source of the update 
# from multiprocessing import Pool
# c = combos[:15]
# print("~~~~")
# print(c)

            #exit(0)
            #break
# for updateMonitorASN in updates:
#     for updatePeerIP in updates[updateMonitorASN]:
#         for updateASN in updates[updateMonitorASN][updatePeerIP]:
#             for update in updates[updateMonitorASN][updatePeerIP][updateASN][:10]:
#                 print(update)
#             exit(0)
    # print(update[updateASN])
# print(len(rib))
# print(len(update))
    # print(rib,update)






# for collector in collectorSet:
#     try:
#         startTimes = ribFileGroup[collector]
#     except:
#         continue
#     for startTime in startTimes:
#         for endTime in ribFileGroup[collector][startTime]:
#             #files i need to load 
#             ribFileGroupArray = getFileGroupArray(ribFileGroup,c,startTime,endTime)
#             if ribFileGroupArray == None:
#                 print('ribFileGroupArray is none!', collector,startTime,endTime)
#            # try:
#             for stu in updatesFileGroup[collector]:
#                 for etu in updatesFileGroup[collector][stu]:
#                     updatesFileGroupArray = getFileGroupArray(ribFileGroup,c,startTime,endTime)
#                     for ribFile in ribFileGroupArray:
#                         for updateFile in updatesFileGroupArray:
#                             print(ribFile,updateFile)
#             # except KeyError as e:
#             #     print('except key error:', e)
                

            #allStats.append((c,len(fileGroupArray),startTime,endTime))

#     ribStartTimes = findStartTimesForCollector(ribFileGroup,collector)
#     updatesStartTimes = findStartTimesForCollector(updatesFileGroup,collector)

# for c in ribFileGroup:
#     collector = findStartTimesForCollector(ribFileGroup,c)
#     for startTime in collector:
#         for endTime in collector[startTime]:
#             fileGroupArray = getFileGroupArray(ribFileGroup,c,startTime,endTime)
#             allStats.append((c,len(fileGroupArray),startTime,endTime))


# for c in updatesFileGroup:
#     collector = findStartTimesForCollector(updatesFileGroup,c)
#     for startTime in collector:
#         for endTime in collector[startTime]:
#             fileGroupArray = getFileGroupArray(updatesFileGroup,c,startTime,endTime)
#             allStats.append((c,len(fileGroupArray),startTime,endTime))
            
#             # print(c,'has',len(fileGroupArray))

# sortedByRrc = sorted(allStats,key=lambda l: l[0])
# sortedByNumFiles = sorted(allStats,key=lambda l: l[1])

# print("~~~sorted by rrc~~~")
# for a in sortedByRrc:
#     print(a)
# print("~~~sorted by numFiles~~~")
# for b in sortedByNumFiles:
#     print(b)
# from datetime import datetime
# s = '2024-03-31T00:00:00'
# fmt = "%Y-%m-%dT%H:%M:%S"
# dt = datetime.strptime(s,fmt)
# print(dt)
    # for c in fileGroups:
    #     for s in fileGroups[c]:
    #         for e in fileGroups[c][s]:
    #             for things in fileGroups[c][s][e]:
                    
# def findLocalPref(ribEnd):
#     print("LOADING UPDATE")
#     with gzip.open(ribsPath+ribEnd,'rb') as f:
#         updates = pickle.load(f)
#     # updates=pickle.load(open(updatesPath+updateEnd,'rb'))
#     for updateMonitorASN in updates:
#         for updatePeerIP in updates[updateMonitorASN]:
#             for updateASN in updates[updateMonitorASN][updatePeerIP]:
#                 for update in updates[updateMonitorASN][updatePeerIP][updateASN]:
#                     local_pref = int(update['local_pref'])
#                     if local_pref !=0:
#                         print('local: ',local_pref,update)
#                         exit(0)
# def doEndTimes(fileGroup1, startTime,collector,fileGroup2):
#     combinations = []
#     try:
#         for endTime in fileGroup1[collector][startTime]:
#              for updateFile in updatesNormalFiles[collector]:
#                 normalFileCombos.append((ribFile,updateFile))
#     except:
#         pass