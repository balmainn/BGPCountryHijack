import networkx
import pickle 

import requests
import bgpkit


def checkpoint(startTime:str,endTime:str,graph:networkx.DiGraph):
    safeStartTime = startTime.replace(':','-')
    safeEndTime = endTime.replace(':','-')
    print(safeStartTime,safeEndTime )
    pFileName = safeStartTime+'--'+safeEndTime+"iDieGraph.pickle"
    pickle.dump(graph, open(pFileName,'wb'))
    pass


def getAllUpdateFilesForTimeRangeRequestVersion(tStart,tEnd):
    #need a way to sort by monitor
    """uses requests"""
    i = 0
    maxSearch = 10000
    dataUrls = []
    while i < maxSearch:
    # for i in range(10):
        page_size = 1000
        pageNum=i
        i +=1
        url=f"https://alpha.api.bgpkit.com/broker?ts_start={tStart}&ts_end={tEnd}&page={pageNum}&page_size={page_size}"
        res = requests.get(url)
        js = res.json()
        if js['count'] ==0 :
            break
        print( js['data'])
        for data in js['data']:
            dataUrl = data['url']
            dataUrls.append(dataUrl)
            print(dataUrl)
        print("~~~~~~~~~~~~~~~~")
    return dataUrls

def getAllUpdateFilesForTimeRange(tStart,tEnd,pageSize = 1000):
    #need a way to sort by monitor
    broker = bgpkit.Broker(page_size=pageSize)
    dataUrls = []
    items = broker.query(ts_start=tStart, ts_end=tEnd)
    for item in items:
        print(item.url)
        dataUrls.append(item.url)
    print(len(items))
    return dataUrls
import json
from multiprocessing import Pool
def multiProcessDataWithOriginASN(dataUrls,asn,processes=4):
    #need a way to sort by monitor
    dataToParse = []
    for dataUrl in dataUrls:
        dataToParse.append((dataUrl,asn))
    pool = Pool(processes=processes)
    res = pool.starmap(multiProcessParseDataWithOriginASN,dataToParse)
    pool.close()
    c = 0
    for r in res:
        if len(r) ==0:
            continue
        print(r)
        c+=1
    print(len(res),c)
    # res = pool.map_async(getMonitorTrainingData,monitorPrefixes)
    
    pass
def multiProcessParseDataWithOriginASN(dataUrl,asn):
    parser = bgpkit.Parser(url=dataUrl,
                        cache_dir="cache",
                        filters={"origin_asn":f"{asn}","type":"announce"}
                        )
    allPaths =[]
    elems = parser.parse_all()
    for elem in elems:
        # elem_type = elem['elem_type']
        # if elem_type != 'A':
        #     continue
        paths = elem['as_path'].split()
        #convert paths to set to remove duplicates 
        pset = set()
        for p in paths:
            pset.add(p)
        timestamp = elem['timestamp']
        
        allPaths.append( list(pset))
        # print(pset)
    return allPaths

def multiprocessParsing(dataUrl):
    """parses each data URl with bgpkit
    this function caches the datafiles by default 
    params:
        dataUrls: a list of datafiles that will be parsed
    returns:
        allPaths-> list of tuples -> (path, timestamp)
    """
    allPaths = []
    
    print("parsing url!!", dataUrl)
    
    parser = bgpkit.Parser(url=dataUrl,cache_dir="cache",filters={"type":"announce"})
    # parser = bgpkit.Parser(url=dataUrl,filters={"type":"announce"})
    elems = parser.parse_all()
    i = 0
    for elem in elems:
        if i > 10:
            break
        i+=1
        # elem_type = elem['elem_type']
        # if elem_type != 'A':
        #     continue
        paths = elem['as_path'].split()
        #convert paths to set to remove duplicates 
        pset = set()
        for p in paths:
            pset.add(p)
        
        allPaths.append( list(pset))
        # print(pset)
    return allPaths
def parseDataUrls(dataUrls):
    """parses each data URl with bgpkit
    this function caches the datafiles by default 
    params:
        dataUrls: a list of datafiles that will be parsed
    returns:
        allPaths-> list of tuples -> (path, timestamp)
    """
    allPaths = []
    i = 0
    for dataUrl in dataUrls:
        print("parting url", dataUrl , i+1 , '/ ', len(dataUrls))
        i+=1
        parser = bgpkit.Parser(url=dataUrl,cache_dir="cache",filters={"type":"announce"})
        elems = parser.parse_all()
        for elem in elems:
            # elem_type = elem['elem_type']
            # if elem_type != 'A':
            #     continue
            paths = elem['as_path'].split()
            #convert paths to set to remove duplicates 
            pset = set()
            for p in paths:
                pset.add(p)
            timestamp = elem['timestamp']
            
            allPaths.append( list(pset))
            # print(pset)
    return allPaths

