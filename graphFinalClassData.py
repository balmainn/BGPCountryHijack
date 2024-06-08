import pickle 
from matplotlib import pyplot as plt
import numpy as np


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
    colors = []
    print("extracting data ",keyType)
    
    #(r,g,b,a)
    # random.seed(datetime.now().timestamp())
    # r = random.randint(0,100)
    value = 1#(100-r)/100
    
    colorSuccess = (0, 1, 0, 1)
    
    colorPartial = (0, 0, 1, 1)
    
    colorFail    = (1, 0, 0, 1)
    
    cone,sCone = loadCone()
    
    cnt=0
    
    results = {'Success': [], 'Partial': [], 'Failure': []}
    
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
        if success ==0 and partial == 0 and failure ==0:
            continue
        results['Success'].append(success)
        results['Partial'].append(partial)
        results['Failure'].append(failure)
        
        # print(f"({x1},{y1})")
        # coords.append((x1,y1))
        #x.append(neighbors)
        #y.append(success)
        #colors.append(colorSuccess)
        #x.append(neighbors)
        #y.append(partial)
        #colors.append(colorPartial)
        #x.append(neighbors)
        #y.append(failure)
        #colors.append(colorFail)
        
        x.extend([neighbors]*3)
        y.extend([success, partial, failure])
        colors.extend([colorSuccess, colorPartial, colorFail])
    #handle Nonetype errors 
    if len(results['Success']) ==0 or len(results['Partial'])==0 and len(results['Failure'])==0:
        results['Success'].append(0)
        results['Partial'].append(0)
        results['Failure'].append(0)
    return x,y,colors, results

def createPlots(dataDict, victim, cone,whatKey,whatName,useHistorgram=False,saveData=False,display=True):
    x, y, colors, boxData = extractData(dataDict, whatKey)
    fig, axs = plt.subplots(1, 3, figsize=(21, 7))

    # Scatter plot on the left
    axs[0].scatter(x, y, c=colors)
    axs[0].set_title(f'Scatter Plot for AS {victim}')
    axs[0].set_xlabel('Hijacker Cone Size')
    axs[0].set_ylabel('Count')
    axs[0].grid(True)

    # Box plot on the right, hiding outliers
    # I prefer the violin plots to the box plots. It shows the outliers in a way 
    # that doesnt work with the box plots. 
    """
    boxprops = dict(linestyle='-', linewidth=2, color='k')
    whiskerprops = dict(linestyle='--', linewidth=2, color='blue')
    flierprops = {'marker': 'o', 'markersize': 0, 'markeredgewidth': 0}  # Outliers invisible
    axs[1].boxplot(
        [boxData['Success'], boxData['Partial'], boxData['Failure']],
        labels=['Success', 'Partial', 'Failure'],
        whiskerprops=whiskerprops,
        boxprops=boxprops,
        flierprops=flierprops,  # Make outliers invisible
        whis=1.5  # This controls the reach of the whiskers beyond the first and third quartiles
    )
    axs[1].set_title(f'Box Plot for AS {victim}')
    axs[1].set_xlabel('Outcome Type')
    axs[1].set_ylabel('Counts')
    axs[1].grid(True)"""
    
    #Histogram plot
    if useHistorgram:
        axs[1].hist(boxData['Success'], bins=20, color='green', edgecolor='black')
        axs[1].set_title('Histogram of Successes')
        axs[1].set_xlabel('Number of Successes')
        axs[1].set_ylabel('Frequency')
        axs[1].grid(True)

    # Stacked Bar Chart
    else:
        indices = np.arange(len(boxData['Success']))  # the x locations for the groups
        bar_width = 0.35  # the width of the bars: can also be len(x) sequence

        axs[1].bar(indices, boxData['Success'], bar_width,
                label='Successes', color='g')
        axs[1].bar(indices, boxData['Partial'], bar_width, bottom=boxData['Success'],
                label='Partials', color='b')
        axs[1].bar(indices, boxData['Failure'], bar_width, bottom=np.array(boxData['Success']) + np.array(boxData['Partial']),
                label='Failures', color='r')

        axs[1].set_title('Stacked Bar Chart of Outcomes')
        axs[1].set_xlabel('AS Index')
        axs[1].set_ylabel('Outcome Counts')
        axs[1].legend()

    #heatmap - this is not working correctly
    """
    heatmap_data = np.array([boxData['Success'], boxData['Partial'], boxData['Failure']]).T
    im = axs[2].imshow(heatmap_data, cmap='hot', interpolation='nearest')
    axs[2].set_title('Heatmap of Outcomes')
    axs[2].set_xlabel('Outcome Type')
    axs[2].set_ylabel('AS Index')
    fig.colorbar(im, ax=axs[2])"""
    print("LENBOX",len(boxData['Failure']))
    # Violin plot
    axs[2].violinplot(
        [boxData['Success'], boxData['Partial'], boxData['Failure']],
        showmeans=False,
        showmedians=True
    )
    axs[2].set_title('Violin Plot of Outcomes')
    axs[2].set_xlabel('Outcome Type')
    axs[2].set_ylabel('Counts')
    axs[2].set_xticks([1, 2, 3])
    axs[2].set_xticklabels(['Success', 'Partial', 'Failure'])

    plt.tight_layout()
    if saveData:
        plt.savefig(f'plots/{whatKey}-{whatName}-fig.png')
    if display:
        plt.show()
    



#~~~~~~~~MAIN ~~~~~~#

#load preprocessed results 
#processed = pickle.load(open('processedResults.pickle','rb'))

#change the following options to view different results
#ALL: view all data, or data filtered down through the bgp path selection process
#do not touch Use_hijacker
#FNAME: what should the name of the file be (if we want to save the data)
#USEHISTO: True: shows the histogram, False: shows stacked bar
#SAVEDATA: should the data be saved to disk?
#DISPLAY: should the data be shown to the screen?

ALL = False
USE_HIJACKER = not ALL #if this isnt set like this we get individual hijackers
FNAME='collated-stackedBars'
USEHISTO=False 
SAVEDATA = True
DISPLAY = False #show the graphs?
#data with things removed
if not ALL:
    if USE_HIJACKER:
        processed = pickle.load(open('pickles/results/normalizedVictimResults.pickle','rb'))
    else:
        processed = pickle.load(open('pickles/results/normalizedHijackerResults.pickle','rb'))
#ALL data nothing removed 
else:
    if USE_HIJACKER:
        processed = pickle.load(open('pickles/results/allHijackerResults.pickle','rb'))
    else:
        processed = pickle.load(open('pickles/results/allVictimResults.pickle','rb'))


cone,scone = loadCone()
count = 1
#only show this many graphs, since theres only 1 observer, thats all we care about.
MAXGRAPHS = 1
for victim in processed:
    #plt = pyplot
    if count > MAXGRAPHS:
        break
    print(f"Creating plots for AS {victim}")

    createPlots(processed[victim], victim, None,'policy',FNAME,useHistorgram=USEHISTO,saveData=SAVEDATA,display=DISPLAY)
    createPlots(processed[victim], victim, None,'asPath',FNAME,useHistorgram=USEHISTO,saveData=SAVEDATA,display=DISPLAY)
    createPlots(processed[victim], victim, None,'originType',FNAME,useHistorgram=USEHISTO,saveData=SAVEDATA,display=DISPLAY)
    count+=1
    
    if count > MAXGRAPHS:
        exit(0)

