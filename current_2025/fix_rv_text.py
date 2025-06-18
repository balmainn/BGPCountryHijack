def fix_rvtext():
    header = "ROUTEVIEWS COLLECTOR | AS NUMBER | PEERING ADDRESS |  PREFIXES | CC | REGION  | ASNAME"
    allnums = set()
    with open ('route_views_editing_csv.csv','r') as f:
        with open ('route_views_peers.csv','w') as outfile:
            outfile.write(header)
            for line in f.readlines():
                parts = line.strip().replace('"','').split(',')
                newParts = [] 
                
                if len(parts[0])==0:
                    continue
                if parts[0][0] != 'r':
                    continue
                for part in parts:
                    if len(part) == 0:
                        continue 
                    else:
                        newParts.append(part)
        #        print(newParts)
                allnums.add(len(newParts))
                "ROUTEVIEWS COLLECTOR | AS NUMBER | PEERING ADDRESS |  PREFIXES | CC |"
                " REGION  | ASNAME"
                collector = newParts[0]
                ASN = newParts[1]
                peering_address = newParts[2]
                prefixes = newParts[3]
                cc = newParts[4]
                region = newParts[5]
                asname = ''
                for part in newParts[6:]:
                    if '.' in part:
                        asname = asname + part
                    else:
                        asname = asname + part+' '
                asname.strip()
                outline = f"{collector}|{ASN}|{peering_address}|{prefixes}|{cc}|{region}|{''.join(asname)}"
                print(outline)
                outfile.write(outline+'\n')

