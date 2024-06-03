import pickle 
from matplotlib import pyplot


def loadCone():
    """Loads the cone dictionary
    cone[someAS] = [list of ASes in the cone]
    sCone is sorted by the number of ASes in someAS's cone
    """
    cone = pickle.load(open('pickles/asnCone.pickle','rb'))
    sCone = sorted(list(cone.items()), key=lambda a_c: len(a_c[1]),reverse=True)
    return cone,sCone

def extractData(dataDict,keyType):
    x = []
    y = []
    coords = []
    colors = []
    print("extracting data ",keyType)
    
    #(r,g,b,a)
    # random.seed(datetime.now().timestamp())
    # r = random.randint(0,100)
    value = 1#(100-r)/100
    
    colorSuccess = (0, value, 0, 1)
    
    colorPartial = (0, 0, value, 1)
    
    colorFail    = (value, 0, 0, 1)
    
    cone,sCone = loadCone()
    
    cnt=0
    for hijackerASN in dataDict:
        infoDict = dataDict[hijackerASN][keyType]
    
        # try:
        #     neighbors = len(cone[str(hijackerASN)]) #int(info[hijackerASN]['neighbors'])
        # except:
        #     #continue
        #     neighbors = 0
        neighbors = cnt
        cnt+=1
        # print(dataDict)
        # print(hijackerASN)    
        success = int(dataDict[hijackerASN][keyType]['hijackerWins'])
        partial = int(dataDict[hijackerASN][keyType]['hijackerTies'])
        failure = int(dataDict[hijackerASN][keyType]['hijackerLosses'])
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


#~~~~~~~~MAIN ~~~~~~#

#load preprocessed results 
processed = pickle.load(open('pickles/processedResults.pickle','rb'))
cone,scone = loadCone()
count = 1
#only show this many graphs
MAXGRAPHS = 3
for victim in processed:
    plt = pyplot
    count+=1
    
    #key values can be 'asPath' or 'originType', key: 'policy' is changing
    #to make it easy, you can just swap these two lines to compare results of the asPath and originType
    #x,y,colors = extractData(processed[victim],'originType')
    x,y,colors = extractData(processed[victim],'asPath')
    
    #optional print to see the values from the above function
    #for i in range(len(x[:10])):
    #    print(x[i],y[i],colors[i])

    #title of the graph
    title = f'AS {victim}'
    color = 'maroon'
    width = 3
    #vertical line denoting the cone size of the victim
    #this is probably not terribly relevent
    #not every as has a customer cone, these cause key error exceptions
    try:
        xpos = len(cone[str(victim)])
        plt.axvline(xpos,0,max(y),c=color,linewidth=width)
        print(xpos,max(y))
    except Exception as e:
        print("exception ", e)

    plt.title(title)
    plt.xlabel('Hijacker Cone Size')
    plt.ylabel('Count')
    plt.scatter(x,y,c=colors)
    plt.grid()
    #show the plot
    plt.show()
    #clear the graph so we can show the next one
    plt.clf() 
    if count > MAXGRAPHS:
        exit(0)

   