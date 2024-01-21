import requests
import pickle
from multiprocessing import Pool #so we can do things faster

def getCountryASNPrefixes(countryCode):
    """get a country's ASNS, ipv4, and ipv6 prefixes.
    paramaters: countryCode, a 2-digit ISO-3166 country code (e.g. "at","de"...)
    returns: countryInfo = {'code':countryCode, 'asns': asns, 'ipv4':ipv4,"ipv6":ipv6}
    countryCode (see above)
    asns-> a list of asns
    ipv4 -> a list of ipv4
    ipv6 -> a list of ipv6"""

    url=f"https://stat.ripe.net/data/country-resource-list/data.json?resource={countryCode}"
    print("getting country info for : ", url)
    resp = requests.get(url)
    json = resp.json()
    asns = json['data']['resources']['asn']
    ipv4 = json['data']['resources']['ipv4']
    ipv6 = json['data']['resources']['ipv6']
    countryInfo = {'code':countryCode, 'asns': asns, 'ipv4':ipv4,"ipv6":ipv6}
    # print('asns: ',asns[:5])
    print(countryCode, "has ", len(asns), " asns in it")
    return countryInfo


def getNeighbor(asn,query_time):
    """find the neighbors of a given ASN
    returns a set to remove duplicates"""
    neighbors = set()
    url = f"https://stat.ripe.net/data/asn-neighbours/data.json?resource={asn}&query_time={query_time}&lod=1"
    print("getting neighbors for AS",asn)
    res = requests.get(url)
    try:
        json = res.json()
    except:
        return None
    # print(json)
    allneighbors = json["data"]["neighbours"]
    
    for neighbor in allneighbors:
        neighbors.add(neighbor['asn'])
    return neighbors

def readCountryList():
    """read in isocountries.csv 
    this file was exported from a table found on wikipedia 
    here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2"""

    countryCodes = []
    countryNames = []
    #technically we dont need the name, 
    #but that will be easier to read than shorthand codes for everything
    # count = 0
    with open('isocountries2.csv','r') as f:
        
        line = f.readline()#skip past the header
        lines = f.readlines()
        # print(line)
        # print(lines)
    for line in lines:
        # print("line: ",line)
        parts = line.split(',')
        # print(parts)
        name = parts[0]
        code = parts[1]                
        countryNames.append(name)
        countryCodes.append(code)
    # print(countryCodes)
    return countryCodes, countryNames

def storeCountryInfo(countryInfo):
    """stores a country's info in a pickle file for easier loading later"""
    
    countryCode = countryInfo['code']
    print(f"storing country info for {countryCode}")
    filename = f"pickles/{countryCode}-info.pickle"
    file = open(filename,'wb')
    pickle.dump(countryInfo,file)
    file.close()

def loadCountryInfo(countryCode):
    """loads a country's info from file"""
    # print(f"loading country info for {countryCode}")
    filename = f"pickles/{countryCode}-info.pickle"
    file = open(filename,'rb')
    countryInfo = pickle.load(file)
    file.close()
    return countryInfo
def getCountryName(countryCode):
    """returns a country's name from its code"""
    #TODO
    pass

def countUniqueNeighbors(country):
    """returns the number of unique countries that are peered with a given country"""
    #TODO
    pass

def countNeighborCountrys(country):
    """returns the number of countries that are peered with a given country
    each country may be counted multiple times as that represents an additional 'external' peerage link"""
    #TODO
    pass

def sortCountriesByNumASN(countriesList):
    """sort the list of dictionaries by how many ASNs they have"""
    countries = countriesList
    for i in range(len(countries)):
        for j in range(len(countries)):
            if len(countries[i]['asns']) > len(countries[j]['asns']):
                tmp = countries[i]
                countries[i] = countries[j]
                countries[j] = tmp
    # for i in range(len(countries)):
    #     print(countries[i]['code'], ' has ', len(countries[i]['asns']), 'asns')
    return countries

#this function could be handy to have if we need to find what prefixes a given ASN has under it
#beware of multihoming. the only way we'd know is if we query whois for the prefix
#for now we'll ignore it.
def getPrefixesForAsn(asn):
    """get the prefixes an ASN has under it"""
    #TODO specify start time
    #/data/announced-prefixes/data.json?resource=AS3333&starttime=2020-12-12T12:00
    url=f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    resp = requests.get(url)
    json=resp.json()
    prefixes = json['data']['prefixes']
    prefixSet = set()
    # print(prefixes)
    for prefix in prefixes:
        p = prefix['prefix']
        prefixSet.add(p)
    print(prefixSet)
    return prefixSet
