def loadASNsFromCone():
    lines = []
    with open("cone-test3.py/coneSize.txt",'r') as f:
        for line in f.readlines():    
            if not line.startswith("#"):
                splitLine = line.strip().split()
                asn = splitLine[0]
                coneSize = splitLine[1]
                if int(coneSize)>100:
                    lines.append(asn)
    print(lines)
    print(len(lines))                    
    return lines

# return lines
checkpoint = 1
for i in range(0,519):
    if checkpoint % 25 ==0 or checkpoint == 519:
        with open('checkpoint.txt','a') as f:
            f.write(f"checkpoint reached for {checkpoint}\n")
        print("checkpoint! ",checkpoint)
    checkpoint+=1