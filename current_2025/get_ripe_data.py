import pickle 
import helpers
chosen_rv = []
num_from_each=2
with open('route_views_peers.csv','r') as f:
  
    f.readline() #skip header
    for line in f.readlines():
        parts = line.strip().split('|')        
        rv_collector = parts[0].replace('.routeviews.org','')
        asn = parts[1]
        ip_addr = parts[2]
        num_prefixes = int(parts[3])
        cc = parts[4]
        chosen_rv.append((rv_collector,asn,ip_addr,num_prefixes,parts[4]))

rv_peers = sorted(chosen_rv,key=lambda x: (x[-2],x[-1]),reverse=True)
def select_on_cc(chosen_rv):
    ccdict = {}
    for collector, asn, peer_ip, num_prefixes, cc in chosen_rv:
        if cc not in ccdict:
            ccdict[cc] = [] 
        ccdict[cc].append((collector,asn,peer_ip,num_prefixes))
    chosen_rv = []

    for cc in ccdict:
        peers = ccdict[cc]
        sorted_peers = sorted(peers,key=lambda x: x[-1],reverse=True)
        for i in range(num_from_each):
            if i >= len(sorted_peers):
                break
            collector, asn, peer_ip, num_prefixes = sorted_peers[i]
            if num_prefixes < 2000:
                continue
            chosen_rv.append((collector, asn, peer_ip, num_prefixes))
    return chosen_rv

#print(observers['rv'])
def add_to_observers(observers,chosen_rv,ctype):
    print(len(observers[ctype]))
    for chosen in chosen_rv:
        collector, chosen_asn, chosen_ip, num_prefixes = chosen
        chosen_asn = int(chosen_asn) 
        found = False
    # print(chosen)
        for observer in observers[ctype]:
        # print('\t',observer)
            rrc,asn,ip = observer
            if isinstance(asn,str):
                asn = int(asn.replace('.0',''))
            if chosen_asn == asn and chosen_ip==ip:
                found = True
                # print('found')
                # exit(0)
                break
        if not found:
            observers[ctype].append((collector, chosen_asn, chosen_ip))

ripe_peers = []
rrcdict = pickle.load(open('RIPE_peers_dict.pickle','rb'))
for key in rrcdict.keys():
    print(key)
    for item in rrcdict[key]:
        #print(item)
        
        for peer in rrcdict[key]['peers']:
            #print(peer)
            #exit(0)
            asn = peer['asn']
            peer_ip = peer['ip']
            cc = peer['CC']
            v4_prefix_count = peer['v4_prefix_count']
            print(key.lower(),asn,peer_ip)            
            ripe_peers.append((key.lower(),asn,peer_ip,v4_prefix_count,cc))
chosen_rv = select_on_cc(rv_peers)

print(len(chosen_rv))
# print(chosen_rv)
# exit(0)
observers = pickle.load(open('observers.pickle','rb'))
print(len(observers['rv']))
add_to_observers(observers,chosen_rv,'rv')
print(len(observers['rv']))
print("~~~adding ripe~~~")
chosen_ripe = select_on_cc(ripe_peers) 
print(len(chosen_ripe))
print(len(observers['ripe']))
add_to_observers(observers,chosen_ripe,'ripe')
print(len(observers['ripe']))
pickle.dump(observers,open('observers2.pickle','wb'))
exit(0)
print(len(ripe_peers))   
        
exit(0)
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

# pickle.dump(observers,open('observers.pickle','wb'))
