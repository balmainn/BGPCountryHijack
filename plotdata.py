# import matplotlib as plt
from matplotlib import pyplot

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
    
import networkx
def countData(asGraph:networkx.Graph):
    lv1 = 0
    lv2 =0
    lv3 = 0
    for node in asGraph.nodes:
        nodeData = asGraph.nodes.get(node)
        if nodeData['linkLevel'] ==1:
            lv1+=1    
        if nodeData['linkLevel'] ==2:
            lv2+=1
        if nodeData['linkLevel'] ==3:
            lv3+=1
    print("lv1 ", lv1, "lv2,",lv2, "lv3, ",lv3, "sum ",lv1+lv2+lv3)
    return lv1, lv2, lv3
 
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
queryTime = "2024-03-01T09:00:00"
import pickle 
def getNeighbor(asn,query_time):
    """find the neighbors of a given ASN
    returns a set to remove duplicates
    """

    #if we already ran the query, dont do it again, just return what we have from file.
    safeTime=query_time.replace(":",'-')
    if os.path.exists(f'pickles/neighbors/{asn}-{safeTime}'):
        neighbors = pickle.load(open(f'pickles/neighbors/{asn}-{safeTime}','rb'))
        return neighbors
for file in datafiles: 
    plt = pyplot
    plt.subplot(3,4,count)
    
    x = []
    y = []
    coords = []
    colors = []
    info = {}
    info = readfile(file)
    x,y,colors = extractData(info,x,y,colors)
    a = file.find('-')
    b = file.find('.')
    graphPath = 'pickles/asGraph-'+file[a+1:b]+'.pickle'
    asGraph = pickle.load(open(graphPath,'rb'))
    lv1, lv2, lv3 = countData(asGraph)
    title = 'AS '+file[a+1:b]# + " n1= " +str(lv1)+ " n2= " +str(lv2)+ " n3= " +str(lv3)
    color = 'maroon'
    width = 3
    plt.axvline(lv1,0,max(y),c=color,linewidth=width)
    # plt.annotate(str(lv1), xy=(lv1, -1))
    plt.axvline(lv2,0,max(y),c=color,linewidth=width)
    # plt.annotate(str(lv2), xy=(lv2, -1))
    #plt.axvline(lv3,0,10,c='lavenderblush')
    plt.title(title)
    plt.xlabel('Hijacker Neighbors')
    plt.ylabel('Count')
    plt.scatter(x,y,c=colors)
    #plt.axvline(xpoint,ymin,ymax,c='red')
    plt.grid()
    # print(len(x))
    count+=1
    plt.savefig(f'imgs/{file[a+1:b]}-picture.png')
    plt.clf()

plt.subplot_tool()    
plt.show()
# plt.show()
    # ax.scatter(x,y,c=colors)

# plt.show()    
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
#~~~~uo asn~~~~
#these are multihomed so lets plot them together 
# files = ['hijackingScores-3582.csv', 'hijackingScores-198949.csv']
# count=1
# for file in files: 

#     plt.subplot(2,1,count)
   
#     x = []
#     y = []
#     coords = []
#     colors = []
#     info = {}
#     info = readfile(file)
#     x,y,colors = extractData(info,x,y,colors)
#     a = file.find('-')
#     b = file.find('.')
#     title = file[a+1:b]

#     plt.title(title)
#     plt.scatter(x,y,c=colors)
#     plt.grid()
#     # print(len(x))
#     count+=1
    
# plt.show()

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