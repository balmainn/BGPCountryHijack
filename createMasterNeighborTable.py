import pickle
queryTime = "2024-03-01T09:00:00"

safeTime=queryTime.replace(":",'-')
masterNeighbors = {}
import os 
files = os.listdir('pickles/neighbors/')
count = 1
for file in files:
    if count %1000==0:
        print(f"{count}/{len(files)}")
    count+=1
    neighbors = pickle.load(open(f'pickles/neighbors/{file}','rb'))
    dashPos = file.find('-')
    asn = file[:dashPos]
    # print(dashPos, asn ,file)
    masterNeighbors[asn] =  neighbors
    # print(neighbors)
pickle.dump(masterNeighbors,open('pickles/masterNeighborTable.pickle','wb'))
print(masterNeighbors)


    
    # if os.path.exists(f'pickles/neighbors/{asn}-{safeTime}'):
        
    #     return neighbors