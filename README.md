# BGPCountryHijack

# getting started 
The necessary packages are defined in requirements.txt you can use the following command to install the necessary componants before running any files. <br>
pip install -r requirements.txt

# getting data 
Enter prefixes into the file prefixTestSet.txt <br>
NOTE: lines that start with # will not run. This is useful for comments and only running specific prefixes.<br>
It is reccomended to run getData.py in order to gather data BEFORE running v3.py. getData is multithreaded so it will gather data much faster than simply running v3.py. <br>
This file creates a LOT of pickle files that v3.py will use in order to create the graph. While the storage requirements are not huge (about 20MB) this is a consideration. <br>
NOTE: gathering data takes a VERY long time as it can make over 10,000 GET requests to RIPE. Be sure you have enough time before running this file. <br>
One additional consideration is that getdata.py can require, at the worst case, 32 GB of RAM. If you do not have enough RAM, just run v3.py. It will probably take twice as long, but it does not use as much RAM.

# Creating graph object
After running getData.py, run v3.py to produce and save the graph structure. <br>
NOTE: running v3.py also takes a very long time, as it has to create the graph then iterate through it twice to create the scores datafile.

# plotting data 
Currently any file in the scores/ directory that starts with hijackingScores- and ends with .csv will be collected in plotdata.py and shown as a scatter pyplot. <br>
To change the number of charts on the same plot edit this line 
plt.subplot(3,4,count) on line 77. <br>
This is also true for bardata.py, except it produces a bar graph instead. the subplot line to edit to change the number of plots on a graph is line 82 for this file. <br>
NOTE: if you run bardata.py or plotdata.py it will clobber any associated data in the imges directory! 

# University of Oregon data
plot-uo.py is hard coded to produce the graphs for university of oregon. The .csv files will need to be moved to the root directory from scores for this to work, however. 

# drawing graph data structure 
the file drawGraph.py will produce an image of the graph in a spring layout, it looks like a cloud. However, this function can take upwards of 2 hours to run, due to the size of the graphs. <br>
Though it also will save the fig object as a pickle file so this should only need to happen once, unless the underlying graph structure changes. 
