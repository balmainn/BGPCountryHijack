# BGPCountryHijack

# getting data 
Enter prefixes into the file prefixTestSet.txt \\
NOTE: lines that start with # will not run. This is useful for comments and only running specific prefixes.
It is reccomended to run getData.py in order to gather data BEFORE running v3.py. getData is multithreaded so it will gather data much faster than simply running v3.py. 

# Creating graph object
After running getData.py, run v3.py to produce and save the graph structure

# plotting data 
Currently any file in the scores/ directory that starts with hijackingScores- and ends with .csv will be collected in plotdata.py and shown as a scatter pyplot. \\
To change the number of charts on the same plot edit this line 
plt.subplot(3,4,count) on line 77. \\
This is also true for bardata.py, except it produces a bar graph instead. the subplot line to edit to change the number of plots on a graph is line 82 for this file. 

# University of Oregon data
plot-uo.py is hard coded to produce the graphs for university of oregon. The .csv files will need to be moved to the root directory from scores for this to work, however. 


# drawing graph data structure 
the file drawGraph.py will produce an image of the graph in a spring layout, it looks like a cloud. However, this function can take upwards of 2 hours to run, due to the size of the graphs. \\
Though it also will save the fig object as a pickle file so this should only need to happen once, unless the underlying graph structure changes. 