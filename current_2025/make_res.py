import pickle 
import pandas
import matplotlib.pyplot as plt
import matplotlib.pyplot
import numpy as np
import os
import helpers

# step 1  for each hijacker find how “damaging” (hijackability success chance), they have for prefixes 0-50. 
# sum s( h1,p1,oi) where s is success chance 
# each success is over any result so 
# if h1 is successful because of as path, count it 
# if h1 Is successful because of HPP but not as_path, still count HPP result. (but don’t double count things) its just were they successful at all. 
# Success chance is then number of successes / number pf prefixes (50)


observers = pickle.load(open('observers.pickle','rb'))

# observerids = [3,8,17,20,22]#,18]
title_text_size = 42 
label_text_size = 36
legend_text_size = 36
#observerids = [22]
#observer_ID = 8
results_folder = '/mnt/research/pickles_2025/main_test/rs_ukrain_test/'
files = os.listdir(results_folder)
tfile = 'rs-rrc10-51185-217.29.66.102.pickle'#'rs-route-views4-1299-62.115.129.134.pickle'
# all_results = []
# for file in files:#[tfile]:
#     print(file)
#     if 'unknown' in file:
#         continue
#     observer = file.replace('.pickle','')
#     print('loading ',observer)
#     results = pickle.load(open(results_folder+file,'rb'))
#     for result in results:
#         if observer in result:
#                 print('already has observer?')
#                 print(observer)
#                 exit(0)
#         result['observer'] = observer
#         all_results.append(result)

# pickle.dump(all_results,open('all_results.pickle','wb'))
# exit(0)
print('loading all results')
all_results = pickle.load(open('all_results.pickle','rb'))
df = pandas.DataFrame(all_results)
print(df)
print(df.columns)
#print(df['origin_results_won'])
def is_success(origin_results_won_dict):
    #print(origin_results_won_dict)
    for key in origin_results_won_dict:
        #print(key)
        if len(origin_results_won_dict[key])>0:
            return 1
        #print(origin_results_won_dict[key],len(origin_results_won_dict[key]))
    return 0        
    exit(0)
    return int(any(len(v) > 0 for v in origin_results_won_dict.values()))

# Step 2: Apply it to create a new column
df['success'] = df['origin_results_won'].apply(is_success)
prefixes = df['prefix_hijacked'].unique()
# Step 3: Create a pivot table with hijacker_asn as rows, prefix_hijacked as columns
pivot = df.pivot_table(
    index='hijacker_asn',
    columns='prefix_hijacked',
    values='success',
    aggfunc='max',  # use max in case of duplicates: 1 means at least one success
    fill_value=0    # if a hijacker didn't try a prefix, fill with 0
)

# Step 4: Add success chance (divide number of wins by 50)
pivot['success_chance'] = pivot.sum(axis=1) / len(prefixes)#50

# Step 5: Optional – reset index to make hijacker_asn a column again
final_df = pivot.reset_index()
final_df.to_csv('first_step.csv')
print(final_df)
print(len(prefixes))
from collections import defaultdict
import pandas as pd
# Step 1: Sort by success_chance, descending for top, ascending for bottom
sorted_by_success = final_df.sort_values('success_chance', ascending=False)

# Step 2: Get top hijackers
top_hijackers = []
seen_chances = set()
for chance in sorted_by_success['success_chance'].unique():
    group = sorted_by_success[sorted_by_success['success_chance'] == chance]
    top_hijackers.append(group)
    if sum(len(g) for g in top_hijackers) >= 5:
        break
top_5_df = pd.concat(top_hijackers)

# Step 3: Get bottom hijackers
sorted_by_success_asc = final_df.sort_values('success_chance', ascending=True)
bottom_hijackers = []
for chance in sorted_by_success_asc['success_chance'].unique():
    group = sorted_by_success_asc[sorted_by_success_asc['success_chance'] == chance]
    bottom_hijackers.append(group)
    if sum(len(g) for g in bottom_hijackers) >= 5:
        break
bottom_5_df = pd.concat(bottom_hijackers)

# Step 4: Get middle hijackers (by value, not index)
# Get unique sorted list of success chances
unique_chances = sorted(final_df['success_chance'].unique())

# Find median-ish range
mid_idx = len(unique_chances) // 2

# Expand out from the middle until at least 5 hijackers are included
middle_hijackers = []
left = mid_idx
right = mid_idx + 1 if len(unique_chances) % 2 == 0 else mid_idx

while sum(len(g) for g in middle_hijackers) < 5:
    groups = []
    if left >= 0:
        val = unique_chances[left]
        groups.append(final_df[final_df['success_chance'] == val])
        left -= 1
    if right < len(unique_chances):
        val = unique_chances[right]
        groups.append(final_df[final_df['success_chance'] == val])
        right += 1
    middle_hijackers.extend(groups)

middle_5_df = pd.concat(middle_hijackers)
print('top')
print(top_5_df)
print('middle_5_df')
print(middle_5_df)
print('bottom_5_df')
print(bottom_5_df)

# Drop the 'success_chance' column to only focus on prefix results
prefix_success = pivot.drop(columns='success_chance')

# Step 1: Sum success counts for each prefix (i.e., column-wise)
prefix_success_sum = prefix_success.sum(axis=0)

# Step 2: Divide by number of hijackers to get success chance
num_hijackers = prefix_success.shape[0]
prefix_success_chance = prefix_success_sum / num_hijackers

