import os 
import gzip
import pickle
import re
pref = 'pickles/test-results/'
files = os.listdir(pref)
# print(files)

def getCollector(file):
    if 'rrc' in file:
        #RE to find RIPE collectors
        collectorRE = r"rrc\d*-"
    else: #RE to find routeViews collectors
        collectorRE = r"route-(.*?-)"
    m = re.search(collectorRE,file)
    collector = m[0][:-1]
    return collector
#rrc25-8987-tid644-results-1
def getVictimASes(file):
    vicASRE = r'\[.*\]' #victim AS regular expression
    m = re.search(vicASRE,file)
    vicASes = m[0][1:-1].split(', ')
    print(vicASes)
    return vicASes

processed = {}
for file in files:
    collector = getCollector(file)
    vicASes = getVictimASes(file)
    print(file)
  
    # print(collector,vicAS)
    # try:
    #     processed[collector]={victimAS: results}
    # except:

    # if collector not in processed.keys:
    #     processed[collector] = {}
    # victimAS = getVictimAS(file)
    # if victimAS not in 
    # print(collector,victimAS)
    #try:
    with gzip.open(pref+file,'rb') as f:
        results = pickle.load(f)
    for vicAS in vicASes:
        for result in results:
            # if result['vicASN'] == vicAS:
            print(result,len(results))
            exit(0)
    exit(0)
    
#     except Exception as e:
#         print("EXCEPTION", e)
#         exit(0)

def calculatePolicyResults(defaultresult):
    pass

#cases:
# if H and V have the same sender ASN, 
#then policy defaults to path length
# import re