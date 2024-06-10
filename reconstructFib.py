import pickle
import gzip
import os 
import policies
import bgpkit
def addUpdateToFib(fib,peerIP,regASN,update):
    
    try:
        peerIpLoc = fib[peerIP]
    except Exception as e:
        # print('exception second loc ',e)
        fib[peerIP] = {}
        peerIpLoc = fib[peerIP]
    # print(peerIpLoc)
    try:
        originAsnLoc=peerIpLoc[regASN]
    except Exception as e:
        # print('exception in 3',e)
        peerIpLoc[regASN] = []
        originAsnLoc = peerIpLoc[regASN]
    originAsnLoc.append(update)

# for collector in masterPeers:
#     peers = masterPeers[collector]['peers']
#     if '14061' in peers:
#         print('collector: ',collector)
#     # continue
#     for peer in peers:
#     #     if peer not in allPeers:
#             allPeers.add(peer)
#     #     else:
#     #         print("DUPLICATE PEER FOUND",collector, peer)
# print(len(allPeers))



def parseFileWithParams(brokerItem,prefix,ribPeer_asn):
    print('parsing ',brokerItem)
    #filters = {'type':'announce','prefix':prefix,'peer_asn':str(ribPeer_asn)}   
    filters = {'type':'announce','peer_asn':str(ribPeer_asn)}   
    # filters = {'type':'announce','peer_ip':'198.32.160.170','peer_asn':str(ribPeer_asn)}   
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser
def parseFile(brokerItem):
    print('parsing ',brokerItem)
    filters = {'type':'announce'}
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache",filters=filters)      
    return parser

ribsPath = 'pickles/ribData/'
files = os.listdir(ribsPath)
specCollector = 'rrc14'
ribFiles = []
for file in files:
    if specCollector not in file:
        continue
    ribFiles.append(file)
masterPeers = policies.getMasterPeers()

# print()
# exit(0)
peers = list(masterPeers[specCollector]['peers'])
allPeers = set()

broker = bgpkit.Broker(page_size=1000)
prefix ='140.78.0.0/16'
peer_asn = 14061
tStart="2020-12-21T00:00:00"
tEnd="2020-12-21T2:00:00"
updatesList = []
collectors = ['rrc14','rrc11']
riblist = []
updatesList = []
for collector_id in collectors:
    ribs = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector_id,data_type='rib')
    updates = broker.query(ts_start=tStart, ts_end=tEnd,collector_id=collector_id,data_type='update')
    # print(collector_id,len(ribs))
    for rib in ribs:
        riblist.append(rib)
    # for update in updates:
    #     updatesList.append(update)

# print(len(updatesList))


# parser = parseFileWithParams(updatesList[0],prefix,peer_asn)
# exit(0)
# for elem in parser:
#     print(elem)

# print("parsing 1")
# parser14 = parseFileWithParams(riblist[0],prefix,peer_asn)
# # parser14 = parseFile(ribs[0])
# print("parsing 2")
# parser11 = parseFileWithParams(riblist[1],prefix,peer_asn)
# # parser11 = parseFile(ribs[1])
# cnt = 0
# # for elem in parser14:
# #     print(elem)
# # exit(0)
# skip =0
# peerIPs = set()
# for elem in parser14:
#     peerIPs.add(elem['peer_ip'])

# print(peerIPs,len(peerIPs))
# skip =0
# peerIPs = set()
# for elem in parser11:
#     peerIPs.add(elem['peer_ip'])
# print(peerIPs,len(peerIPs))
# exit(0)
# # print('~~~')
# # for elem in parser11:
# #     print(elem)
# for elem14,elem11 in zip(parser14,parser11):
#     if skip < 1:
#         skip +=1
#         continue
#     # if elem14['peer_asn'] == elem11['peer_asn']:
#     print("~~~~")
#     print(elem14)
#     print(elem11)
#     if cnt > 20:
#         exit(0)
#     cnt+=1
# exit(0)
# # for i,item in enumerate(updatesList):
def storeFib(collector,peerASN):
    print("not actually storing fib but i would if i had instructions...\n",collector,peerASN)#<TODO>
#store these as collector-peerASN fib file

for peerASN in peers:
    fib = {}
    for ribEnd in ribFiles:
        print('LOADING RIB',ribEnd)
        with gzip.open(ribsPath+ribEnd,'rb') as f:
            ribUpdates = pickle.load(f)
        try:
            for peerIP in ribUpdates[peerASN]:
                print(peerIP)
                for regASN in ribUpdates[peerASN][peerIP]:
                    print(regASN)
                    for update in ribUpdates[peerASN][peerIP][regASN]:
                       # prefix  = update['prefix']
                        addUpdateToFib(fib,peerIP,regASN,update)
                       
        except Exception as e:#ignore peers not in current rib part
            print('excception ',e)
            pass
    #collector = policies.getCollector(ribEnd)
    storeFib(specCollector,peerASN)
        