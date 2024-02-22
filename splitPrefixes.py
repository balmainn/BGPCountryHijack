from netaddr import IPNetwork, cidr_merge, cidr_exclude
# cidr = '192.168.0.1/24'

# network = set(IPNetwork(prefix))
# print(network.)
# subnets = list(network.subnet(prefix, count=count))
# print(subnets)

from ipaddress import ip_network,ip_address,IPv4Address



# network = ip_network('192.168.0.1/24')
# addr = ip_address('192.168.0.1')
# v4addr = IPv4Address('192.168.0.1')
# netAddr = network.network_address
# # hosts = list(network.hosts())
# #need to find all network addresses for a subnet
# # numHosts = len(hosts)
# # host = str(hosts[0])+'/'+str(cidr) #j
# print(netAddr)



import ipcalc
#technically we are given the network address on query, but just in case, find it anyway.
def findPossibleSubnets(addr,cidr,isIPv4=True):
    """find maximum number of subnets of the same type for a given address and cidr prefix
    addr: an ipv4 address"""
    subnetDict = {}
    net = ipcalc.Network(addr+'/'+cidr)
    
    if isIPv4:
        network = str(net.guess_network()) #get network address from ip address and subnet
        maxCidr = 30 
        network = ip_network(network)
    else:
        maxCidr=80
        network = ip_network(net)


    print(network)
    loopRange = maxCidr-int(cidr) #count up from 0 to 30-cidr
    for i in range(loopRange+1): #+1 fix off by 1 since range is from [0,end) 
        #both of these increase by 2^n possible prefixes
        try:
            if isIPv4:
                subnets=list(network.subnets(prefixlen_diff=i))
                numSubnets = len(subnets)
            else:
                numSubnets = pow(2,i) #probably can just return this fun thing for a given thing
                subnets = [network,network]
        except Exception as e:
            print(i, "is invalid diff")
            print("error: ",e)
            continue
        
        if numSubnets == 1:
            print(subnets[0], "is the original")
            subnetDict['orignal prefix'] = str(subnets[0])
        else:
            print(numSubnets,"are possible for ",subnets[0])#, subnets[1])
            #this just grows exponentially at a rate of 2^n so....
            
        if isIPv4: 
            key = str(subnets[0]).split('/')[1]
            subnetDict[key] = numSubnets
        else:
            key = int(cidr)+i
            subnetDict[key] = numSubnets
    return subnetDict
        
# addr ='192.168.0.1'
# cidr = '24'
v6addr = '2001:67c:2e8::'
v6cidr = '48'
addr = '193.0.12.0'
cidr = '23'
subnets = findPossibleSubnets(v6addr,v6cidr,False)
print(subnets)
subnets = findPossibleSubnets(addr,cidr,True)
print(subnets)
# print(subnets)
ciders = []
for i in range(10,29):
    ciders.append(str(i))
for cidr in ciders:
    subnets: findPossibleSubnets(addr,cidr)
print(cidr, "for subnets: ",subnets)

#More-specific prefixes are chosen first, i.e., the longest mask wins, all else being equal.
        #from https://www.catchpoint.com/bgp-monitoring/bgp-path-selection
#You could say that the ‘smaller’ prefix is ‘more specific’ inside the ‘less specific’ larger prefix. Or you could say it’s a ‘longer match’ because more of the bits of the fixed part are matched.
        #from https://blog.apnic.net/2021/09/01/routing-concepts-you-may-have-forgotten-part-1-prefixes/
        #we can infer this to mean that larger cidr values are less specific and smaller cidr values are more specific 
        #ex: 192.168.0.0/24 covers 192.168.0.0 to 192.168.0.255 but 192.168.0.0/16 covers 192.168.0.0 to 192.168.255.255
            #192.168.0.0/32 covers only 192.168.0.0
        #there is only so far you can take this though since /32 on ipv4 yields no usable hosts or broadcast addresses.
        #in theory if a prefix is owned by an ASN then the ASN should also own the sub prefix as well
        #this fact is what bgp sub prefix hijacking exploits 
        

#need to use the network address, not any ip in the range
# for i in range(10):
#     #need to examine i+cidr and compare it to 32
#     network = ip_network(network) #convert string obj to ip_network obj
    
#     hosts = list(network.hosts())
#     #need to find all network addresses for a subnet
#     numHosts = len(hosts)
#     host = str(hosts[0])+'/'+str(cidr) #just take a single host, since the splitting will be the same regardless of host we select #just take a single host, since the splitting will be the same regardless of host we select
#     #it seems unlikely that an adversary or BGP will like splitting into subnets below 30
#     #but this needs verification
#     if 32-cidr-i <maxPrefixLen:
#         try:
#             somenets = list(network.subnets(prefixlen_diff=i))
#             print(len(somenets),somenets[0])
#             print(numHosts*len(somenets), "possible subnets are possible",somenets[0])
#         except:
#             print(i,'is an invald diff')