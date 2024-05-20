import os
import gzip 
import pickle
import re 
#'pickles/ribData/{collectorID}-{startTime}-{endTime}.pickle
updatesFileDir = 'pickles/updateData/'
ribsFileDir = 'pickles/ribData/'


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

def applyPolicy(victim, hij, victimCone, hijackerCone):
    # print('checking victim',victim)
    # print('hijacker:',hij)
    # policyChoice = random.randint(0, 100) 

    # if policyChoice <= 25:
        #This first policy selection is for shortest path. Returns True if the hijack is 
        #successful. This policy would mirror one which does not have any restrictions on 
        #import or export, and has no preferred paths selected 
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

updateFiles = os.listdir(updatesFileDir)
ribFiles = os.listdir(ribsFileDir)

rib = ribFiles[0]
print(rib)
# with gzip.open(ribsFileDir+rib,'rb') as f:
#     r = pickle.load(f)
#     print(len(r),type(r))

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
    
    


#         # # print(span)
#         # collector = file[:span0]
#         # print(collector)
#         # print(file[span0:span1])

ribFileGroup, ribNormalFiles = groupFiles(ribFiles)
# collectorSet = set()
# for collector in ribFileGroup:
#     collectorSet.add(collector)
# for collector in ribNormalFiles:
#     collectorSet.add(collector)

# for c in ribFileGroup:
#         for s in ribFileGroup[c]:
#             for e in ribFileGroup[c][s]:
#                 print('collector',c,ribFileGroup[c][s][e])
                    
# print(collectorSet)
updatesFileGroup, updatesNormalFiles= groupFiles(updateFiles)


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


c = 'rrc26'
startTime = '2024-03-31T02:00:00'
endTime = '2024-03-31T02:00:00'
allStats = []

#time is irrelevent, we just need to load from the same collector file for both updates and ribs 

collectorSet = set()


for c in ribFileGroup:
    collectorSet.add(c)
for c in ribNormalFiles:
    collectorSet.add(c)

print(collectorSet,len(collectorSet))


#normal files first
normalFileCombos = []
for collector in collectorSet:
    try:
        for ribFile in ribNormalFiles[collector]:
            for updateFile in updatesNormalFiles[collector]:
                normalFileCombos.append((ribFile,updateFile))
                # print(ribFile,updateFile)
    except KeyError as e:
        print("collector ", collector, "not found.", e)
        continue

multipartFileCombos = []

def doEndTimes(fileGroup1, startTime,collector,fileGroup2):
    combinations = []
    try:
        for endTime in fileGroup1[collector][startTime]:
             for updateFile in updatesNormalFiles[collector]:
                normalFileCombos.append((ribFile,updateFile))
    except:
        pass

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


            
    
    # try:
    #     return 
    # except KeyError as e:
    #     print('Key error in filegroups. cannot find ', e)
    #     return None
combos = []    
for collector in collectorSet:
    try:
        for ribStartTimes in ribFileGroup[collector]:
            for updateStartTimes in updatesFileGroup[collector]:
                combos = combineRibWithRibs(ribFileGroup,updatesFileGroup,collector)
                
    except KeyError as e:
        print("collector ", collector, "not found.", e)
        continue

print(combos)
ribsPath = 'pickles/ribData/'
updatesPath = 'pickles/updateData/'

# for combo in combos:
ribEnd = combos[0][0]
updateEnd = combos[0][1]
print(ribsPath+ribEnd)
# print("LOADING RIB")
# with gzip.open(ribsPath+ribEnd,'rb') as f:
#     ribUpdates = pickle.load(f)
updates = []
# for combo in combos:
    
#     updateEnd = combo[0]
#     updates.append(updateEnd)
    # print("LOADING UPDATE")
    # updates=pickle.load(open(updatesPath+updateEnd,'rb'))
    # findLocalPref(updates)
def findLocalPref(ribEnd):
    print("LOADING UPDATE")
    with gzip.open(ribsPath+ribEnd,'rb') as f:
        updates = pickle.load(f)
    # updates=pickle.load(open(updatesPath+updateEnd,'rb'))
    for updateMonitorASN in updates:
        for updatePeerIP in updates[updateMonitorASN]:
            for updateASN in updates[updateMonitorASN][updatePeerIP]:
                for update in updates[updateMonitorASN][updatePeerIP][updateASN]:
                    local_pref = int(update['local_pref'])
                    if local_pref !=0:
                        print('local: ',local_pref,update)
                        exit(0)



ribTestCount = 2 
updateTestCount = 2




#  for updateMonitorASN in updates:
#                     for updatePeerIP in updates[ribMonitorASN]:
#                         for updateASN in updates[ribMonitorASN][ribPeerIP]:

def gogogadgetmagicfunction(ribEnd,updateEnd):
    hijWins = 0
    partials=0
    vicWins = 0
    print("LOADING RIB")
    with gzip.open(ribsPath+ribEnd,'rb') as f:
        ribUpdates = pickle.load(f)
    print("LOADING UPDATE")
    updates=pickle.load(open(updatesPath+updateEnd,'rb'))
    for ribMonitorASN in ribUpdates:
        for ribPeerIP in ribUpdates[ribMonitorASN]:
            for ribASN in ribUpdates[ribMonitorASN][ribPeerIP]:
                for ribUpdate in ribUpdates[ribMonitorASN][ribPeerIP][ribASN][:ribTestCount]:
                    # print(ribUpdate)
                    try:
                        for updateASN in updates[ribMonitorASN][ribPeerIP]:
                            if updateASN!=ribASN:     
                                for update in updates[ribMonitorASN][ribPeerIP][updateASN][:updateTestCount]:
                                    success = applyPolicy(ribUpdate,update,0,0)
                                    if success == 'Equal':
                                        partials+=1
                                    elif success:
                                        hijWins+=1
                                    else:
                                        vicWins +=1
                                # exit(0)
                                    # print(success)
                    except:
                            pass
                                    
    print('hij wins!',hijWins,"percent", hijWins/(hijWins+partials+vicWins)*100)
    print('partials?',partials, "percent",partials/(hijWins+partials+vicWins)*100)
    print('origPath',vicWins,"percent",vicWins/(hijWins+partials+vicWins)*100)
    
    #memory be FREE!
    updates = ""
    ribUpdates = ""
from multiprocessing import Pool
c = combos[:15]
print("~~~~")
print(c)
pool = Pool(processes=5)
pool.starmap(gogogadgetmagicfunction,c)
pool.close()
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
                    
