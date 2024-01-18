import requests
import pickle

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
    print('asns: ',asns[:5])
    return countryInfo

def getASNneighbors(asn):
    """query RIPE for the neighbors for a given AS"""
    neighbors = []
    #TODO copy code over from bg project
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

#~~~~~ main ~~~~~#
codes,names = readCountryList()
# for code in codes:
#     countryInfo = getCountryASNPrefixes(code)
#     storeCountryInfo(countryInfo)
for code in codes:
    countryInfo = loadCountryInfo(code)
    if len(countryInfo['asns']) == 0:
        print(code, "does not have any ASNS!")

#needs testing    
#add an additional paramater for neighborCountries 
for country in countryInfo:
    for asn in country['asns']:
        countryInfo['asnNeighbors'] = (asn,[]) #each asn can have one or more neighbors

# countryInfo = {'code':countryCode, 'asns': asns, 'ipv4':ipv4,"ipv6":ipv6}
for code in codes:
    #get as neighbors 
    for country in countryInfo:
        #see if they are neighbors 
        #append the country's code if they are neighbors 
        pass

# for country in countryInfo:
#     countUniqueNeighbors(country)    
#     countNeighborCountrys(country)

print("~~~ DONE! ~~~")
# countryInfo = loadCountryInfo('AF')
#print(countryInfo)


# for c,n in zip(codes,names):
#     print(c," is the code for ", n)