# import matplotlib as plt
import matplotlib.pyplot as plt
def readfile(file):
    lines = []
    with open(file,'r')as f: 
        f.readline()
        for line in f.readlines():
            # print(line)
            lines.append(line)

    info = {}
    for line in lines:
        parts = line.split(',')
        # print(line)
        #hijackerASN	AVG	     success   partial	failure	linkLevel direct neighbors
        info[parts[0]]={"average":parts[1],"success":parts[2],
                        "partial":parts[3],"failure":parts[4],
                        "linkLevel":parts[5],"neighbors":parts[6]}

    return info


import random
from datetime import datetime
def extractData(info,x,y,colors):
    #(r,g,b,a)
    random.seed(datetime.now().timestamp())
    r = random.randint(0,100)
    value = 1#(100-r)/100
    
    colorSuccess = (0, value, 0, 1)
    
    colorPartial = (0, 0, value, 1)
    
    colorFail    = (value, 0, 0, 1)
    for hijackerASN in info:
        
        neighbors = int(info[hijackerASN]['neighbors'])
        success = int(info[hijackerASN]['success'])
        partial = int(info[hijackerASN]['partial'])
        failure = int(info[hijackerASN]['failure'])
        # print(f"({x1},{y1})")
        # coords.append((x1,y1))
        x.append(neighbors)
        y.append(success)
        colors.append(colorSuccess)
        x.append(neighbors)
        y.append(partial)
        colors.append(colorPartial)
        x.append(neighbors)
        y.append(failure)
        colors.append(colorFail)
    
    return x,y,colors
    

 
# ax.set_ylim(0,10)

import os 
files = os.listdir('scores/')
datafiles = []
for file in files:
    if file.startswith('hijackingScores-') and file.endswith('.csv'):
        print(file)
        datafiles.append('scores/'+file)


maxFiles = 2
# fig = plt.figure()
# plt.rcParams["figure.figsize"] = (10,6) 

count = 1
import re
for file in datafiles: 

    plt.subplot(3,3,count)
   
    x = []
    y = []
    coords = []
    colors = []
    info = {}
    info = readfile(file)
    x,y,colors = extractData(info,x,y,colors)
    a = file.find('-')
    b = file.find('.')
    title = 'AS '+file[a+1:b]

    plt.title(title)
    plt.scatter(x,y,c=colors)
    plt.grid()
    # print(len(x))
    count+=1
# plt.show()
    # ax.scatter(x,y,c=colors)

plt.show()    
# print(x,y,colors)
# for c in colors:
#     print(c)
print(len(x))
# ax.scatter(x,y,c=colors)
print(len(datafiles))

# infos = []

# print(datafiles)

# for file in datafiles:
    
#     info = readfile(file)
#     infos.append(info)

# asn = '6429'
# for info in infos:
#     if asn in info:
#         print(info[asn])
#         print("yes")
    # for hijackerASN in info:
    #     print(hijackerASN)

# plt.show()
#these are multihomed so lets plot them together 
files = ['hijackingScores-3582.csv', 'hijackingScores-198949.csv']
count=1
for file in files: 

    plt.subplot(2,1,count)
   
    x = []
    y = []
    coords = []
    colors = []
    info = {}
    info = readfile(file)
    x,y,colors = extractData(info,x,y,colors)
    a = file.find('-')
    b = file.find('.')
    title = file[a+1:b]

    plt.title(title)
    plt.scatter(x,y,c=colors)
    plt.grid()
    # print(len(x))
    count+=1
plt.show()
# xs = []
# ys = []
# colorss = []
# for file in files:
#     info = readfile(file)
#     x,y,colors = extractData(info,x,y,colors)
#     xs.append(x)
#     ys.append(y)
#     colorss.append(colors)
# x1 = [] 
# y1 = []
# color1= []
# for x in xs:
#     for a in x:
#         x1.append(a)
# for y in ys:
#     for a in y:
#         y1.append(a)
# for c in colorss:
#     for a in c:
#         color1.append(a)
# plt.scatter(x1,y1,c=color1)
# plt.show()