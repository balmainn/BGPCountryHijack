# import bgpkit
# #general format    https://data.ris.ripe.net/rrcXX/YYYY.MM/TYPE.YYYYMMDD.HHmm.gz
# url =    "https://data.ris.ripe.net/rrc01/2024.02/updates.20240201.0000.gz"
import bgpkit
import os 
import pickle 
#save data to disk or just run tests with False
SAVEDATA = True
#NOTE THIS SAVES DUPLICATE DATA, USE SIMILAR METHOD IN fixUpdates.py TO RESOLVE IF USING AGAIN LATER 
collector = 'route-views.nwax'

#test url
#url = "https://data.ris.ripe.net/rrc01/2024.02/bview.20240201.0000.gz"

#init the broker
broker = bgpkit.Broker(page_size=1000)
dataUrls = []
#timeframe we want to test 
tStart="2024-03-31T12:00:00"
tEnd="2024-03-31T14:00:00"
#have the broker get all files for this timeframe 
items = broker.query(ts_start=tStart, ts_end=tEnd)
ribs = []
updates = []
unk = []
#seperate the ribs from the updates 
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

# collectors = set()
# for rib in ribs:
#     collector = rib.collector_id
#     collectors.add(collector)
#     print(collector)

# print(len(collectors))
# print(ribs[0])
# rib = ribs[0]
# startTime = rib.ts_start
# endTime = rib.ts_end
# print(startTime, endTime)
# print(len(ribs))
# exit(0)
# parseFile()
def parseFile(brokerItem):
    """simply parse the file and return a parser object 
    which works as an iterator over the elements (list of dictionaries)"""
    print("parsing brokered item",brokerItem)
    #'https://ris.ripe.net/dumps-per-peer-rest/prototype/rrc00/2024-05-06T22/bview-20240506T2200-2406F400000800340000000000000001.gz
    parser = bgpkit.Parser(url=brokerItem.url,cache_dir="cache")      
    # preProcessPeers()
    return parser
    elems = parser.parse_all()
    return elems
    cnt=  0
    for elem in elems:
        print(elem)
        if cnt < 10:
             cnt +=1
        else:
            return(0)

def findPickleMultipart(filepath, isRib):
    print("FINDING GREATEST PART")
    if isRib:
        path ='pickles/ribData/'
    else:
        path ='pickles/updateData/'
    
    files = os.listdir(path)
    greatestFile = 0
    hasMultipart = False
    for file in files:
        if filepath+'-multipart' in path+file:
            fileNumber = int(file[-1])
            if greatestFile <fileNumber:
                greatestFile = fileNumber
            hasMultipart = True
    
    #done this way because testing and printing, can fix later
    if hasMultipart:
        retVal = filepath+'-multipart'+str(greatestFile)
    else:
        retVal = filepath
    print(retVal)
    return retVal
        
