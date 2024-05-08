# import bgpkit
# #general format    https://data.ris.ripe.net/rrcXX/YYYY.MM/TYPE.YYYYMMDD.HHmm.gz
# url =    "https://data.ris.ripe.net/rrc01/2024.02/updates.20240201.0000.gz"
import bgpkit
import os 
import pickle 

url = "https://data.ris.ripe.net/rrc01/2024.02/bview.20240201.0000.gz"
broker = bgpkit.Broker(page_size=1000)
dataUrls = []
tStart="2024-03-31T00:00:00"
tEnd="2024-03-31T02:00:00"
items = broker.query(ts_start=tStart, ts_end=tEnd)
ribs = []
updates = []
unk = []
for item in items:
        # print(item)
        if item.data_type == 'rib':
            ribs.append(item)
        elif item.data_type == 'update':
            updates.append(item)
        else:
            unk.append(item)
print('ribs',len(ribs))
#the ribs present a 'ground truth' of sorts. They are the given state of the network at a given point in time. 
#we use these to build out or original updates for a given observer, 
#then we compare against updates from a different time (thats later)

#run a test on this and compare it to  "http://archive.routeviews.org/route-views.sg/bgpdata/2022.02/RIBS/rib.20220205.1800.bz2"
# peer-stats-single-file --debug http://archive.routeviews.org/route-views.sg/bgpdata/2022.02/RIBS/rib.20220205.1800.bz2 


# print(ribs)

collectors = set()
for rib in ribs:
    collector = rib.collector_id
    collectors.add(collector)
    print(collector)

print(len(collectors))
print(ribs[0])
rib = ribs[0]
startTime = rib.ts_start
endTime = rib.ts_end
print(startTime, endTime)
# parseFile()
def parseFile(brokerItem):
    """simply parse the file and return the elements (list of dictionaries)"""
    print("parsing brokered item",brokerItem)
    #'https://ris.ripe.net/dumps-per-peer-rest/prototype/rrc00/2024-05-06T22/bview-20240506T2200-2406F400000800340000000000000001.gz
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache")      
    elems = parser.parse_all()
    return elems
    cnt=  0
    for elem in elems:
        print(elem)
        if cnt < 10:
             cnt +=1
        else:
            return(0)
        
def createRibsDict(rib,continueAddingToDict=True):
    """create a rib dictionary file
    params: rib: pyBgpkit Broker Item
    add: do we want to add to the dictionary, or do we want to just return what we have (if anything)"""
    #<TODO> consider what happens when we have an update that already exists in the list
    print("creating rib dict for: ",rib)
    collectorID = rib.collector_id
    startTime = rib.ts_start
    endTime = rib.ts_end
    filepath = f'pickles/ribData/{collectorID}-{startTime}-{endTime}.pickle'
    if os.path.exists(filepath):
        asDict = pickle.load(open(filepath,'rb'))
        if not continueAddingToDict:
            return asDict
    else:
        asDict = {}
    elems = parseFile(rib)
    cnt = 0
    totalElems = len(elems)
    for elem in elems:
        print(f"parsing {cnt}/{totalElems}")
        cnt +=1
        # print(elem)
        peer_asn = elem['peer_asn']
        # print(peer_asn, type(peer_asn))
        peer_ip = elem['peer_ip']
        originAsns = elem['origin_asns']
        #handle multi-home with a for loop 
        for originAsn in originAsns:
            try:
                peerAsnLoc = asDict[peer_asn]
            except Exception as e:
                asDict[peer_asn] = {}
                peerAsnLoc = asDict[peer_asn]
                print("exception: ", e)
                pass
            # print(peerAsnLoc)
            try:
                peerIpLoc = peerAsnLoc[peer_ip]
            except Exception as e:
                print('exception second loc ',e)
                peerAsnLoc[peer_ip] = {}
                peerIpLoc = peerAsnLoc[peer_ip]
            # print(peerIpLoc)
            try:
                originAsnLoc=peerIpLoc[originAsn]
            except Exception as e:
                print('exception in 3',e)
                peerIpLoc[originAsn] = []
                originAsnLoc = peerIpLoc[originAsn]
            originAsnLoc.append(elem)
        
            # print('orign asn loc',originAsnLoc)
            
            # print('~~~~~~~~~~~~~~~~~~~~')
        #save the file 
        # pickle.dump(open(filepath,'wb'))
    # print('~~~~~~~~~~~~~~~~~~~~')
    # # print('asdict: ' , asDict)
    # for peerAsn in asDict:
    #     for peerIp in asDict[peerAsn]:
    #         for originAsn in asDict[peerAsn][peerIp]:
    #             print('ELEMS!')
    #             print(asDict[peerAsn][peerIp][originAsn])
    # print('~~~~~~~~~~~~~~~~~~~~')
    # with open ('asDictTest.txt','w') as f:
    #     # f.write(str(asDict))
    #     for peerAsn in asDict:
    #         for peerIp in asDict[peerAsn]:
    #             f.write(str(asDict[peerAsn][peerIp]))
    #             f.write("\n")
                # for originAsn in asDict[peerAsn][peerIp]:
                #     # print('ELEMS!')
                #     for elem in asDict[peerAsn][peerIp][originAsn]:
                        
                #         f.write(str(elem))
                #         f.write("\n")
    # print(asDict)
        # return
        # asDict[peer_asn] = {peer_ip: {originAsn:[elem]}}
