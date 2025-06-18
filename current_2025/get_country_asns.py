import requests
import pandas 
df = pandas.read_csv('country_information.csv')
import pickle
ccs = df['alpha-2']
print(ccs)


country_dict = {}
i = 0
for country in ccs:
    if isinstance(country,float):
        country = 'NA'
    cc = country.lower()
    print(i, cc)
    i+=1
    if cc not in country_dict:
        country_dict[cc] = {}
#url =f'https://stat.ripe.net/data/country-asns/data.json?resource={cc}&lod=1&query_time=2025-03-31T00:00:00'
    url =f'https://stat.ripe.net/data/country-resource-list/data.json?resource={cc}&time=2025-03-31T00:00:00'
    resp = requests.get(url)
    js = resp.json() 
    asns = js['data']['resources']['asn']
    ipv4 = js['data']['resources']['ipv4']
    ipv6 = js['data']['resources']['ipv6']
    country_dict[cc] = js['data']['resources']
#print(country_dict.keys(),country_dict[cc].keys())
    print(len(asns),len(ipv4),len(ipv6))
print('dumping')
pickle.dump(country_dict,open('country_information.pickle','wb'))