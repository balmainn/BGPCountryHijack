#hard coded uo prefix files
files = ['hijackingScores-3582.csv', 'hijackingScores-198949.csv']
import pickle

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

def findAvg(success, partial, failure):
    average =  (100*float(success) + 50*float(partial))/(float(success)+float(partial)+float(failure))
    print("average success: ",average, "%")
    return average

def getASFromFile(file):
    a = file.find('-')
    b = file.find('.')
    return file[a+1:b]

count = 1
for file in files: 
    plt = pyplot
    plt.subplot(2,2,count)
    
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
    #~~~~~~~~~~~~~~~~~~~~~~#
    
    prefixPAS = getASFromFile(file)
    plt = pyplot
    plt.subplot(2,2,count)
    # plt.subplot(1,4,count)
    count+=1
    info = readfile(file)
    x=[]
    y=[]
    
    averages = []
    for asn in info:
        
        average = info[asn]['average']
        success = info[asn]['success']
        partial = info[asn]['partial']
        failure = info[asn]['failure']
        linkLevel = info[asn]['linkLevel']
        neighbors = info[asn]['neighbors']
        # x.append(count)
        # y.append(float(average))
        averages.append(float(average))

    avgSorted = sorted(averages)
    colors = []
    low = 25
    med =  50
    high = 75
    for i in range(len(avgSorted)):
        x.append(i)
        if avgSorted[i] <= low:
            colors.append('red')
        if avgSorted[i] > low and avgSorted[i] <= med:
            colors.append('orange')
        if avgSorted[i] > med and avgSorted[i] < high:
            colors.append('yellow')
        if avgSorted[i] >= high:            
            colors.append('green')            
    # for i in range(len(x)):
    #     print(f"({x[i]},{y[i]})")
    num_points=len(x)
    plt.bar(x,avgSorted,color=colors)#get_color_gradient(color1, color2, num_points))
    avg = findAvg(success,partial,failure)
    plt.hlines(avg,xmin=0,xmax=max(x),linewidth=2.3)
    plt.xlabel('sorted run number')
    plt.ylabel('percent success')
    plt.grid()
    plt.title(prefixPAS)
# plt.savefig(f'imgs/scatterplots-picture.png')
    # plt.clf()
plt.subplot_tool()
plt.show()
