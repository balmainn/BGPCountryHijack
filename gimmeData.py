import pickle 
ALL = True
USE_HIJACKER = not ALL
if not ALL:
    if USE_HIJACKER:
        processed = pickle.load(open('pickles/results/normalizedVictimResults.pickle','rb'))
    else:
        processed = pickle.load(open('pickles/results/normalizedHijackerResults.pickle','rb'))
#ALL data nothing removed 
else:
    if USE_HIJACKER:
        processed = pickle.load(open('pickles/results/allHijackerResults.pickle','rb'))
    else:
        processed = pickle.load(open('pickles/results/allVictimResults.pickle','rb'))

def extractData(dataDict,keyType):
   
    print("extracting data ",keyType)
    
    #(r,g,b,a)
    # random.seed(datetime.now().timestamp())
    # r = random.randint(0,100)
    
    #res = {}
    results = {'Success': 0, 'Partial': 0, 'Failure': 0}
    
    for hijackerASN in dataDict:
        infoDict = dataDict[hijackerASN][keyType]
    
        # try:
        #     neighbors = len(cone[str(hijackerASN)]) #int(info[hijackerASN]['neighbors'])
        # except:
        #     #continue
        #     neighbors = 0
        
        # print(dataDict)
        # print(hijackerASN)    
        success = int(dataDict[hijackerASN][keyType]['hijackerWins'])
        partial = int(dataDict[hijackerASN][keyType]['hijackerTies'])
        failure = int(dataDict[hijackerASN][keyType]['hijackerLosses'])
        # if success ==0 and partial == 0 and failure ==0:
        #     continue
        results['Success']+=success
        results['Partial']+=partial
        results['Failure']+=failure
        
    
    return results 



for victim in processed:
    
    print(f"Creating plots for AS {victim}")

    res = extractData(processed[victim],'policy')
    print("result of policy is: ",res)
    res = extractData(processed[victim],'asPath')
    print("result of asPath is: ",res)
    res = extractData(processed[victim],'originType')
    print("result of originType is: ",res)