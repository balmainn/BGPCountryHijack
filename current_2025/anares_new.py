import pickle, pandas as pd, numpy as np
from matplotlib import pyplot as plt 

# import gzip 
# with gzip.open('all_hijacker_results2.pickle','rb') as f:
#     hijacker_results = pickle.load(f) 
# keys = list(hijacker_results.keys())[:20]
# partial_data = {}
# for key in keys:
#     partial_data[key] = hijacker_results[key]
# pickle.dump(partial_data,open('partial_hijacker_results.pickle','wb'))
results = pickle.load(open('partial_hijacker_results.pickle','rb'))
#print(results.keys())
#print(results['6700'][1])

#check if as path distance makes a difference 
result = results['6700'][1]
#print(result['hijacker_update']['as_path'])
#result['as_path']
#exit(0)

winning_results = result['origin_results_won']
max_inflations = [] 
for reason in winning_results:
    max_inflate = None
    print(reason)
    if reason == 'HPP' and len (winning_results[reason]) >0:
        max_inflate = 'inf'
    elif reason == 'AS_Path':
        print(winning_results[reason])
        for path in winning_results[reason]:
            path_length_hijacker = len(result['hijacker_update']['as_path'].split(' '))
            print(path)
            _, path_length_victim = path
            if path_length_hijacker < path_length_victim:
                max_inflate = path_length_victim - path_length_hijacker 
    else:
        if len (winning_results[reason]) >0:
            max_inflate = -1
    if max_inflate != None:
        max_inflations.append(max_inflate)
print(max_inflations)    