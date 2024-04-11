import pickle 
import requests
masterNeighbors = pickle.load(open('pickles/masterNeighborTable.pickle','rb'))


        # print('no')
def getNeighbor(asn):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    """
    query_time= "2024-03-01T09:00:00"
    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    
    print("getting neighbor for: ",asn)
    neighbors = set()
    url = f"https://stat.ripe.net/data/asn-neighbours/data.json?resource={asn}&query_time={query_time}&lod=0"
    print("getting neighbors for AS",asn, type(asn))
    print(url)
    res = requests.get(url)
    try:
        json = res.json()
        allneighbors = json["data"]["neighbours"]
        print('all neighbors: ', allneighbors)
    except:
        print("error getting neighbors for ", asn)
        return
    # print(json)
    
    
    for neighbor in allneighbors:
        neighbors.add(neighbor['asn'])
    # if len(neighbors) !=0: 
    print(neighbors)        
    pickle.dump(neighbors,open(f'pickles/neighbors/{asn}-{safeTime}','wb'))
    
things = []
# for i in range()
# for asn in masterNeighbors:
#     if masterNeighbors[asn] ==None or len(masterNeighbors[asn])==0:
#          things.append(asn)
    # if masterNeighbors[asn]:
    #     # print(type(asn))
    #     # print("yes")
    #     pass
    # else:
    #     # getNeighbor(asn)
    #     print(asn, masterNeighbors[asn])
    #     things.append(asn)
# print(len(things), type(things[0]),things[0])


for i in range(1,400001):
    if str(i) not in masterNeighbors.keys():
        print(i, 'not in keys')
        things.append(i)
        getNeighbor(i)
# print(len(things))
# for asn in things:
#     if type (masterNeighbors[asn]) is  set:
#         print(asn,masterNeighbors[asn])