createRibsDict(ribs[0])
        
# {collector: [{ asn of collector peer : {ip of collector peer  : [ {origin_asn of update: [updates] } ] }} ] }

# print("~~~~~")
# for rib in updates:
#     collector = rib.collector_id
#     print(collector)

# print(ribs[0])
# print('updates',len(updates))
# print(updates[0])
# print('unk',len(unk))
# if len(unk) > 0:
#     print(unk[0])

# {collector: [{ asn of collector peer : {ip of collector peer  : [ {origin_asn of update: [updates] } ] }} ] }
# parseFile(ribs[0])
# print('~~~~~~')
# parseFile(updates[0])
# print("parser got dir")
# elems = parser.parse_all()
# for elem in elems:
#     print(elem)

# # elems = parser.parse_all()
# # print('parser done parsing')
# import pickle 
# # pickle.dump(elems,open('pickles/elemsTest','wb'))
# # elems = pickle.load(open('pickles/elemsTest','rb'))
# # print("done? loading")
# # for elem in elems:
#     # print(elem)

# print("DONE!")
# import requests
# def getRIS():
#     #LOOK AT JUST FILTERING BY IP IN PARSER DEEEERP
#     url = "https://stat.ripe.net/data/rrc-info/data.json"
#     ips = []
#     resp = requests.get(url)
#     json = resp.json()
#     data = json['data']
#     for rrc in data['rrcs']:
#         for peer in rrc['peers']:
#             ip = peer['ip'].strip()
#             ips.append(ip)
#     return ips
#             # for elem in elems:
#             #     peer = elem['peer_ip'].strip()
#             #     if ip == peer:
#             #         print("THESE ARE EQUAL")
#             #         print('ip:',ip, type(ip),' peer',peer,type(peer))
#             #         print(elem)
#             #         return 1
#             # if ip in 
#             # print(ip)

# #get RIS peer IP addresses
# ips = getRIS()
# #convert it to a string for use in filters
# s = ', '.join(str(x) for x in ips)



# filters = {"peer_ips": s}
# parser = bgpkit.Parser(url=url,cache_dir="cache",filters=filters)
# print("parser got dir")
# elems = parser.parse_all()
# #general dictionary structure
# #{collector: [{ asn : {ip : [updates] }} ] }
#victims = {collector: [{ asn : {ip : [updates] }} ] }
#hijackers = {collector: [{ asn : {ip : [updates] }} ] }
# #for victimCollector in victims:
    #for asn in victimCollectors:
        #for ip in asn

    # for hijackerCollector in hijackers
        #
# def compareHijackingUpdate(victimUpdate,hijackerUpdate, policy?):
#     return True/False
#     pass
#ew this one but yeah
# {collector: [{ asn of collector peer : {ip of collector peer  : [ {origin_asn of update: [updates] } ] }} ] }
# #{RIS IP: {origin ASN: [updates]}}
# #{RIS IP: {origin ASN: {timeStamp : [updates]}}}
# #allow updates within +- 3 minutes of this timestamp
# #altern
# #so now the loop is 
# #for observer in RIS IP:
#     #for Hijacker in originASN
#         #find updates that occure around a similar time
#         #for Victim in originASN
#             #if victim_asn == hijacker_asn pass
#             #perform hijacking(v,h)
# for elem in elems:
#     print(elem)

# def getAllUpdateFilesForTimeRange(tStart,tEnd,pageSize = 1000):
#     #need a way to sort by monitor
#     broker = bgpkit.Broker(page_size=pageSize)
#     dataUrls = []
#     items = broker.query(ts_start=tStart, ts_end=tEnd)
#     for item in items:
#         print(item.url)
#         dataUrls.append(item.url)
#     print(len(items))
#     return dataUrls


# #in case we need to do a whois query 
## import os 

## cmd = 'whois -h whois.radb.net AS131477'
## obj = os.popen(cmd)
## print(obj.read())

