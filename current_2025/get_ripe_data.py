import pickle 
import helpers

# for key in rrcdict.keys():
#     print(key)
#     for item in rrcdict[key]:
#         for peer in rrcdict[key]['peers']:
#             asn = peer['asn']
#             peer_ip = peer['ip']
#             print(asn,peer_ip)
        #break
#RRC26 15802 185.1.8.1
# endTime = helpers.addTime(startTime,minutesToAdd=fileDelta*(run+1))#30,15 doesnt work


#collector = 'route-views.napafrica'
def do_rv(rv_collector, startTime,endTime):
            broker = helpers.createBroker()
    
    #        asn = parts[2]
    #        ip_addr = parts[3]
    #        print(rv_collector,asn,ip_addr)
            items = broker.query(startTime,endTime,rv_collector,data_type='update')
            num_elems = 0
            for item in items:
                #print(item)
                
                parser = helpers.parseFile(item)
                for elem in parser:
                    print(elem)
                    num_elems+=1
                    break
            #print(item)
            print(num_elems)
            input()

def do_ripe(collector, startTime,endTime):
        broker = helpers.createBroker()
    
    #for c in rrcdict.keys():
     #   collector = c.lower()
        print(collector)
        items = broker.query(startTime,endTime,collector,data_type='update')
        num_elems = 0
        for item in items:
            print(item)
            parser = helpers.parseFile(item)
            
            for elem in parser:
                num_elems+=1
                #print(elem)
                break
            #print(item)
        print(num_elems)
        input()
startTime = '2025-03-01T00:00:00' 
endTime = '2025-03-31T00:00:00'   
#do_ripe(startTime,endTime)
from multiprocessing import Pool 
pool = Pool(processes=3)
args = []
with open('top_rv_selected','r') as f:
    f.readline() #skip header
    for line in f.readlines():
        if not line:
            print('found eof')
            break
        parts = line.strip().split(',')        
        rv_collector = parts[1].replace('.routeviews.org','')
        args.append((rv_collector,startTime,endTime))
# rrcdict = pickle.load(open('RIPE_peers_dict.pickle','rb'))
# for rrc in rrcdict.keys():
#     args.append((rrc.lower(),startTime,endTime))
# rrcdict = {}
#pool.starmap(do_ripe,args)
# for arg in args:
#     do_rv(*arg)
print(len(args))
#pool.starmap(do_rv,args)
#pool.close()
#do_rv(startTime,endTime)
#filters = helpers.addFiltersNotPrefix(peer_ip=observerIP,type='all')    

#~~~~~~~~create observer dict ~~~~~~~~~
exit(0)
observers = {'ripe':[],'rv':[]}

rrcdict = pickle.load(open('RIPE_peers_dict.pickle','rb'))
for key in rrcdict.keys():
    print(key)
    for item in rrcdict[key]:
        for peer in rrcdict[key]['peers']:
            asn = peer['asn']
            peer_ip = peer['ip']
            print(asn,peer_ip)
            observers['ripe'].append((key.lower(),asn,peer_ip))
print(observers)
with open('top_rv_selected','r') as f:
    f.readline() #skip header
    for line in f.readlines():
        parts = line.strip().split(',')        
        rv_collector = parts[1].replace('.routeviews.org','')
        asn = parts[2]
        ip_addr = parts[3]
        observers['rv'].append((rv_collector,asn,ip_addr))
print(observers)        
pickle.dump(observers,open('observers.pickle','wb'))
