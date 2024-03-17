import requests 

def getPeeringdbInfo(asn):
    url= f'https://peeringdb.com/api/net?asn={asn}'