#cannot query by time, so this always has to be ran for timely data
#rather than sort through all the data to figure out what neighbor AS is in which country
#just ask maxmind api
def getNeighborCountry(asns):
    """find the country a list of ASNs is in"""
    #document the api call
    #This product includes GeoLite2 data created by MaxMind, available from
    #<a href="https://www.maxmind.com">https://www.maxmind.com</a>.
    countries = []
    for asn in asns:
        url=f"https://stat.ripe.net/data/maxmind-geo-lite-announced-by-as/data.json?resource=AS{asn}"
        print('getting neighbor country url\n',url)
        resp = requests.get(url)
        json = resp.json()
        locatedResources = json["data"]["located_resources"]
        for locations in locatedResources:
            for location in locations['locations']:
                print(location)
                country = location['country']
                city = location['city']
                prefixes =location['resources'] #the prefix this as is connected to
                countries.append(country)
    return countries

def findPrefixLengthCidr(prefix):
    
    """return the cidr prefix of a given prefix"""
    
    return prefix.split('/')[1]
    
    
def cidrToInt(cidr,isIPv4):
    #TODO figure out ipv6
    #
    """convert cidr notation to the number of IPs that are possible
    only supports IPv4 for now"""
    if isIPv4:
        power = 32-int(cidr)
        print('cidr to int ipv4', power, cidr)
    else:
        power = 128-int(cidr)
        print('cidr to int ipv6', power, cidr)
        print("{:e}".format(pow(2,power)))
    
    return pow(2,power)
def findPrefixLengthInt(prefix, isIPv4=True):
    cidr = findPrefixLengthCidr(prefix)
    return cidrToInt(cidr,isIPv4)
   
    
    # 232-29
prefix1 = '2a07:8100::/29'
prefix2 = '185.152.68.0/22'
prefix3 = '192.168.0.1/24'
a = findPrefixLengthInt(prefix1,False)
print(a)

#~~~~~ main ~~~~~#
# codes,names = readCountryList()
# # for code in codes:
# #     countryInfo = getCountryASNPrefixes(code)
# #     storeCountryInfo(countryInfo)
# countries = []

# for code in codes:
#     countryInfo = loadCountryInfo(code)
#     countries.append(countryInfo)
#     if len(countryInfo['asns']) == 0:
#         print(code, "does not have any ASNS!")

# countries = sortCountriesByNumASN(countries)

# lines = []
# with open('isocountries2.csv','r') as f:
    
#     line = f.readline()#skip past the header
#     lines = f.readlines()
#     # print(line)
#     # print(lines)
# print('country code , number ASNs')
# for country in countries:
#     for line in lines:
#         # print("line: ",line)
#         parts = line.split(',')
#         # print(parts)
#         name = parts[0]
#         code = parts[1]    
#         if country['code']==code:
#             # print(name, "for country code is ", code)
#             # print(name, ':',code, ' has ', len(country['asns']), 'asns')
#             print(code, ',', len(country['asns']))

# #needs testing    
# #add an additional paramater for neighborCountries 
# for country in countryInfo:
#     for asn in country['asns']:
#         countryInfo['asnNeighbors'] = (asn,[]) #each asn can have one or more neighbors

testCountry = loadCountryInfo('VA')
queryTime = "2024-01-17T09:00:00"


# testCountry['asnNeighbors'] = []
# for asn in testCountry['asns']:
#     neighbors = getNeighbor(asn,queryTime)
#     neighborsWithName=getNeighborCountry(neighbors)
#     testCountry['asnNeighbors'].append((asn,neighbors,neighborsWithName)) #each asn can have one or more neighbors
# print(testCountry)

# pickle.dump(testCountry,open('pickles/testCountry.pickle','wb'))
testCountry = pickle.load(open('pickles/testCountry.pickle','rb'))
# print()

# for c in testCountry['asnNeighbors']:

#     neighborList = [i for i in c[2] if i != '?']  
#     neighborSet = set(c[2])
#     neighborSet.remove('?') #remove unknown connections
#     print("country ", testCountry['code'], 'as', c[0], 'has ',len(neighborList), 'connections ', len(neighborSet), 'unique country neighbor')#, type(c), c[2])
#     print(set(c[2]))



# # countryInfo = {'code':countryCode, 'asns': asns, 'ipv4':ipv4,"ipv6":ipv6}
# for code in codes:
#     #get as neighbors 
#     for country in countryInfo:
#         #see if they are neighbors 
#         #append the country's code if they are neighbors 
#         pass

# for country in countryInfo:
#     countUniqueNeighbors(country)    
#     countNeighborCountrys(country)

print("~~~ DONE! ~~~")
# countryInfo = loadCountryInfo('AF')
#print(countryInfo)


# for c,n in zip(codes,names):
#     print(c," is the code for ", n)