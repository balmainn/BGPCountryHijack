# import json
# import os
# import subprocess
# cmd = 'peer-stats-single-file http://archive.routeviews.org/route-views.sg/bgpdata/2022.02/RIBS/rib.20220205.1800.bz2'
# # obj = os.popen(cmd)
# # js = json.loads(obj.)
# output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
# js = json.dumps(output.stdout)
# print(js)
# # with open('peer-stats-output.json','r') as f:
# #     js = json.load(f)
#     # print(js)

import json, sys, time

output = sys.stdin
acc = '{'

def skip(output):
    while True:
        l = output.readline()
        if l.strip() != '{':
            continue
        else:
            break


skip(output)
print("starting")
for line in output.readlines():
# while True:
    l = line#output.readline()
    if l.strip() != '':
        acc += l.strip()
    try:
        o = json.loads(acc)
        print(o)
        skip(output)
        acc = '{'
    except:
        # pass
        break