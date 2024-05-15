import os
import gzip 
import pickle
import re 
#'pickles/ribData/{collectorID}-{startTime}-{endTime}.pickle
updatesFileDir = 'pickles/updateData/'
ribsFileDir = 'pickles/ribData/'


updateFiles = os.listdir(updatesFileDir)
ribFiles = os.listdir(ribsFileDir)

rib = ribFiles[0]
print(rib)
# with gzip.open(ribsFileDir+rib,'rb') as f:
#     r = pickle.load(f)
#     print(len(r),type(r))

def groupFiles(files):
    """groups multipart files together"""
    # file = files[0]
    # for file in files:
    file = files[0]
    collectorRE = ""
    # startTimeRE = "-2.*-2"
    bothTimesRE = "-2.*-m"
    if 'multipart' in file:
        m = re.search(bothTimesRE,file)
        print(m)
        # m =re.search('-2',file)
        span0 = m.span()[0]
        span1 = m.span()[1]
        bothTimes = file[span0+1:span1-2]
        print(bothTimes)
        parts = bothTimes.split('-')
        print(parts)
        startTime=parts[0]+parts[1]+parts[2]
        endTime=parts[3]+parts[4]+parts[5]
        print(startTime)
        print(endTime)
        # m = re.finditer('-',file)
        # for i in m :
        #     s0 = i.span()[0]
        #     s1 = i.span()[0]
        #     print(file[:s0])
        #     print(file[:s1])
        #     print(file[s0:s1])
        
        # # print(span)
        # collector = file[:span0]
        # print(collector)
        # print(file[span0:span1])
groupFiles(ribFiles)