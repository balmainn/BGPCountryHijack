import pickle 
import os 
somedir = 'pickles/processedUpdates/'
file = 'route-views.chile-27678.pickle'
# file = 'route-views.linx-714.pickle'
# files = os.listdir(somedir)
#for file in files:
prefixNeighborsDict = pickle.load(open(somedir+file,'rb'))
collector = 'route-views.chile'
peer='27678'

def getAllNeighbors(storeDict):
    allNeighbors = set()
    for prefix in storeDict:
        for neighbor in storeDict[prefix].keys():
            allNeighbors.add(neighbor)
    return allNeighbors
allNeighbors = getAllNeighbors(prefixNeighborsDict)
# print(len(allNeighbors))
print(allNeighbors)
#neighborTalleys = {} #{prefix: {n1: n2, count: 0 }}
neighborUpdates ={}
for neighbor in list(allNeighbors):
    for prefix in prefixNeighborsDict:
        if neighbor not in prefixNeighborsDict[prefix].keys():
            continue
        updates = prefixNeighborsDict[prefix][neighbor]
        if neighbor not in neighborUpdates.keys():
            neighborUpdates[neighbor] = {}
            if prefix not in neighborUpdates[neighbor].keys():
                neighborUpdates[neighbor][prefix] = []
        neighborUpdates[neighbor][prefix]= updates

#neighborUpdates['16471']
# print(neighborUpdates)
for neighbor in neighborUpdates:
    ct = 0
    try:
        print(neighbor, len(neighborUpdates[neighbor]['185.18.201.0/24']))
        for update in neighborUpdates[neighbor]['185.18.201.0/24']:
            print(update)
    except:
        pass
    # for prefix in neighborUpdates[neighbor]:
    #     if ct < 5:
    #         print(prefix)
    #     else:
    #         break
    #     ct+=1
        
        


outdir = "pickles/collectorPeerASNeighbors"
