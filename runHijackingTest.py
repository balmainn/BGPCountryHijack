import os

#'pickles/ribData/{collectorID}-{startTime}-{endTime}.pickle
updatesFileDir = 'pickles/updateData/'
ribsFileDir = 'pickles/ribData'


updateFiles = os.listdir(updatesFileDir)
ribFiles = os.listdir(ribsFileDir)
