import helpers 
import gzip 
import pickle
import os 
from multiprocessing import Pool

startTime = '2025-03-26T00:00:00' 
#startTime = '2025-03-30T00:00:00' 
endTime = '2025-03-31T00:00:00'    
testEndTime = '2025-04-01T00:00:00'
# ripe = pickle.load(open('RIPE_peers_dict.pickle','rb'))
observers = pickle.load(open('observers2.pickle','rb'))
# # # for key in observers.keys():
# # #     print(key,len(observers[key]))
# # # exit(0)
# ccdict = {}
# chosen = []
# for rrc in ripe.keys():
#     peers = ripe[rrc]['peers']
#     for peer in peers:
#         #print(peer)
#         asn = peer['asn']
#         ip = peer['ip']
#         numv4 = 0
#         numv6 =0
#         ffv4 = peer['is_full_feed_v4']
#         ffv6 = peer['is_full_feed_v6']
#         cc = peer['CC']
#         if not ffv4 and not ffv6:
#             continue
#         if peer['is_full_feed_v4']:
#             numv4 = peer['v4_prefix_count']
#         if peer['is_full_feed_v6']:
#             numv6 = peer['v6_prefix_count']
#         if cc not in ccdict:
#             ccdict[cc] = []
#         ccdict[cc].append(peer)
    
# # # for cc in ccdict:
# # #     # print(cc)
# # #     # continue
# # # exit(0)
# # for _ in range(50):    
#     newlist = []
#     cclen = len(ccdict[cc])
#     #print(cc,cclen)
#     # if cclen ==1:
#     #     #nothing to sort just add
#     #     continue
#     peers = sorted(ccdict[cc], key=lambda x: (x['v4_prefix_count'],x['v6_prefix_count']),reverse=True)
#     chosen.append(peers[0])
#     if cclen > 10:
#         chosen.append(peers[1])
#         chosen.append(peers[2])
#     # if cc == 'US':
#     #     chosen.append(peers[2])
# print(len(chosen))    
# # for cc in ccdict:
# #     print(cc)
# #     print(ccdict[cc])
# #     break
# # #     print("~~~")


# observers = pickle.load(open('observers.pickle','rb'))
# print(chosen[0])
# print(len(observers['ripe']),observers['ripe'][0])
# found_list = []
# for chosen_peer in chosen:
#     chosen_asn = chosen_peer['asn']
#     chosen_ip = chosen_peer['ip']
#     found =False
#     for observer in observers['ripe']:
#         rrc,asn,ip = observer
#         if chosen_asn == asn and chosen_ip==ip:
#             # print(chosen_peer,'is',rrc)
#             found_list.append(observer)
#             # found = True
#             # exit(0)
#     if not found:
#         continue
#         print('could not find',chosen_peer)
# print(len(found_list))   
# observers['ripe'] = found_list
# for key in observers:
#     print(key,len(observers[key]))
# # pickle.dump(observers,open('observers.pickle','wb'))    
# # # for c in chosen:
# # #     print(c)
# exit(0)  
# #     #print()
# #     #print(ripe[rrc]['multihop'])
# #     #exit(9)
# # #exit(0)
# # #observers = pickle.load(open('observers.pickle','rb'))

# # exit(0)



# #collector,asn,ip = observers['ripe'][3] #orig test
# #observerids=[3,8] 
# #10 wont work on 5 day
# #neither will 11-13, but 14,15 are fine

# ids = []
# ripeRV = 'ripe'
# for id in range(len(observers[ripeRV])):
#      ids.append(id)
# print(len(ids))
#exit(0)

#print(ids)     
#ids=[20,21,22,23]
#print(observers[ripeRV][0])
#print(observers['ripe'][0])
#print(len(observers['rv']))
# rd = pickle.load(open('RV_.pickle','rb'))
# for peer in rd['RRC00']['peers']:
#     print(peer['asn'],peer['ip'])
# print(observers['ripe'][0])    
#print()
# exit(0)
# num_procs = 1
# ids = [44,42] #44 is HUUUUUGE
# ids = [42] #42 is bugged
def parse_file(ripeRV,collector,asn,ip):
    broker = helpers.createBroker()
    if ripeRV =='rv':
        if isinstance(asn,str):
            asn = int(float(asn))
        filepath = f'/mnt/research/pickles_2025/main_test/{collector}-{asn}-{ip}.pickle'
    else:
        #collector,asn,ip = observers[ripeRV]    
        filepath = f'/mnt/research/pickles_2025/all_ripe/{collector}-{asn}-{ip}.pickle'
    
    if os.path.exists(filepath):
        print(collector,asn,ip,'already exists, skipping ...')
        return
    else:
        print('aight lets go')
    # else:
    #     print(id,'does not exist')
    #     return
    print(collector,asn,ip)
    items = helpers.queryBroker(broker,startTime,endTime,collector,'updates')

    params = helpers.addFiltersNotPrefix(peer_ip=ip,peer_asn=str(asn))
    neighbor_dict = {}

    for item in items:
        parser = helpers.parseFileWithParams(item,params)
        if parser == None:
            for _ in range(5):
                print("error in parser? ")
            return#exit(0)
        try:
            for elem in parser:

                prefix = elem['prefix']
                update_type = elem['elem_type']
                as_path = elem['as_path']
                origin_type = elem['origin']
                timestamp = elem['timestamp']
                if prefix not in neighbor_dict:
                    neighbor_dict[prefix] = []
                neighbor_dict[prefix].append((update_type,as_path,origin_type,timestamp))    
        except:
            print('error detected')
            return
    print('dumping...')
    with gzip.open(filepath,'wb') as f:
        pickle.dump(neighbor_dict,f)
    return
    #pickle.dump(neighbor_dict,open(filepath,'wb'))
#num_procs = 3
todo = [] 
for ctype in observers.keys():
    peers = observers[ctype]
    for peer in peers:
        collector,asn,ip = peer
        if 'route' not in collector:
            continue
        if collector == 'rrc24':
            continue
        if ip =='45.6.54.203' or ip=='2a00:1ca8:2a::e0' or ip =='195.239.77.236':
            
            print("skipping long one")
            continue
        #todo.append((ctype,collector,asn,ip))
        if ctype =='rv':
            if isinstance(asn,str):
                asn = int(float(asn))
            filepath = f'/mnt/research/pickles_2025/main_test/{collector}-{asn}-{ip}.pickle'
        else:
            #collector,asn,ip = observers[ripeRV]    
            filepath = f'/mnt/research/pickles_2025/all_ripe/{collector}-{asn}-{ip}.pickle'
        
        if os.path.exists(filepath):
            #print(collector,asn,ip,'already exists, skipping ...')
            continue
            #return
        print((ctype,collector,asn,ip))
 #       todo.append(asn)
#print(len(todo))        
        parse_file(ctype,collector,asn,ip)
#pool = Pool(processes=num_procs)
#pool.starmap(parse_file,todo)
