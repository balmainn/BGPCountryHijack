def policyFive():
    policy = {0:10, 1:50, 2:100, 3:300, 4:500}
    return policy

def uniformPolicy(num):
    policy = {}
    for i in range(num):
        policy[i] = i*10
    return policy

def policyUnderFive(num):
    policy = {}
    for i in range(num):
        if i ==0:
            policy[i] = 10
        else:
            policy[i] = i*100
    return policy
def getUniformPolicy(numPeers,peers):
    policyDict = {}
    for i,peer in enumerate(peers):
        policyDict[peer] = (i+1)*10
    return policyDict
import itertools
def allUniformCombinations(peers):
    numPeers = len(peers)
    localPreferenceValues = []
    for i in range(numPeers):
        localPreferenceValues.append(i%3*10)
    # allVals = []
    
    # for val1 in localPreferenceValues:
    #     innerVals = []
    #     for val2 in localPreferenceValues:
    #         innerVals.append(val2)
    #     allVals.append(innerVals)
    combs = itertools.permutations(localPreferenceValues)
    # print(len(combs))
    # for comb in combs:
    #     i +=1
        # print(comb)
    # itertools.product()
    # print(allVals)
    print(combs)
    return combs
                 


def getPolicy(peers, numPeers=None,uniform=True):
    
    if numPeers == None:
        numPeers = len(peers)
    if uniform:
        policyDict = getUniformPolicy(numPeers,peers)
        
    if numPeers == 1:
        policy='default'
        policyDict = {peers:100}
        return policyDict
    elif numPeers < 5:
        policyDict = getPolicyDict(numPeers,peers)
    
    else:
        policyDict = getPolicyDict(5,peers)
    
    return policyDict

def getPolicyDict(policy,peers,maxLocalPref=500):
    
    pol = int(policy)
    if pol <5:
        localPrefDict = policyUnderFive(pol)
    else:
        localPrefDict = policyFive()
        
    remainder = len(peers) % pol
    policyDict = {}
    if remainder == 0:#apply policy uniformly 
        for i,var in enumerate(peers):
            policyDict[var] = localPrefDict[i%pol]
            # print('even ',i)
        # print('even')
    else:
        #apply policy uniformly to everyone but those who remain
        #try each policy individually for the remainder
        # print('UNEVEN')
        for i,var in enumerate(peers[:len(peers)-remainder]):
            policyDict[var] = localPrefDict[i%pol]
            # print('uniform',i)
        for var in peers[len(peers)-remainder:]:
            allPols = []
            for i in range(pol):
                allPols.append(localPrefDict[i])
            policyDict[var] = allPols
            print(i)#everything else 
    print(policyDict)
    return policyDict

import requests
def getRipePeers():
    url = "https://stat.ripe.net/data/ris-peers/data.json"
    resp = requests.get(url)
    json = resp.json()
    peers = json['data']['peers']
    # print(peers.keys(),len(peers), len(peers.keys()))
    # peerASNS = set()
    peerDict = {}
    for peerID in peers:
        peerASNS = set()
        # print(peerID, len(peers[peerID]))
        
        for item in peers[peerID]:
            # print(item['asn'])
            peerASNS.add(item['asn'])
        peerDict[peerID] = {'numPeers': len(peerASNS), 'peers':peerASNS}
    return peerDict    
        # print(len(peerASNS))
    # print(peerDict)
# getRipePeers() 
import csv 
import json

def getRVPeers():
    with open('routeviews_peers.csv','r') as f:
        f.readline() #skip first
        lines = f.readlines()
        peerDict = {}
        for line in lines:
            parts = line.split(',')
            # print(parts)
            collector = parts[0].strip()
            asNumber = parts[1].strip()
            if collector not in peerDict:
                peerDict[collector] = set()

            peerDict[collector].add(asNumber)
        
        outDict = {}
        for peer in peerDict:
            outDict[peer] = {'numPeers': len(peerDict[peer]), 'peers':peerDict[peer]}
        return outDict
        
# getRVPeers()    
import os
import pickle
def getMasterPeers():
    if os.path.exists('pickles/masterPeers.pickle'):
        masterPeers = pickle.load(open('pickles/masterPeers.pickle','rb'))
        return masterPeers
    routeViewsPeers = getRVPeers()
    ripePeers = getRipePeers()
    masterPeers = {}
    for peer in routeViewsPeers:
        masterPeers[peer] = {'peers': routeViewsPeers[peer]['peers'],
                            'numPeers': routeViewsPeers[peer]['numPeers']}
        # print(peer, routeViewsPeers[peer]['numPeers'])
    for peer in ripePeers:
        masterPeers[peer] = {ripePeers[peer]['peers']
                            :ripePeers[peer]['numPeers']}
        # print(peer, ripePeers[peer]['numPeers'])
    # print(masterPeers)
    # pickle.dump(masterPeers, open('pickles/masterPeers.pickle','wb'))
    return masterPeers
from random import randint

def randomPolicy(peers,min,max):
    """returns a random local_preference policy for number of peers
    params: 
        peers: the list of collector peers
        min: the minimum value of the policy
        max: the maximum value of the policy
    returns:
        randPolicyDict: dictionary in the form of {peer: randomInteger} 
            where randomInteger is in the range of [min,max]
        """
    randPolicyDict = {}
    for peer in peers:
        randPolicyDict[peer] = randint(min,max)
    return randPolicyDict

# print(len(getMasterPeers()))
# masterPeers = getMasterPeers()
# for collector in masterPeers:
#     numPeers = len(masterPeers[collector]['peers'])
#     if numPeers < 10:
#         print(collector, len(masterPeers[collector]['peers']))

    
def allThumbs():
    print("┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌█████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌███████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌███┌┌┌██┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌██┌┌┌┌██┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌███┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌███┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌██┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌███┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌██┌┌┌┌┌┌████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌┌┌██┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌███┌███┌┌┌┌┌┌┌┌┌┌██┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌████████████┌┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌")
    print("┌┌████████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌")
    print("┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌█████████┌┌")
    print("███┌┌┌┌█████████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌█████┌")
    print("██┌┌┌███████┌████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌███┌")
    print("██┌┌┌┌███┌┌┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("███┌┌┌┌┌┌┌┌┌┌┌█████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("┌███┌┌┌┌┌┌┌████████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("┌┌████████████┌┌┌████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("┌███┌██████┌┌┌┌┌┌┌████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("┌███┌┌┌┌┌┌┌┌┌┌┌██████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("┌┌████┌████┌██████████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌██┌")
    print("┌┌┌████████████┌┌┌┌┌███┌┌┌┌┌┌┌┌┌┌┌┌┌███┌")
    print("┌┌┌┌██┌┌┌┌┌┌┌┌┌┌┌███████┌┌┌┌┌┌┌███████┌┌")
    print("┌┌┌┌████┌┌┌┌┌┌████████┌┌┌┌┌┌┌┌████████┌┌")
    print("┌┌┌┌┌████████████┌┌┌███┌┌┌┌┌███┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌███┌█┌█┌┌┌┌┌┌███┌┌┌███┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌███┌┌┌┌┌┌█████┌┌█████┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌██████████████████┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌██████████████┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")
    print("┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌┌")