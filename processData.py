from matplotlib import pyplot

import pickle 
import gzip
import os
import re
#rfile= "pickles/results/rrc03-[196740, 209854, 209767, 137409, 215677, 16509, 61028, 60980, 50427, 50174, 34771, 50591, 57324, 201942, 199610, 60976, 44592, 48314, 197071, 30823, 21176, 50299]-tid6487-results-0"
# rfile = "pickles/results/rrc26-v[51375]-h[9829]-tid502-results-0"


#sum up all trues, falses, and Es 
def parseSuccesses(keyValue,dictResults,result):
    # print('parsing successes')
    # print(keyValue)
    # print(dictResults)
    # print(result)
    # result[keyValue]
    # dictResults['policy'][keyValue]
    res = result[keyValue]
    if res == None or res == "E":
        dictResults['policy'][keyValue]['hijackerTies']+=1
    elif res == True:
        dictResults['policy'][keyValue]['hijackerWins']+=1
    elif res == False:
        dictResults['policy'][keyValue]['hijackerLosses']+=1
    else:
        print("UKNOWN VALUE IN STORE SINGLE RESULT WTF")
        exit(0)
def getHijackingASes(file):
    print(file)
    hijASRE = r'h\[.*\]-' #victim AS regular expression
    try:
        m = re.search(hijASRE,file)
        hijASes = m[0][2:-2].split(', ') #idea make this a set
    except Exception as e:
        print("get hijacking ",e)
        return "Unknown"
    # print(vicASes)
    return hijASes

def getVictimASes(file):
    vicASRE = r'v\[.*\]-h' #victim AS regular expression
    m = re.search(vicASRE,file)
    try:
        vicASes = m[0][2:-3].split(', ') #idea make this a set
    # print(vicASes)
        return vicASes
    except:
        return "Unknown"

def findVictimFiles(vic,listOfFiles):
    vicFiles = []
    for file in listOfFiles:
        victimASes = getVictimASes(file)
        # print(victimASes)
        # exit(0)
        if vic in victimASes:
            vicFiles.append(file)
    return vicFiles

# print(listOfFiles[0])
# a = findVictimFiles('23764',listOfFiles)
# print(a)
# exit(0)
def storeSingleResult(keyValue,dictResults,result):
    #pull value out of result
    #{'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}, 
    # print('storing single result')
    # print(keyValue)
    # print(dictResults)
    # print(result)
    res = result[keyValue]
    if res == None or res == "E":
        dictResults[keyValue]['hijackerTies']+=1
    elif res == True:
        dictResults[keyValue]['hijackerWins']+=1
    elif res == False:
        dictResults[keyValue]['hijackerLosses']+=1
    else:
        print("UKNOWN VALUE IN STORE SINGLE RESULT WTF")
        exit(0)

