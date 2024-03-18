import networkx 
import requests
import pickle 
import os 
from multiprocessing import Pool
def getNeighbor(asn):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    """
    query_time= "2024-03-01T09:00:00"
    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    if os.path.exists(f'pickles/neighbors/{asn}-{safeTime}'):
        return
        neighbors = pickle.load(open(f'pickles/neighbors/{asn}-{safeTime}','rb'))
        print(asn," neighbors returned from file")
        return neighbors
    
    print("getting neighbor for: ",asn)
    neighbors = set()
    url = f"https://stat.ripe.net/data/asn-neighbours/data.json?resource={asn}&query_time={query_time}&lod=1"
    print("getting neighbors for AS",asn, type(asn))
    res = requests.get(url)
    try:
        json = res.json()
        allneighbors = json["data"]["neighbours"]
    except:
        print("error getting neighbors for ", asn)
        return
    # print(json)
    
    
    for neighbor in allneighbors:
        neighbors.add(neighbor['asn'])
    
    pickle.dump(neighbors,open(f'pickles/neighbors/{asn}-{safeTime}','wb'))
    

def getData():
    asns = []
    #401308 is the last as according to https://2ip.io/analytics/asn-list/?pageId=1219&orderBy=id&itemPerPage=100
    #we just add +1 to make the range actually go that high
    # for i in range(0,401308+1):
    for i in range(385000,401308+1):
        asns.append(i)
    print("i done")
    pool = Pool(processes=8)
    pool.map_async(getNeighbor,asns)
    pool.close()
    pool.join()

getData()