
import os 
import pickle 
from matplotlib import pyplot
import numpy as np

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

def getASFromFile(file):
    a = file.find('-')
    b = file.find('.')
    return file[a+1:b]

def sortVals(x,y):
    for i in range(len(y)):
        for j in range(len(y)):
            if float(y[j]) < float(y[i]):
                tmpy = y[i]
                y[i] = y[j]
                y[j] = tmpy
                tmpx = x[i]
                x[i] = x[j]
                x[j] = tmpx
    return x,y
def hex_to_RGB(hex_str):
    #from https://medium.com/@BrendanArtley/matplotlib-color-gradients-21374910584b
    """ #FFFFFF -> [255,255,255]"""
    #Pass 16 to the integer function for change of base
    return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]

def get_color_gradient(c1, c2, n):
    #from https://medium.com/@BrendanArtley/matplotlib-color-gradients-21374910584b
    """
    Given two hex colors, returns a color gradient
    with n colors.
    this function is not used.
    """
    assert n > 1
    c1_rgb = np.array(hex_to_RGB(c1))/255
    c2_rgb = np.array(hex_to_RGB(c2))/255
    mix_pcts = [x/(n-1) for x in range(n)]
    rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
    return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]



def findAvg(success, partial, failure):
    average =  (100*float(success) + 50*float(partial))/(float(success)+float(partial)+float(failure))
    print("average success: ",average, "%")
    return average


def loadCone():
    cone = pickle.load(open('cone-test3.py/asnCone.pickle','rb'))
    sCone = sorted(list(cone.items()), key=lambda a_c: len(a_c[1]),reverse=True)
    return cone,sCone

files = os.listdir('scores/')
datafiles = []
for file in files:
    if file.startswith('hijackingScores-') and file.endswith('.csv'):
        print(file)
        datafiles.append('scores/'+file)
count = 1
color1 = "#fa0505"
color2 = "#05fa05"

cone, sCone = loadCone()

for file in datafiles:
    
    prefixPAS = getASFromFile(file)
    plt = pyplot
    plt.subplot(1,4,count)
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
    # plt.savefig(f'imgs/{prefixPAS}-bar.png')
    plt.clf()

plt.subplot_tool()    
plt.show()
    