# Step 3: Convert to DataFrame
prefix_success_df = prefix_success_chance.reset_index()
prefix_success_df.columns = ['prefix_hijacked', 'success_chance']
print(prefix_success_df)
#prefix_success_df.to_csv('by_prefix.csv')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_cdf(df, title, column_name,label):
    # Extract the relevant column
    data = df[column_name].astype(float)  # Ensure the data is in float format
    
    # Sort the data in ascending order
    sorted_data = np.sort(data)
    
    # Calculate the cumulative distribution function (CDF)
    cdf = np.linspace(0., 1., len(sorted_data))
    
    # Plot the CDF
    plt.figure(figsize=(8, 6))
    # fig,ax = plt.subplots()
    plt.plot(sorted_data, cdf, marker='.', linestyle='none',label=label)
    plt.legend()
    plt.title('CDF of ' + title)
    xmin = sorted_data[0]#min(sorted_data)
    xmax = sorted_data[-1]#max(sorted_data)
    avg = np.mean(sorted_data)
    #d = pandas.DataFrame(sorted_data)
    
    #xticks = np.arange(start=sorted_data[0], stop=sorted_data[-1] + avg, step=avg)
    if sorted_data[1] - sorted_data[0] > 0.50:
        xticks = list(np.unique(sorted_data)) #np.u #sorted_data. # list(np.linspace(xmin,xmax,10))# [x for x in range(xmin,xmax,(xmax-xmin)/10)]        
    else:
        xticks =  np.linspace(xmin,xmax,8)
        # xticks = [0.0,0.66]
        # for x in list(sorted_data):
        #     if x > 0.66 and x not in xticks:
        #         xticks.append(x)
        
    print(xticks)
        
    # if xmin not in xticks:
    #     xticks.insert(0,xmin)
    # if 1 not in xticks:
    #     xticks.append(xmax)  
    
    #xticks = [float(f"{v:.2g}") for v in xvals]
    xtlabels = [f"{tick:.3f}" for tick in xticks]
    #plt.xscale('log')
    plt.xticks(xticks,xtlabels)    
    plt.xlabel('Percentage')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()


def plot_multi_cdf(dfs, title, column_name,labels):
    # Extract the relevant column
    plt.figure(figsize=(8, 6))
    for i,df in enumerate(dfs):
        data = df[column_name].astype(float)  # Ensure the data is in float format
        
        # Sort the data in ascending order
        sorted_data = np.sort(data)
        
        # Calculate the cumulative distribution function (CDF)
        cdf = np.linspace(0., 1., len(sorted_data))
    
    # Plot the CDF
    
    # fig,ax = plt.subplots()
        plt.plot(sorted_data, cdf, marker='.', linestyle='none',label=labels[i]+' hijackers')

        
        xmin = sorted_data[0]#min(sorted_data)
        xmax = sorted_data[-1]#max(sorted_data)
        avg = np.mean(sorted_data)
        #d = pandas.DataFrame(sorted_data)
        
        #xticks = np.arange(start=sorted_data[0], stop=sorted_data[-1] + avg, step=avg)
        if sorted_data[1] - sorted_data[0] > 0.50:
            xticks = list(np.unique(sorted_data)) #np.u #sorted_data. # list(np.linspace(xmin,xmax,10))# [x for x in range(xmin,xmax,(xmax-xmin)/10)]        
        else:
            xticks =  np.linspace(xmin,xmax,8)
        # xticks = [0.0,0.66]
        # for x in list(sorted_data):
        #     if x > 0.66 and x not in xticks:
        #         xticks.append(x)
        
    #print(xticks)
        
    # if xmin not in xticks:
    #     xticks.insert(0,xmin)
    # if 1 not in xticks:
    #     xticks.append(xmax)  
    
    #xticks = [float(f"{v:.2g}") for v in xvals]
        xtlabels = [f"{tick:.3f}" for tick in xticks]
        #plt.xscale('log')
        plt.xticks(xticks,xtlabels) 
    plt.legend()
    plt.title('CDF of ' + title)   
    plt.xlabel('Percentage')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()
# print('top')
# print(top_5_df)
# print('middle_5_df')
# print(middle_5_df)
# print('bottom_5_df')
# print(bottom_5_df)

plot_multi_cdf([top_5_df,middle_5_df,bottom_5_df],'top, middle, bottom 5 hijackers success chance accross all prefixes','success_chance', ['top', 'middle', 'bottom'])
exit(0)
print(final_df.columns)
print(prefix_success_df.columns)

plot_cdf(final_df,'all hijackers success chance accross all prefixes','success_chance', 'hijacker')
plot_cdf(prefix_success_df,'success chance accross individual prefixes','success_chance','prefix') 
#exit(0)
# split by hijacker so we get h1, now i need to split again by prefix 
hijacker_dfs = {asn: group for asn, group in df.groupby('hijacker_asn')}

for df in hijacker_dfs:
    prefix_dfs = {prefix: group for prefix, group in df.groupby('prefix_hijacked')}
    print(df)
    print(hijacker_dfs[df])
    print("~~~~~")
exit(0)

all_keys = ['hijacker_asn', 'hijacker_update', 'prefix_hijacked', 'num_benign_updates', 'hijacker_path_len', 'origin_results_won', 'origin_results_lost']
