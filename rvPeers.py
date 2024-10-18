def getRVPeers():
    peers = {}
    with open('routeviews_peers.csv','r') as f:
        f.readline()#skip header
        #ROUTEVIEWS COLLECTOR,AS NUMBER,PEERING ADDRESS,PREFIXES
        for line in f.readlines():
            parts = line.split(',')
            collector = parts[0].strip()
            asn = parts[1].strip()
            peerIP = parts[2].strip()
            numPrefixes = parts[3].strip()
            if collector not in peers:
                peers[collector] = {'ipv4':[],'ipv6':[]}
            if ':' in peerIP:
                peers[collector]['ipv6'].append((numPrefixes,asn,peerIP))
            else:
                peers[collector]['ipv4'].append((numPrefixes,asn,peerIP))
    for collector in peers:
        peers[collector]['ipv6'] = sorted(peers[collector]['ipv6'])
        peers[collector]['ipv4'] = sorted(peers[collector]['ipv4'])
    # for collector in peers:
    #     print(collector,peers[collector]['ipv4'][:5])
    return peers            
#getRVPeers()