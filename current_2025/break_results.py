import pickle 
import gzip 
import helpers 
observers = pickle.load(open('observers.pickle','rb'))
observerids=[3,8,10]
newdict = {}
for id in observerids:
    broker = helpers.createBroker()
    collector,asn,ip = observers['ripe'][id]
    filepath = f'/mnt/research/pickles_2025/poster_test/{collector}-{asn}-{ip}.pickle'
    filepath2 = f'/mnt/research/pickles_2025/poster_test/{collector}-{asn}-{ip}_mar15.pickle'
    with gzip.open(filepath,'rb') as f:
        neighbor_dict = pickle.load(f)
    for prefix in neighbor_dict:
        if prefix not in newdict:
            newdict[prefix] = []
        prefixList = neighbor_dict[prefix]
        for someupdate in prefixList:
            update_type,as_path,origin_type,timestamp = someupdate
            if timestamp < 1741996800:
                continue 
            else:
                newdict[prefix].append(someupdate)
with gzip.open(filepath2,'wb') as f:
    pickle.dump(newdict,f)
        