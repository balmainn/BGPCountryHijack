import json
import requests
import pickle 
import pandas as pd
rrcDict = pickle.load(open('rrc_peers_dict.pickle','rb'))
ccs = set()
countryDict = {}
for rrc in rrcDict:
    newDict ={}
    for key in rrcDict[rrc].keys():
        if key == 'peers':
            continue
        newDict[key] = rrcDict[rrc][key]
    #print(newDict.keys())
    #exit(0)
    print(rrc)
    # print('geo',rrcDict[rrc]['geographical_location'])
    # print('top',rrcDict[rrc]['topological_location'])
    peers = rrcDict[rrc]['peers']
    # print('peer')
    for peer in peers:
        #print(type(peer['is_full_feed_v4']))
        if not peer['is_full_feed_v4']:
            continue
        if peer['CC'] not in countryDict:            
            countryDict[peer['CC']] = []
        countryDict[peer['CC']].append((newDict,peer))

selected = []
for country in countryDict:
    tupleList = countryDict[country]
    sortedPeers = sorted(tupleList, key=lambda x: x[1]['v4_prefix_count'],reverse=True)
    # for rrc,peer in sortedPeers:#countryDict[country]:
    #     print(country,rrc,peer)
    print(country,sortedPeers[0],sortedPeers[-1])
    select = {}
    for key in sortedPeers[0][0]:
        select[key] = sortedPeers[0][0][key]
    #for key in sortedPeers[0][1]:
    select['top_peer'] = sortedPeers[0][1]
    selected.append(select)
    select = {}
    if len(sortedPeers) > 1:
        for key in sortedPeers[1][0]:
            select[key] = sortedPeers[1][0][key]
        #for key in sortedPeers[0][1]:
        select['top_peer'] = sortedPeers[1][1]
        selected.append(select)
print(selected[0])
print(len(selected))
for item in selected:
    if ':' in item['top_peer']['ip']:
        print('badness')
        exit(0)
print('all good')
    # for rrc,peer in countryDict[country]:
    #     print(rrc,peer)
    #     break
       # continue
        #continue
#     print(country, len(countryDict[country]))
#     s +=len(countryDict[country])
# print(s)

# df = pd.DataFrame.from_dict(rrcDict)
# def find_truth(group):
#     print('examining ',group)
#     for _, row in group.iterrows():
        
#         if row['is_full_feed_v4']:
#             print(row, 'should count')
#             return row
# for rrc in df.columns:
#     peers = pd.DataFrame.from_dict(df[rrc]['peers'])
#     fullFeeders = peers.groupby('is_full_feed_v4').apply(find_truth)
#     print(fullFeeders)

#print(df['RRC00']['peers'])
#exit(0)
      
    #print(peers[0])

# url = 'https://stat.ripe.net/data/rrc-info/data.json'
# resp = requests.get(url)
# js = resp.json()
# rrcList = js['data']['rrcs']
# print(rrcList[0].keys())
    
exit(0)

#ensure our victim prefix is NOT a victim 
#js = json.load(open('ripe_peers.json','r'))
url = 'https://stat.ripe.net/data/rrc-info/data.json'
resp = requests.get(url)
js = resp.json()
rrcList = js['data']['rrcs']
#print(js['data']['rrcs'][4])
def getCountry(ip):
    url = f'https://stat.ripe.net/data/rir-geo/data.json?resource={ip}'
    resp = requests.get(url)
    js = resp.json()
    locations = set()
    for resource in js['data']['located_resources']:
        locations.add(resource['location'])
    if len(locations) == 1:
        return list(locations)[0]
    else:
        print("MORE THAN ONE LOCATION?")
        print(locations)
        exit(0)
        return locations
    print(js)
#loc = getCountry('185.1.8.250')  
#print(loc)
#exit(0)    
rrcDict = {}
for item in rrcList:
#    print(item)
    rrc =item['name']
    peers = item['peers']
    if len(peers) == 0 :
        continue
    print(rrc,len(peers))
    for peer in peers:
        ip = peer['ip']
        countryInfo = getCountry(ip)
        peer['CC'] = countryInfo
        
    if rrc not in rrcDict:
        rrcDict[rrc] = item
    #print(rrcDict[rrc]['peers'][0])
    #exit(0)
for rrc in rrcDict:
    print(rrc)
    peers = rrcDict[rrc]
    for peer in peers:
        print(peer)
        continue
import pickle 
pickle.dump(rrcDict,open('rrc_peers_dict.pickle','wb'))
print('dumped!')
exit(0)

    
# getCountry('192.65.185.157')
# for rrc in js['data']['peers']:
#     rrcList = js['data']['peers'][rrc]
#     print(len(rrcList),rrcList[0]['ip'])

# allparts = set()
# rvDict = {} 
# import pandas as pd 
# df = pd.read_csv('route_views_peers.csv',delimiter='|')
# nope = ['AS NUMBER', 'PEERING ADDRESS', 'PREFIXES', 'ASNAME']
# df.columns = df.columns.str.strip()
# for column in df.columns:
#     if column in nope:
#         continue
#     print(column)
#     print(df[column].unique(), len(df[column].unique()))
# print(df.columns)
# def get_top_valid_row(group):
#     # Sort the group by PREFIXES descending
#     sorted_group = group.sort_values(by='PREFIXES', ascending=False)
    
#     # Iterate over the rows and return the first one without ':' in PEERING ADDRESS
#     for _, row in sorted_group.iterrows():
#         if ':' not in str(row['PEERING ADDRESS']):
#             return row
#     return None

# df['PREFIXES'] = pd.to_numeric(df['PREFIXES'], errors='coerce')
# df = df.dropna(subset=['PREFIXES'])
# #top_prefixes_per_cc = df.loc[df.groupby('CC')['PREFIXES'].idxmax()]
# top_prefixes_per_cc = df.groupby('CC').apply(get_top_valid_row).reset_index(drop=True)

# #print(top_prefixes_per_cc)
# top_prefixes_per_cc.to_csv('top_rv_selected')
# #for index,row in top_prefixes_per_cc.iterrows():
#     #print(row)

# #print(df.keys())
# # with open ('route_views_peers.csv','r') as f:
# #     header = f.readline()
# #     print(header)
# #     for line in f.readlines():
# #         newParts = line.strip().split('|')
# #         collector = newParts[0]
# #         ASN = newParts[1]
# #         peering_address = newParts[2]
# #         prefixes = newParts[3]
# #         cc = newParts[4]
# #         region = newParts[5]
# #         asname = newParts[6]
# #         #print(len(newParts))
# #         allparts.add(len(newParts))
# #         if collector not in rvDict:
# #             rvDict[collector] = {}
# #         if ASN not in rvDict[collector]:
# #             rvDict[collector][ASN] = {}
# #         if peering_address not in rvDict[collector][ASN]
# #         rvDict[collector][ASN][peering_address][prefixes][cc][region] = asname