def parseDataUrlsWithOriginASN(dataUrls,asn):
    """parses each data URl with bgpkit
    this function caches the datafiles by default 
    params:
        dataUrls: a list of datafiles that will be parsed
        asn: the ASN we want to find the data for
    returns:
        allPaths-> list of tuples -> (path, timestamp)
    """
    allPaths = []
    i = 0
    for dataUrl in dataUrls:
        print("parting url", dataUrl , i+1 , '/ ', len(dataUrls))
        i+=1
        parser = bgpkit.Parser(url=dataUrl,
                        cache_dir="cache",
                        filters={"origin_asn":f"{asn}","type":"announce"}
                        )
        elems = parser.parse_all()
        for elem in elems:
            # elem_type = elem['elem_type']
            # if elem_type != 'A':
            #     continue
            paths = elem['as_path'].split()
            #convert paths to set to remove duplicates 
            pset = set()
            for p in paths:
                pset.add(p)
            timestamp = elem['timestamp']
            
            allPaths.append( (list(pset),timestamp))
            # print(pset)
    return allPaths
def addPathToGraph(path:list,dGraph:networkx.DiGraph):
    #<TODO>
    #add all the nodes in the path
    dGraph.add_nodes_from(path)
    for i in range(len(path)):
        nodeA = path[i]
        if(i+1 >= len(path)):
            break
        nodeB = path[i+1]
        dGraph.add_edge(nodeA,nodeB)
        

###~~~~~~MAIN~~~~~~~~~~main~~~~~~~~~###
# tStart="2008-02-24T18:00:00"
tStart="2024-03-31T00:00:00"
tEnd="2024-03-31T02:00:00"
# tEnd="2024-04-01T00:00:00"
timeFmt = "%Y-%m-%dT%H:%M:%S"

from datetime import datetime, timedelta

stfmt = datetime.strptime(tStart,timeFmt)
tEnd = tStart
tStart = (stfmt - timedelta(days=1)).strftime(timeFmt)
print(tStart, type(tStart), tEnd)
# checkpoint(tStart,tEnd,networkx.DiGraph())

dGraph = networkx.DiGraph()
datafiles = getAllUpdateFilesForTimeRange(tStart,tEnd)
# paths = parseDataUrls(datafiles)
allPaths = []
pool = Pool(processes=1)
paths = pool.map(multiprocessParsing,datafiles[:4])
# print(paths)
pool.close()
for p1 in paths:
    print('p1:',p1)
    for p2 in p1:
        print('p2--:',p2)
        for p3 in p2:
            allPaths.append(p3)
addPathToGraph(allPaths,dGraph)
print("paths added!")
print(len(paths))
# checkpoint(tStart,tEnd,dGraph)

from matplotlib import pyplot as plt
networkx.draw(dGraph)
plt.show()


    

class BGPPolicy():
    def __init__(self) -> None:
        self.policyName = ""
        self.localPreference = ""
        self.importPolicy = ""
        self.exportPolicy = ""
    pass

class BGPASN():
    def __init__(self,asn) -> None:
        self.asn = asn
        self.prefixes = []
        self.policy = BGPPolicy()
        self.community = []
    def addPrefix(self,prefix):
        self.prefixes.append(prefix)
        pass
    def addCommunity(self,community):
        self.community.append(community)



# dataUrls = getAllUpdateFilesForTimeRange(tStart,tEnd)
# multiProcessDataWithOriginASN(dataUrls,174)

        # print("path len is now: ",len(allPaths))

# print(allPaths)
        # print(json.dumps(elem, indent=4))
        # break

# dataUrls = getAllUpdateFilesForTimeRange(tStart,tEnd)

# """from the github repo readme: 
#     The Parser constructor takes the following parameters:

#     url: the URL or local file path toward an MRT file
#     fitlers: optional a dictionary of filters, available filters are:
#         origin_asn: origin AS number
#         prefix: exact match prefix
#             prefix_super: exact prefix and its super prefixes
#             prefix_sub: exact prefix and its sub prefixes
#             prefix_super_sub: exact prefix and its super and sub prefixes
#         peer_ip: peer's IP address
#         peer_ips: peers' IP addresses
#         peer_asn: peer's ASN
#         type: message type (withdraw or announce)
#         ts_start: start unix timestamp
#         ts_end: end unix timestamp
#         as_path: regular expression for AS path string
#     cache_dir: optional string for specifying a download cache directory
# """

# parser = bgpkit.Parser(url="https://data.ris.ripe.net/rrc15/2008.02/updates.20080224.2300.gz",
#                        cache_dir="cache"
#                        )
# elems = parser.parse_all()
# # assert len(elems) == 4227
# import json
# for elem in elems:
#     if elem['elem_type'] != "A":
#         continue
#     print(json.dumps(elem, indent=4))
#     break

