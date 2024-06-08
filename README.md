# BGPCountryHijack-v2

# getting and preprocessing data 
Simply run updatesHijackingMethod.py to preprocess data for the nwax route-views collector. 

# getting results
simply run the file runHijacking.py in order to simulate a hijacking. This is a proof of concept that only works for nwax peer AS 6423.<br>
note that updatesHijackingMethod.py must be ran BEFORE this file. 

# processing results
After running updatesHijackingMethod.py, and runHijacking.py, run processResultsFromHijacking.py to process the results. 

# plotting data 
Manipulate the following variables on lines 180-185 of graphFinalClassData.py to have the results displayed or saved to disk. <br>
ALL: view all data, or data filtered down through the bgp path selection process<br>
do not touch Use_hijacker<br>
FNAME: what should the name of the file be (if we want to save the data)<br>
USEHISTO: True: shows the histogram, False: shows stacked bar<br>
SAVEDATA: should the data be saved to disk?<br>
DISPLAY: should the data be shown to the screen?<br>