#~~~~~~MAIN~~~~~#        
def goProcess():
    pref = 'pickles/results/'
    resultsDict = {}
    filecount = 5
    cnt = 0
    allVictims = set()
    allHij = set()
    listOfFiles = os.listdir(pref)
    for file in listOfFiles:
        cnt+=1
        victimASes = getVictimASes(file)
        hijASes = getHijackingASes(file)
        # for v in victimASes:
        #     # print(v)
        #     allVictims.add(v)
        # for hij in hijASes:
        #     allHij.add(hij)
        
    # print(len(allVictims))
    # print(len(allHij))
        # print(a)
        # print(b)
        with gzip.open(pref+file,'rb') as f:
            results = pickle.load(f)
        print(len(results))
        for result in results:
            # print(result)
            victimASN = result['victimASN']
            hijackASN = result['hijASN']
            successResults = result['success']
            try:
                dictHijacker = resultsDict[victimASN]
            except:
                resultsDict[victimASN] = {}
                dictHijacker = resultsDict[victimASN]
            try:
                dictResults = dictHijacker[hijackASN]
            except:
                dictHijacker[hijackASN] = {
                'policy' : {3: {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                        5: {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}, 
                        12:{'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}, 
                        20:{'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}, 
                        50:{'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}, 
                        'random':  {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}},
                'asPath' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0},
                'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}
                }

                dictResults = dictHijacker[hijackASN]
            # print(result)
            
            storeSingleResult('asPath',dictResults,result['success'])
            storeSingleResult('originType',dictResults,result['success'])
            for key in successResults['localPref']:
                parseSuccesses(key,dictResults,result['success']['localPref'])
                #exit(0)
                #   sr = parseSuccesses(successResults)
            # {'hijackerWins':wins,"hijackerLosses":losses,"hijackerTies":ties,
            #  "resolvedBy":resolvedBy}
            # exit(1)
            #resultsDict[victimASN][hijackASN].append(successResults)
            # except Exception as e:
            #     print('exception', e)
            #     resultsDict[victimASN] = {hijackASN:[successResults]}            
            # print(result)
        print("~~~~")
        
        # for victimASN in resultsDict:
        #     hijackerASNSinDict = resultsDict[victimASN]
        #     print(victimASN ,len(hijackerASNSinDict))
            # print("~~~~")
            # for hijackerASN in resultsDict[victimASN]:
            #     results = resultsDict[victimASN][hijackASN]
            #     print(hijackASN, len(results))
                
        print(len(resultsDict))

    pickle.dump(resultsDict,open('pickles/processedResults.pickle','wb'))
processed = pickle.load(open('pickles/processedResults.pickle','rb'))

testAS =23764
testSet = processed[testAS]
for hij in testSet:
    orRes = testSet[hij]['originType']
    print(orRes)
#'originType' : {'hijackerWins':0,"hijackerLosses":0,"hijackerTies":0}

def loadCone():
    cone = pickle.load(open('pickles/asnCone.pickle','rb'))
    sCone = sorted(list(cone.items()), key=lambda a_c: len(a_c[1]),reverse=True)
    return cone,sCone
# print(processed)
def extractData(dataDict,keyType):
    x = []
    y = []
    coords = []
    colors = []
    print("extracting data ",keyType)
    
    #(r,g,b,a)
    # random.seed(datetime.now().timestamp())
    # r = random.randint(0,100)
    value = 1#(100-r)/100
    
    colorSuccess = (0, value, 0, 1)
    
    colorPartial = (0, 0, value, 1)
    
    colorFail    = (value, 0, 0, 1)
    
    cone,sCone = loadCone()
    
    cnt=0
    for hijackerASN in dataDict:
        infoDict = dataDict[hijackerASN][keyType]
    
        # try:
        #     neighbors = len(cone[str(hijackerASN)]) #int(info[hijackerASN]['neighbors'])
        # except:
        #     #continue
        #     neighbors = 0
        neighbors = cnt
        cnt+=1
        # print(dataDict)
        # print(hijackerASN)    
        success = int(dataDict[hijackerASN][keyType]['hijackerWins'])
        partial = int(dataDict[hijackerASN][keyType]['hijackerTies'])
        failure = int(dataDict[hijackerASN][keyType]['hijackerLosses'])
        # print(f"({x1},{y1})")
        # coords.append((x1,y1))
        x.append(neighbors)
        y.append(success)
        colors.append(colorSuccess)
        x.append(neighbors)
        y.append(partial)
        colors.append(colorPartial)
        x.append(neighbors)
        y.append(failure)
        colors.append(colorFail)
    
    return x,y,colors

def extractPolicyData(dataDict,keyType):
    x = []
    y = []
    coords = []
    colors = []
    print("extracting Policy Data ",keyType)
    # print(dataDict)
    
    #(r,g,b,a)
    # random.seed(datetime.now().timestamp())
    # r = random.randint(0,100)
    value = 1#(100-r)/100
    
    colorSuccess = (0, value, 0, 1)
    
    colorPartial = (0, 0, value, 1)
    
    colorFail    = (value, 0, 0, 1)
    
    cone,sCone = loadCone()
    
    cnt=0
    for hijackerASN in dataDict:
        infoDict = dataDict[hijackerASN]['policy'][keyType]
    
        try:
            neighbors = len(cone[str(hijackerASN)]) #int(info[hijackerASN]['neighbors'])
        except:
            #continue
            neighbors = 0
        #neighbors = cnt
        cnt+=1
        # print(dataDict)
        # print(hijackerASN)    
        success = int(infoDict['hijackerWins'])
        partial = int(infoDict['hijackerTies'])
        failure = int(infoDict['hijackerLosses'])
        # print(f"({x1},{y1})")
        # coords.append((x1,y1))
        x.append(neighbors)
        y.append(success)
        colors.append(colorSuccess)
        x.append(neighbors)
        y.append(partial)
        colors.append(colorPartial)
        x.append(neighbors)
        y.append(failure)
        colors.append(colorFail)
    
    return x,y,colors
count = 0
for victim in processed:
    count+=1
    # print(len(processed[victim]))
    #x,y,colors = extractData(processed[victim],'originType')
    x,y,colors = extractPolicyData(processed[victim],3)
    for i in range(len(x[:10])):
        print(x[i],y[i],colors[i])
    title = 'AS '#+file[a+1:b]# + " n1= " +str(lv1)+ " n2= " +str(lv2)+ " n3= " +str(lv3)
    color = 'maroon'
    width = 3
    try:
        xpos = 50#len(cone[file[a+1:b]])
        plt.axvline(xpos,0,max(y),c=color,linewidth=width)
    except:
        pass
    
    # plt.annotate(str(lv1), xy=(lv1, -1))
    # plt.axvline(lv2,0,max(y),c=color,linewidth=width)
    # plt.annotate(str(lv2), xy=(lv2, -1))
    #plt.axvline(lv3,0,10,c='lavenderblush')
    plt = pyplot
    plt.title(title)
    plt.xlabel('Hijacker Cone Size')
    plt.ylabel('Count')
    plt.scatter(x,y,c=colors)
    #plt.axvline(xpoint,ymin,ymax,c='red')
    plt.grid()
    plt.show()
    plt.clf()
    if count > 1:
        exit(0)
    # exit(0)
    for hij in processed[victim]:
        orRes = processed[victim][hij]['originType']['hijackerWins']
        
    

        if orRes > 0:
            print(processed[victim][hij]['originType'])
            print(orRes,victim,hij)
            #print(processed[victim])
            # exit(0)
        #print(victim)
#     exit(0)
    # if cnt > filecount:
    #     for r in resultsDict:
    #         for s in resultsDict[r]:
    #             print(resultsDict[r][s])
    #             print("~~~")
        # print(resultsDict)
        # exit(0)

