# BGPCountryHijack

# getting data 
Enter prefixes into the file prefixTestSet.txt \\
NOTE: lines that start with # will not run. This is useful for comments. 
It is reccomended to run getData.py in order to gather data BEFORE running v3.py. getData is multithreaded so it will gather data much faster than simply running v3.py. 

# seeing data 
Currently any file in the root dir that starts with hijackingScores- and ends with .csv will be collected in plotdata.py and shown as a pyplot. 
To change the number of charts on the same plot edit this line 
plt.subplot(2,3,count) on line 77. 