def createRibsDict(rib,continueAddingToDict,isRib,tcount,ucount):
    """create a rib dictionary file
    params: 
    rib: pyBgpkit Broker Item
    continueAddingToDict: Bool -> whether or not to load previously saved data and append to it
    isRib: Bool -> is the rib a rib or is it an updates file?
    tcount, ucount: int -> used to print information, so we know whats going on
    """
    #<TODO> consider what happens when we have an update that already exists in the list
    print("creating rib dict for: ",rib)
    collectorID = rib.collector_id
    startTime = rib.ts_start
    endTime = rib.ts_end
    if isRib:
        starterPath = f'pickles/ribData/{collectorID}-{startTime}-{endTime}'
        filepath = findPickleMultipart(starterPath,isRib)
    else:
        starterPath = f'pickles/updateData/{collectorID}-{startTime}-{endTime}'
        filepath = findPickleMultipart(starterPath,isRib)
    print(filepath)
   
    if os.path.exists(filepath):
        asDict = pickle.load(open(filepath,'rb'))
        if not continueAddingToDict:
            return asDict
    else:
        asDict = {}
    # return
    parser = parseFile(rib)
    # return
    cnt = 1
   
    # elems = parser.parse_all()
    totalElems = "some number"
    # totalElems = len(elems)
    print(parser)
    for elem in parser:
        #every n elements, create a new dictionary to save RAM
        if cnt == 1000000: #1,000,000 -> ~ 4 GB RAM
            # 10000000
            print("RESETING DICT for memory")
            print("RESETING DICT for memory")
            print("RESETING DICT for memory")
            print("RESETING DICT for memory")
            print("RESETING DICT for memory")
            if 'multipart' in filepath:
                partNumber = int(filepath[-1])
                filepath = filepath[:-1]+str(partNumber+1)
            else:
                filepath = filepath +'-multipart1'
            if SAVEDATA:
                # print("i would save data, but its commented")
                print("saving to filepath, ",filepath)
                pickle.dump(asDict,open(filepath,'wb'))
            asDict = {}
            cnt = 0
        if cnt % 5000 == 0:
            print(f"parsing {cnt}/{totalElems} for {ucount} thread {tcount}")
        # print(elem)
        cnt +=1
        #ignore withdraw annoucements
        if elem['elem_type']=='W':
            continue
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
                # print("exception: ", e)
                pass
            # print(peerAsnLoc)
            try:
                peerIpLoc = peerAsnLoc[peer_ip]
            except Exception as e:
                # print('exception second loc ',e)
                peerAsnLoc[peer_ip] = {}
                peerIpLoc = peerAsnLoc[peer_ip]
            # print(peerIpLoc)
            try:
                originAsnLoc=peerIpLoc[originAsn]
            except Exception as e:
                # print('exception in 3',e)
                peerIpLoc[originAsn] = []
                originAsnLoc = peerIpLoc[originAsn]
            # if this is an update not a rib file
            # if not isRib:
            #     newUpdateTimestamp = elem['timestamp']
            #     for update in originAsnLoc:
            #       if newUpdateTimestamp == update['timestamp']:
            #             continue
            
            originAsnLoc.append(elem)
        #save the file 
    if SAVEDATA:
        # print("i would save data, but its commented")
        print("FINISHED!")
        print("saving to filepath, ",filepath)
        pickle.dump(asDict,open(filepath,'wb'))

# same = []            
# for rib in ribs:
#     for update in updates:
#         if rib.collector_id == update.collector_id:
#             same.append({rib.collector_id: (rib,update)})

# for s in same:
#     print(s)
# print("~~~~~~~~~~")
# rib = same[-1]['route-views.linx'][0]
# update = same[-1]['route-views.linx'][1]
# print(rib)
# print(update)

# createRibsDict(ribs[0])



# for rib in ribs:
#     createRibsDict(rib)
updateTuples = []
about = 0
actual = 0
u = ''
#NOTE
#RRC 26 is stupid slow
#do that one on its own
#investigate if its just rrc 26 (its huge)
#or if its because its the last one (its probably because its huge)
ucount = 1
tcount = 1
for update in updates:
    about = about + update.rough_size
    if actual < update.rough_size:
        actual = update.rough_size
        u = update
    if update.collector_id == collector:
        updateTuples.append((update,True,False,ucount,tcount))
        ucount+=1
        tcount+=1
ribTuples = []        
for rib in ribs:
    
    if rib.collector_id == collector:
        #print(rib)
        ribTuples.append((rib,True,True,ucount,tcount))
    # if tcount % 6 == 0:
    #     tcount = 1
    # createRibsDict(update,isRib=False)
# print(ribTuples)
def createDirectories():
    if not os.path.exists('cache'): #pybgpkit cache dir
        os.mkdir('cache')
    if not os.path.exists('pickles'):
        os.mkdir('pickles')
    if not os.path.exists('pickles/ribData'):
        os.mkdir('pickles/ribData')
    if not os.path.exists('pickles/updateData'):
        os.mkdir('pickles/updateData')
    if not os.path.exists('pickles/results'):
        os.mkdir('pickles/results')
    if not os.path.exists('pickles/neighbors'):
        os.mkdir('pickles/neighbors')
    if not os.path.exists('plots'):
        os.mkdir('plots')
        


#print(len(updateTuples), 'about: ',about, 'actual:', actual)
# print(u)
#make sure we have directory structure before writing to them
createDirectories()
from multiprocessing import Pool
pool = Pool(processes=6)
# pool.map(createRibsDict,ribs)
pool.starmap(createRibsDict,updateTuples)
pool.close()
print("updates are done!")
pool = Pool(processes=6)
pool.starmap(createRibsDict,ribTuples)
pool.close()
print("ribs are done! runhijacking.py now")        