import pickle 
import pandas
import matplotlib.pyplot as plt
import matplotlib.pyplot
import numpy as np
# url = 'https://stat.ripe.net/data/bgp-state/data.json?resource=3582&timestamp=2025-05-01T12:00'
global color_map
color_map = {
            'AS_Path': 'red',#'#d1473d',#'red',
            'time': 'orange',#'#e38c00',#'orange',
            'HPP': '#c745ff',#'#988dff',
            'Safe': 'green'#'#409d31'#'green'
        }
observers = pickle.load(open('observers.pickle','rb'))

# observerids = [3,8,17,20,22]#,18]
title_text_size = 42 
label_text_size = 36
legend_text_size = 36
#observerids = [22]
#observer_ID = 8
import os

def parse_single_result(result):
    hijacker_asn = result['hijacker_asn']
    hijacker_update = result['hijacker_update']
    hijacker_origin = result['origin']
    hijacker_prefix = result['prefix']
    hijacker_timestamp = result['timestamp']
    hijacker_origin_asns = result['origin_asns']
    hijacker_path_len = result['hijacker_path_len']
    hijacker_prefix_hijacked = result['prefix_hijacked']
    num_benign_updates= result['num_benign_updates']
    hijacker_origin_results_won = result['origin_results_won']
    hijacker_origin_results_lost = result['origin_results_lost']
    return hijacker_asn,hijacker_update,hijacker_origin,hijacker_prefix, hijacker_timestamp , hijacker_origin_asns ,hijacker_path_len ,hijacker_prefix_hijacked ,num_benign_updates,hijacker_origin_results_won,hijacker_origin_results_lost 
import helpers
def how_much_inflate(hijacker_path_len,benign_path_len):
    return benign_path_len - hijacker_path_len
def test_AS_Path_hijacking(result):
    hijacker_asn,hijacker_update,hijacker_origin,hijacker_prefix, hijacker_timestamp , hijacker_origin_asns ,hijacker_path_len ,hijacker_prefix_hijacked ,num_benign_updates,hijacker_origin_results_won,hijacker_origin_results_lost  = parse_single_result()
    #hpp_won = hijacker_origin_results_won['HPP']
    hijacker_path_len 
    as_path_results_won = hijacker_origin_results_won['AS_Path']
    for _, lost_path_len in as_path_results_won:
        max_inflate = how_much_inflate(hijacker_path_len,lost_path_len)
    #TODO

prefixes = set()      
# t = pickle.load(open('/mnt/research/pickles_2025/main_test/rs_ukrain_test/rs-rrc20-51019-185.1.167.88.pickle','rb'))
# print(t)
results_folder = '/mnt/research/pickles_2025/main_test/rs_ukrain_test/'
tfile = 'rs-rrc10-51185-217.29.66.102.pickle'#'rs-route-views4-1299-62.115.129.134.pickle'
#results = pickle.load(open(results_folder+tfile,'rb'))
#print(results[0].keys())
all_hijackers = set() 
prefixes = set()
hijacker_results = {}
files = os.listdir(results_folder)
no_path = 0 
no_hpp = 0
no_lpp = 0 
new_neighbor = 0
inconclusive=  0
#print(no_hpp,no_path,no_lpp,new_neighbor,inconclusive)
#unknown analysis 
# no_hpp 6.394010677319124
# no_path 34.89893241725376
# no_lpp 5.274070582479232
# new_neighbor 1.7004950827350522
# unknown 0.013872459885470164
aa = [42865, 233960, 35357, 11400, 93]
t = 670393
num_tested_observers = 0
num_ripe=0
num_rv = 0
for file in files:#[tfile]:
    print(file)
    if 'unknown' in file:
        continue
    if 'rrc' in file:
        num_ripe +=1
    else:
        num_rv+=1
    num_tested_observers +=1
print(num_tested_observers,num_ripe,num_rv)
exit(0)
for a in aa:
    print(a/t *100)
exit(0)
for file in files:#[tfile]:
    if 'unknown' not in file:
        continue
    observer=file.replace('rs-','').replace('.pickle','')
    print(observer)
    
    results = pickle.load(open(results_folder+file,'rb'))
    for result in results:
        #print(result['why'])
        why = result['why']
        if 'could not find HPP relation' in why:
            no_hpp +=1
        elif 'no path observer and no path hijacker' in why:
            no_path +=1
        elif 'could not find LPP relation' in why:
            no_lpp +=1
        elif 'hijacking from unknown' in why:
            new_neighbor +=1
        elif 'testing inconclusive' in why:
            inconclusive +=1
        else:
            print(result['why'])
total_updates = 0
for file in files:#[tfile]:
    if 'unknown' in file:
        continue 
    results = pickle.load(open(results_folder+file,'rb'))
    for result in results:
        num_updates = result['num_benign_updates']
        total_updates += num_updates
        #print()
        #exit(0)
print(no_hpp,no_path,no_lpp,new_neighbor,inconclusive)
print(total_updates)
exit(0)
#     for result in results: 
#        # print(result)
#         hijacker= result['hijacker_asn']
#         if hijacker not in hijacker_results.keys():
#             hijacker_results[hijacker] = []
#         hijacker_results[hijacker].append(result)
#         #exit(0)    

print('loading hijacker results combined')
import gzip 
with gzip.open('all_hijacker_results.pickle','rb') as f:
    hijacker_results = pickle.load(f)    
# import gzip 
# with gzip.open('all_hijacker_results.pickle','wb') as f:
#     pickle.dump(hijacker_results,f)
# exit(0)
by_hijacker = {}
for hijacker_asn in hijacker_results:
    

    results = hijacker_results[hijacker_asn]
    tot_wins = 0
    tot_loss = 0
    if hijacker_asn not in by_hijacker.keys():
            by_hijacker[hijacker_asn] = {}
    for result in results:
        wins = result['origin_results_won']
        loss = result['origin_results_lost']
        prefix_hijacked = result['prefix_hijacked']
        if prefix_hijacked not in by_hijacker[hijacker_asn].keys():
            by_hijacker[hijacker_asn][prefix_hijacked] = {}

        for key in wins:
            if key not in by_hijacker[hijacker_asn][prefix_hijacked].keys():
                by_hijacker[hijacker_asn][prefix_hijacked][key] = {'win':0,'loss':0}

            num_win = len(wins[key])
            num_loss = len(loss[key])
            by_hijacker[hijacker_asn][prefix_hijacked][key]['win'] += num_win
            # if num_win > 6 :
            #     print(wins[key],num_win)
            # try:
                # by_hijacker[hijacker][key]['win'] = num_win
            # except Exception as e:
            #     print(e)
            #     print(result)
            #     exit(0)
            by_hijacker[hijacker_asn][prefix_hijacked][key]['loss'] += num_loss
            total_tests = by_hijacker[hijacker_asn][prefix_hijacked][key]['win'] + by_hijacker[hijacker_asn][prefix_hijacked][key]['loss']
            if total_tests == 0 and num_win ==0:
                by_hijacker[hijacker_asn][prefix_hijacked][key]['success_ratio'] = 0
            elif total_tests == 0:
                by_hijacker[hijacker_asn][prefix_hijacked][key]['success_ratio'] = 'div_by_0'
            else:
                by_hijacker[hijacker_asn][prefix_hijacked][key]['success_ratio'] = by_hijacker[hijacker_asn][prefix_hijacked][key]['win'] /total_tests
#print(by_hijacker['6700']['188.190.224.0/19'])                
#exit(0)
def make_scatter(hijacker):
    print('making scatter')
    someres = {}
    
    for hijacker_asn in hijacker.keys():
        
        if hijacker_asn not in someres:
            someres[hijacker_asn] = {}
        for prefix_hijacked in hijacker[hijacker_asn].keys():
            for reason in hijacker[hijacker_asn][prefix_hijacked]:
                if reason not in someres[hijacker_asn]:
                    someres[hijacker_asn][reason] = {}
                for key in hijacker[hijacker_asn][prefix_hijacked][reason]:
                    if key not in someres[hijacker_asn][reason].keys():
                        someres[hijacker_asn][reason][key] = 0
                    someres[hijacker_asn][reason][key] += hijacker[hijacker_asn][prefix_hijacked][reason][key]
                    someres[hijacker_asn][reason]['success_ratio'] = 0
        
    #compute success ratios 
    for hijacker_asn in someres:
        for reason in someres[hijacker_asn]:
            num_win = someres[hijacker_asn][reason]['win']
            num_loss =  someres[hijacker_asn][reason]['loss']
            total_tests = num_win + num_loss
            if reason == 'unknown_neighbor' and total_tests > 0:
                print(hijacker[hijacker_asn])
                exit(0)
            if total_tests == 0 and num_win ==0:
                someres[hijacker_asn][reason]['success_ratio'] = 0
            elif total_tests == 0:
               someres[hijacker_asn][reason]['success_ratio'] = 'div_by_0'
            else:
                someres[hijacker_asn][reason]['success_ratio'] = num_win /total_tests
        #print(hijacker_asn,someres[hijacker_asn])
    for a in someres:
        for b in someres[a]['unknown_neighbor']:
            if someres[a]['unknown_neighbor'][b] > 0:
                print(a,someres[a])
        # for reason in someres[a].keys():
        #     if someres[a][reason]['win'] > 10:
        #         print(a,someres[a])
                exit(0)
    # print('all clear?')
    # exit(0)

    rows = []
    for asn, reasons in someres.items():  
        for reason in reasons:
            
            if all(someres[asn][reason]['win'] ==0 for reason in someres[asn]):
                continue
            
        for reason, stats in reasons.items():
            if 'unknown' in reason:
                continue
            # print(reason,stats)
            # exit(0)
            # if stats['win'] ==0:
            #     continue
            
            rows.append({
                'asn': asn,
                'reason': reason,
                'success_ratio': stats['success_ratio'],
                'win': stats['win'],
                'loss': stats['loss']
            })
    #import matplotlib.pyplot as plt
    def scatter(rows,show=0,save=0):
        df = pandas.DataFrame(rows)
        plt.figure(figsize=(12, 6))

        # One point per (ASN, reason), color-coded by reason
        for reason, group in df.groupby('reason'):
            if reason == 'default':
                continue
            plt.scatter(group['asn'], group['success_ratio'], label=reason, alpha=0.8)

        plt.xlabel("Hijacker ASN")
        plt.ylabel("Success Ratio")
        plt.title("Success Ratio by ASN and Reason")
        plt.xticks(rotation=90)
        plt.yticks([0,0.05,0.1,0.2,0.4,0.6,0.8,1])
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(title="Reason")
        plt.tight_layout()
        if show:
            plt.show()
        if save:
            plt.savefig('single_scatter.png')

            
    def scatter_multiple(rows,show=0,save=0):
        to_rem = []
        asns = set()
        for somedict in rows:
            asns.add(hijacker_asn)
            if somedict['win'] ==0:
                to_rem.append(somedict)
        for r in to_rem:
            rows.remove(r)
        asns = sorted(list(asns))
        mapping = {}
        for i in range(len(asns)):
            mapping[asns[i]] = i
        #exit(0)
        df = pandas.DataFrame(rows)
        
        plt.figure(figsize=(12, 6))

        # Get unique reasons and determine subplot layout
        reasons = sorted(df['reason'].unique())
        n = len(reasons)
        cols = 3  # Number of columns in grid
        rows = (n + cols - 1) // cols  # Compute rows needed

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=False, sharey=True)
        axes = axes.flatten()  # Make 1D for easy indexing

        for i, reason in enumerate(reasons):
            ax = axes[i]
            subset = df[df['reason'] == reason]
            ax.scatter(subset['asn'], subset['success_ratio'], alpha=0.8)
            #ax.scatter(as, subset['success_ratio'], alpha=0.8)
            ax.set_title(reason)
            ax.set_xlabel("ASN")
            ax.set_ylabel("Success Ratio")
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.tick_params(axis='x', labelrotation=90)

        # Hide unused subplots if any
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle("Success Ratio by Hijacker ASN (One Plot per Reason)", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        if show:
            plt.show()
        if save:
            plt.savefig('single_multi.png')
    
    cdf_data = []
    df = pandas.DataFrame(rows)
    for reason, group in df.groupby('reason'):
        # Only keep non-zero or meaningful values if desired
        success_ratios = group['success_ratio'].values
        # if len(success_ratios) == 0:
        #     continue
        sorted_vals = np.sort(success_ratios)
        n = len(sorted_vals)

        for i, val in enumerate(sorted_vals):
            cdf_data.append({
                'reason': reason,
                'success_ratio': val,
                'cdf': (i + 1) / n
            })
    cdf_df = pandas.DataFrame(cdf_data)
        # Determine subplot layout
    
    def cdf_multi(cdf_df,show=0,save=0):
        reasons = sorted(cdf_df['reason'].unique())
        cols = 3
        rows = (len(reasons) + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=True, sharey=True)
        axes = axes.flatten()

        for i, reason in enumerate(reasons):
            ax = axes[i]
            group = cdf_df[cdf_df['reason'] == reason]
            ax.step(group['success_ratio'], group['cdf'], where='post', label=reason)
            ax.set_title(reason)
            ax.set_xlabel("Success Ratio")
            ax.set_ylabel("CDF")
            ax.grid(True, linestyle='--', alpha=0.5)

        # Remove unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle("CDF of Success Ratios per Reason", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        if show:
            plt.show()
        if save:
            plt.savefig('cdf_multi.png')
    
    # Initialize the plot
    
    def cdf(df,show=0,save=0):
        print('making cdf')
        plt.figure(figsize=(10, 6))

        # Compute and plot CDFs for each reason
        for reason, group in df.groupby('reason'):
            if reason == 'time':
                continue
            success_ratios = group['success_ratio'].values
            #success_ratios = success_ratios[(success_ratios > 0) & (success_ratios <= 1)]  # Optional filtering

            if len(success_ratios) == 0:
                continue

            sorted_vals = np.sort(success_ratios)
            cdf_vals = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)

            plt.step(sorted_vals, cdf_vals, where='post', label=reason)

        # Customize the plot
        plt.xlabel("Success Ratio")
        plt.ylabel("CDF")
        plt.title("CDF of Success Ratios by Reason")
        plt.grid(True)
        plt.yticks([0, 0.1, 0.2, 0.5, 0.8, 1])
        plt.legend(title="Reason")
        if show:
            plt.show()
        if save:
            plt.savefig('cdf.png')
    def kde_func(df,show=0,save=0):
        from scipy.stats import gaussian_kde
        import numpy as np

        # Get success ratios for a reason
        vals = df[df['reason'] == 'HPP']['success_ratio'].values
        vals = vals[vals > 0]  # Filter out zeros if desired
        vals.sort()

        # Estimate PDF via KDE
        kde = gaussian_kde(vals)
        x = np.linspace(0, 1, 1000)
        pdf = kde(x)
        cdf = np.cumsum(pdf)
        cdf = cdf / cdf[-1]  # Normalize

        # Plot
        plt.plot(x, cdf, label='Smoothed CDF (KDE)', color='red')
        plt.step(vals, np.arange(1, len(vals)+1)/len(vals), where='post', label='Empirical CDF', color='blue')
        plt.legend()
        plt.title("CDF with Smoothed Fit (HPP)")
        plt.xlabel("Success Ratio")
        plt.ylabel("CDF")
        plt.grid(True)
        if show:
            plt.show()
        if save:
            plt.savefig('kde.png')

    def kde_func_multi(df,show=0,save=0):
        from scipy.stats import gaussian_kde
        import numpy as np
        plt.figure(figsize=(12, 6))

        # Get unique reasons and determine subplot layout
        reasons = sorted(df['reason'].unique())
        n = len(reasons)
        cols = 3  # Number of columns in grid
        rows = (n + cols - 1) // cols  # Compute rows needed

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=False, sharey=True)
        axes = axes.flatten()  # Make 1D for easy indexing

        for i, reason in enumerate(reasons):
            subset = df[df['reason'] == reason]
            index = i
            # Fit a Beta distribution
            vals = subset['success_ratio'].values
        # Get success ratios for a reason
        #vals = df[df['reason'] == 'HPP']['success_ratio'].values
            vals = vals[vals > 0]  # Filter out zeros if desired
            vals.sort()

            # Estimate PDF via KDE
            try:
                kde = gaussian_kde(vals)
            except:
                continue
            ax = axes[i]
            
            x = np.linspace(0, 1, 1000)
            pdf = kde(x)
            cdf = np.cumsum(pdf)
            cdf = cdf / cdf[-1]  # Normalize
            ax.set_title(reason)
            ax.set_xlabel("Success Ratio")
            ax.set_ylabel("kde dist")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.5)
        # Plot
        #plt.plot(x, cdf, label='Smoothed CDF (KDE)', color='red')
        #plt.step(vals, np.arange(1, len(vals)+1)/len(vals), where='post', label='Empirical CDF', color='blue')
        plt.legend()
        plt.title("CDF with Smoothed Fit (HPP)")
        plt.xlabel("Success Ratio")
        plt.ylabel("CDF")
        plt.grid(True)
        if show:
            plt.show()
        if save:
            plt.savefig('kde_multi.png')

    def parametric_dist(df,show=0,save=0):
        from scipy.stats import beta
        
        # Fit a Beta distribution
        for reason in df['reason']:
            vals = df[df['reason'] == reason]['success_ratio'].values
            vals = vals[(vals > 0) & (vals < 1)]  # Remove boundaries for fitting
            #a, b, _, _ = beta.fit(vals, floc=0, fscale=1)  # Constrain to [0,1]
            try:
                a, b, loc, scale = beta.fit(vals, floc=0, fscale=1)
            except:
                continue
            x = np.linspace(0, 1, 1000)
            plt.plot(x, beta.cdf(x, a, b), label=f"Beta CDF Fit (a={a:.2f}, b={b:.2f})", color='green')
            plt.step(np.sort(vals), np.arange(1, len(vals)+1)/len(vals), where='post', label='Empirical CDF', color='blue')
        plt.legend()
        plt.title("CDF with Beta Distribution Fit (HPP)")
        plt.xlabel("Success Ratio")
        plt.ylabel("CDF")
        plt.grid(True)
        if show:
            plt.show()
        if save:
            plt.savefig('parametric_distribution.png')
    def parametric_dist_multi(df,show=0,save=0):
        print('doing parametric dist')
        from scipy.stats import beta
        plt.figure(figsize=(12, 6))

        # Get unique reasons and determine subplot layout
        reasons = sorted(df['reason'].unique())
        reasons.remove('LPP')
        n = len(reasons)
        # cols = 3  # Number of columns in grid
        # rows = (n + cols - 1) // cols  # Compute rows needed
        cols = 4
        rows = 1

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=True, sharey=True)
        axes = axes.flatten()  # Make 1D for easy indexing
        previous_index = 0
        for i, reason in enumerate(reasons):
            
            subset = df[df['reason'] == reason]
            next_index = previous_index
            # Fit a Beta distribution
            vals = subset['success_ratio'].values
            vals = vals[(vals > 0) & (vals < 1)]  # Remove boundaries for fitting
            #a, b, _, _ = beta.fit(vals, floc=0, fscale=1)  # Constrain to [0,1]
            try:
                a, b, loc, scale = beta.fit(vals, floc=0, fscale=1)
            except Exception as e:
                previous_index = previous_index - 1
                continue
            ax = axes[next_index]
            previous_index = previous_index +1
            x = np.linspace(0, 1, 1000)
            ax.plot(x, beta.cdf(x, a, b), label=f"Beta Fit (a={a:.2f}, b={b:.2f})", color='green')
            ax.step(np.sort(vals), np.arange(1, len(vals)+1)/len(vals), where='post', label='CDF', color='blue')
            ax.set_title(reason)
            ax.set_xlabel("Success Ratio")
            ax.set_ylabel("parametric dist")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.5)
        
        # axes[-1].remove()
        # axes[-1].remove()
        # plt.legend()
        # plt.title("CDF with Beta Distribution Fit")
        # plt.xlabel("Success Ratio")
        # plt.ylabel("CDF")
        # plt.grid(True)
        if show:
            plt.show()
        if save:
            plt.savefig('parametric_distribution_multi.png')
    show = True 
    save = False
    # scatter(rows,show=show,save=save)    
    # scatter_multiple(rows,show=show,save=save)        
    # cdf(cdf_df,show=show,save=save)    
    # cdf_multi(cdf_df,show=show,save=save)    
    df = pandas.DataFrame(rows)
    #kde_func(df)
    #kde_func_multi(df,show=True)
    #parametric_dist(df) #bugged
    parametric_dist_multi(df,show=show,save=save)
    
    exit(0)
    #exit(0)
                
            
            # for key in hijacker[hijacker_asn][prefix_hijacked].keys():
            #     if hijacker[hijacker_asn][prefix_hijacked][key]['win'] > 6:
            # #if any(value > 0  for value in  ):
            #         print(hijacker[hijacker_asn][prefix_hijacked])
            # # if hijacker[hijacker_asn]['HPP']['win'] > 0:
            # #     print(hijacker)
            #         exit(0)
    #print(hijacker['6700'])
make_scatter(by_hijacker)


#~~~~~~~~~~~~~~~~~ old ~~~~~~~~~~~~~~~~~
#~~~~~~~~~below here be dragons ~~~~~~~~~~~~~~~
exit(0)
for _ in range(0):
    #for result in results:
    prefix = result['prefix_hijacked']
    prefixes.add(prefix)
    
    for key in wins:
        someval = wins[key]
        #print(len(someval))
        #exit(0)
        # if len(someval) > 1:
        #     print(len(someval))
        #     print(len(loss['AS_Path']))
        #     print(someval)
        #     print(result)
        #     exit(0)
        #print(someval)
        #exit(0)
    all_hijackers.add(result['hijacker_asn'])
print(all_hijackers)
print(len(all_hijackers))
print(results[0])
for p in prefixes:
    print(p)
exit(0)
def filter_results(results,observer):
    
    by_prefixes = {'observer':observer} 
    by_hijacker_asn = {'observer':observer}
    for result in results:
        prefix = result['prefix_hijacked']
        hijacker = result['hijacker_asn']
        if prefix not in by_prefixes.keys():
            by_prefixes[prefix] = [] 
        if hijacker not in by_hijacker_asn.keys():
            by_hijacker_asn[hijacker] = [] 
        by_prefixes[prefix].append(result)
        by_hijacker_asn[hijacker].append(result)
    return by_prefixes,by_hijacker_asn 


def comp_res(results,observer):

    wins = []
    success_ratios = []

    for d in results:
        won_count = sum(len(v) for v in d['origin_results_won'].values())
        lost_count = sum(len(v) for v in d['origin_results_lost'].values())
        total = won_count + lost_count
        ratio = won_count / total if total > 0 else 0
        wins.append(won_count)
        success_ratios.append(ratio)

    # 1. Distribution of number of wins (ECDF)
    sorted_wins = np.sort(wins)
    ecdf_wins = np.arange(1, len(sorted_wins)+1) / len(sorted_wins)

    # plt.figure(figsize=(14,4))

    # plt.subplot(1,3,1)
    # plt.step(sorted_wins, ecdf_wins, where='post')
    # plt.xlabel('Number of Wins')
    # plt.ylabel('ECDF')
    # plt.title('ECDF of Number of Wins')
    # plt.grid(True)

    # 2. Distribution of success ratio (ECDF)
    sorted_ratio = np.sort(success_ratios)
    ecdf_ratio = np.arange(1, len(sorted_ratio)+1) / len(sorted_ratio)

    # plt.subplot(1,3,2)
    # plt.step(sorted_ratio, ecdf_ratio, where='post')
    # plt.xlabel('Success Ratio (wins / total)')
    # plt.ylabel('ECDF')
    # plt.title('ECDF of Success Ratio')
    # plt.grid(True)

    # 3. Fraction of ASNs that are successful (at least one win)
    num_successful = sum(w > 0 for w in wins)
    total_asns = len(wins)
    fraction_successful = num_successful / total_asns if total_asns > 0 else 0
    
    # plt.subplot(1,3,3)
    # plt.bar(['Successful', 'Unsuccessful'], [fraction_successful, 1 - fraction_successful], color=['green', 'red'])
    # plt.title('Fraction of ASNs Successful')
    # plt.ylim(0,1)
    # plt.ylabel('Fraction')
    # plt.grid(axis='y')

    # plt.tight_layout()
    # plt.show()

    #print(f"{observer}Fraction of ASNs that were successful: {fraction_successful:.2f} ({num_successful}/{total_asns})")
    print(f"{observer}, {fraction_successful:.2f}, ({num_successful}/{total_asns})")
    return fraction_successful
fracs = []
hijackers_res = []
for file in os.listdir(results_folder):
    if 'unknown' in file:
        continue
    observer=file.replace('rs-','').replace('.pickle','')
    print(observer)
    
    results = pickle.load(open(results_folder+file,'rb'))
    for result in results:
        wins = result['origin_results_won']
        loss = result['origin_results+lost']
        for key in wins:
            someval = wins[key]

    #pefix,hijacker = filter_results(results,observer)

    #hijackers_res.append(hijacker)
exit(0)    
for hijacker_i in range(len(hijackers_res)):
    #print(hijacker.keys())        
    #hijacker_results =
    for hijacker_asn in  hijackers_res[hijacker_i].keys():
        if hijacker_asn == 'observer':
            continue
        else:
            hijacker_res = hijackers_res[hijacker_i][hijacker_asn]
            #results = hijackers_res[hijacker][hijacker_asn]
            frac = comp_res(hijacker_res,observer)
            #frac = comp_res(results,observer)
            #fracs.append((observer,frac))
            fracs.append((hijacker_asn,frac))
    #exit(0)
    
#exit(0)    


df = pandas.DataFrame(sorted(fracs,key=lambda x: x[0]))

#plt.step(df[0], df[1], where='post')
plt.scatter(df[0], df[1])
plt.xlabel('observer')
plt.ylabel('hijacker success')
plt.title('CDF')
plt.grid(True)
plt.show()    

exit(0)
#sorted_fracs = np.sort(fracs,1)
#df

#for f in fracs:

exit(0)
#print(results)
print(results[0]['origin_results_won'].keys())
#reasons = ['HPP', 'AS_Path', 'Origin_Type', 'LPP', 'time', 'default', 'unknown_neighbor']
reasons = ['HPP', 'AS_Path', 'Origin_Type', 'LPP', 'time', 'default']
for result in results:
    #print(result)
    try:
        u = result['origin_results_won']['unknown_neighbor']
        if len(u)>0:
            print(u)
    except:
        pass
hijacker_asns = [int(d['hijacker_asn']) for d in results]

# Sort the data
sorted_asns = np.sort(hijacker_asns)

# Calculate ECDF values
ecdf = np.arange(1, len(sorted_asns) + 1) / len(sorted_asns)

# Plot ECDF
plt.step(sorted_asns, ecdf, where='post')
plt.xlabel('Hijacker ASN')
plt.ylabel('Empirical CDF')
plt.title('ECDF of Hijacker ASN')
plt.grid(True)
plt.show()    
exit(0)
# # for result in results:
# #  #   print(result)
# #     print(result['hijacker_update'])
# exit(0)
observer_mapping = []
hijackers_cc = 'rs'
def parse_default(results):
    num_lost = 0
    num_won = 0
    ukn=0
    t = 0
    for result in results:
        if result['num_benign_updates']==0:
            if 'origin_results_lost' in result.keys():
                num_lost+= len(result['origin_results_lost']['default'])
            elif 'origin_results_won' in result.keys():                
                num_won+=len(result['origin_results_won']['default'])
            else:
                ukn+=1
        t+=1
    if t !=0:
        print(num_won,num_lost,ukn,t, (num_lost/t)*100)
for file in os.listdir(results_folder):
    if 'unknown' in file:
        continue
    results = pickle.load(open(results_folder+file,'rb'))
    parse_default(results)
    continue
    for result in results:
        print(result['num_benign_updates'])
        if result['num_benign_updates']==0:
            print(result)
            exit(0)
        continue
    #exit(0)
        for _ in range(0):
            # if observer_ID == 18:
            #     print(result['origin_results_won'],len(result['origin_results_won']['default']))
            prefix = result['prefix_hijacked']
            if prefix not in prefixes:
                prefixes.add(result['prefix_hijacked'])
#print(prefixes)
exit(0)
prefix_categories =  'hijacker_asn,num_benign_updates,HPP,AS_Path,Origin_Type,LPP,time,default,unknown_neighbor'
#print(prefix_categories)
won_lost = 'origin_results_won'
#won_lost = 'origin_results_lost'
#prefixes = ['52.24.0.0/14']
summaries = []
#print(prefixes)
#exit(0)
all_reasons = {}

for file in os.listdir(results_folder):
    if 'unknown' in file:
        continue
    results = pickle.load(open(results_folder+file,'rb'))
    for result in results:
        for prefix in prefixes:
            if prefix not in all_reasons:
                all_reasons[prefix] = {'total_updates':0}
            # print('\n')
            # print(prefix_categories)
            # print(prefix)
            num_updates = 0
            reasons = {}
    
            if result['prefix_hijacked']!=prefix:
                continue
            winstr = f"{result['hijacker_asn']},{result['num_benign_updates']},"
            num_updates = num_updates + result['num_benign_updates']
            # print(num_updates)
            # continue
            for reason in result[won_lost]:
                if reason not in reasons:
                    reasons[reason] = 0                    
                num_wins = len(result[won_lost][reason])
                reasons[reason]+=num_wins
                #all_reasons[prefix][reason]+=num_wins
                winstr=winstr+str(num_wins)+','
                #if num_wins>0:
                #   print(reason,num_wins)
            #print(winstr[:-1])
        #print('num updates', num_updates)
        'hijacker_asn,num_benign_updates,HPP,AS_Path,Origin_Type,LPP,time,default,unknown_neighbor'
        totalst='total,'+str(num_updates)+','
        
        sum_of_wins = 0
        for reason in reasons:
            if reason not in all_reasons[prefix]:
                all_reasons[prefix][reason] = reasons[reason]
            totalst = totalst+str(reasons[reason])+','
            sum_of_wins+=reasons[reason]
            #print('overall wins ',reason,reasons[reason])
        # print(totalst[:-1])      
        if num_updates ==0:
            pass
            # print("num updates is 0")
            
            # print(prefix,sum_of_wins, num_updates, sum_of_wins/1)
            #num_updates = 1

        else:
            summaries.append((prefix,sum_of_wins , num_updates))  
            #print(prefix,'is hijackable',sum_of_wins / num_updates)
#exit(0)
pie_reasons = {} 
for prefix in all_reasons:
    if prefix not in pie_reasons:
        pie_reasons[prefix] = {}
    total_updates = 0 
    if 'total_updates' in all_reasons[prefix].keys():
        total_updates = all_reasons[prefix]['total_updates']
    print(prefix,total_updates)
    for reason in all_reasons[prefix]:
        num = all_reasons[prefix][reason]        
        if num >0:
            #if reason not in pie_reasons[prefix]:
            pie_reasons[prefix][reason] = num            

        #print(reason,num)
   
#exit(0)
print('summary')
data = [
    {"owner": "OSU", "ip": "52.24.0.0/14", "percent": None,"reasons":{}},
    {"owner": "UO", "ip": "184.171.0.0/17", "percent": None,"reasons":{}},
    {"owner": "SOU", "ip": "141.193.213.0/24", "percent": None,"reasons":{}},
    {"owner": "USU", "ip": "129.123.0.0/16", "percent": None,"reasons":{}},
    {"owner": "Oxford", "ip": "151.101.128.0/22", "percent": None,"reasons":{}},
]

total_attempts =0
total_success = 0
prefres = {}
for prefix,sum_of_wins, num_updates in summaries:        
    if prefix not in prefres:
        prefres[prefix]= {'num_wins':0,'num_updates':0}
    
    if num_updates == 0:
        print('num upates ',num_updates)
        prefres[prefix]['num_updates']+=1
        #total_attempts +=1
        if sum_of_wins >0:
            prefres[prefix]['num_wins']+=1
            #total_success+=1
    else:
        #total_attempts+=num_updates 
        #total_success+=sum_of_wins
        prefres[prefix]['num_wins']+=sum_of_wins
        prefres[prefix]['num_updates']+=num_updates
#for prefix in pie_reasons:
    
    #print(prefix,pie_reasons[prefix])
 
for prefix in prefres:
    #all_reasons[prefix]['total_updates'] = prefres[prefix]['num_updates']
    percent = (prefres[prefix]['num_wins'] / prefres[prefix]['num_updates'])*100
#    print(prefix, prefres[prefix], percent)
    for d in data:
        if d['ip']==prefix:
            d['percent'] = percent
            d['reasons'] = pie_reasons[prefix]

#print(prefix,',',percent)
for d in data:
    print(d)
exit(0)
def prepare_bar_chart(data,save=False,show=False):
    # Prepare data for plotting
    labels = [f"{item['owner']}  {item['ip']}" for item in data]
    percents = [item['percent'] for item in data]

    plt.rcParams.update({
        'font.size': 24,        # Base font size
        'axes.titlesize': 32,   # Title
        'axes.labelsize': 28,   # Axis labels
        'xtick.labelsize': 24,
        'ytick.labelsize': 24,
    })
    # Plot
    fig, ax = plt.subplots(figsize=(24, 16))
    bars = ax.barh(labels, percents, color="#003f5c")
    
    # Add percentage labels to bars
    for bar, pct in zip(bars, percents):
        width = bar.get_width()        
        if width ==100:
            ax.text(width +1, bar.get_y() + bar.get_height()/2,
                f"100%", va='center', ha='left',fontsize=label_text_size)
        else:
            ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f"{pct:.2f}%", va='center', ha='left',fontsize=label_text_size)
    #add y axis label
    plt.text(-40, 3.5, 'Universities and their prefixes', fontsize=24,rotation=90)

    # Style
    ax.set_xlim(0, 115)
    ax.set_xlabel("Percent Chance to be Hijacked", fontsize=32)
    ax.set_title("University's Chance of Being Hijacked", fontsize=title_text_size, weight='bold',y=1.01)
    plt.xticks([0, 20, 40, 60, 80, 100 ], [f"{i:.2f}%" for i in [0, 20, 40, 60, 80, 100]])
    plt.gca().invert_yaxis()  # Highest % on top
    plt.tight_layout()
    #fig.subplots_adjust(left=0.28,bottom=0.1)
    # Show plot
    if show:
        plt.show()
    if save:
        plt.savefig("figures/prefix_vulnerability_bar.png", dpi=600)    

import matplotlib.pyplot as plt

def plot_hijack_pie(data,show=False,save=False):
    
    owner = data['owner']
    percent = data['percent']
    reasons = data['reasons']

    # Map reasons to labels (customize if needed)
    reason_labels = {
        'AS_Path': "Attack Success: Hijacker had a shorter AS_Path length",
        'time': "Attack Success: Hijacker's Update arrived Earlier",
        'HPP': "Attack Success: Hijacker used a more preferred neighbor",
    }

    total_hijacks = sum(reasons.values())

    # Get reason percentages
    slices = []
    labels = []
    colors = []
    explode = []

    

    for reason, count in reasons.items():
        pct = (count / total_hijacks) * percent
        slices.append(pct)
        labels.append(reason_labels.get(reason, reason))
        colors.append(color_map.get(reason, 'gray'))
        explode.append(0)
    # Add "Safe" slice
    safe_pct = 100 - percent
    slices.append(safe_pct)
    labels.append(f"Attack Failed")
    colors.append(color_map['Safe'])
    explode.append(0.1)

    # Plot pie chart
    fig, ax = plt.subplots(figsize=(24, 14))
    #fig2, ax2 = plt.subplots(figsize=(24, 16))

    wedges, texts, autotexts = ax.pie(
        slices, explode=explode,labels=None, colors=colors, autopct='%1.0f%%', startangle=90, textprops={'color': "black", 'fontsize':f'{label_text_size}','weight':'bold'}
    )
    ax.legend(wedges, labels, title="Result", loc="center left", bbox_to_anchor=(1, 0.75),fontsize = legend_text_size,title_fontsize=legend_text_size)
    ax.set_title(f"Hijacking results for {owner}",fontsize=32, weight='bold',loc='left',x=0.75)    
    # handles,leg_lables =ax.get_legend_handles_labels()
    # fig_legend = plt.figure(figsize=(3, 1))
    # ax_legend = fig_legend.add_subplot(111)
    # ax_legend.legend(handles, labels, loc='center')
    # ax_legend.axis('off')    
    # plt.show()
    # exit(0)    
    plt.tight_layout()
    fig.subplots_adjust(top=0.9,right=0.5)
    if show:
        plt.show()
    if save:
        plt.savefig(f"figures/why_is_{owner}_vulnerable.png", dpi=600)    

# def legend_only(show=False,save=False):
#     fig, ax = plt.subplots(figsize=(24, 16))
def export_legend(legend, filename="legend.png"):
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)

def plot_hijack_multi_pie(datas,vert = False,horz = False, show=False,save=False,export_leg=False):
    if vert:
        fig, axes = plt.subplots(2,1,figsize=(24, 14))
    if horz:
        fig, axes = plt.subplots(1,2,figsize=(15, 15))
    for plot_num, data in enumerate(datas):
        owner = data['owner']
        print(plot_num, owner)
        #continue
        
        percent = data['percent']
        reasons = data['reasons']

        # Map reasons to labels (customize if needed)
        reason_labels = {
            'AS_Path': "Attack Success: Shorter AS_Path length",
            'time': "Attack Success: Update arrived earlier",
            'HPP': "Attack Success: More preferred neighbor",
        }

        total_hijacks = sum(reasons.values())

        # Get reason percentages
        slices = []
        labels = []
        colors = []
        explode = []


        for reason, count in reasons.items():
            pct = (count / total_hijacks) * percent
            slices.append(pct)
            labels.append(reason_labels.get(reason, reason))
            colors.append(color_map.get(reason, 'gray'))
            explode.append(0)
        # Add "Safe" slice
        safe_pct = 100 - percent
        slices.append(safe_pct)
        labels.append(f"Attack Failed")
        colors.append(color_map['Safe'])
        explode.append(0.1)

        # Plot pie chart
        
        #fig2, ax2 = plt.subplots(figsize=(24, 16))

        wedges, texts, autotexts = axes[plot_num].pie(
            slices, explode=explode,labels=None, colors=colors, autopct='%1.0f%%', startangle=90, textprops={'color': "black", 'fontsize':f'{label_text_size}','weight':'bold'}
        )
        if plot_num ==0 and export_leg:
            legend = fig.legend(wedges, labels, title="Result", loc="center left", bbox_to_anchor=(1, 0.75),fontsize = legend_text_size,title_fontsize=legend_text_size)        
            #a = fig.get_legend_handles_labels()
            print(legend)
            export_legend(legend)
        if horz:
            axes[plot_num].set_title(f"{owner} Hijacking Results",fontsize=title_text_size, weight='bold',loc='center',y= 0.95)#,x=0.15)    
        if vert:
            fig.subplots_adjust(top=1.0,
                                bottom=0.0,
                                left=0.68,
                                right=1.0,
                                hspace=0.031,
                                wspace=0.2)
            pass
            axes[plot_num].set_title(f"{owner}\nhijacking\nresults",fontsize=title_text_size-4, weight='bold',loc='left',x=-.5,y=.4) 
        
    
    if show:
        plt.show()
    if save:
        plt.savefig(f"figures/multi_pie.png", dpi=600)    
def plot_hijack_custum_pie(datas, show=False,save=False):
    fig, axes = plt.subplots(2,2,figsize=(24, 14))    
        
    for plot_num, data in enumerate(datas):
        owner = data['owner']
        print(plot_num, owner)
        if plot_num == 0:
            plot_pos = 0,0
        elif plot_num == 1:
            plot_pos = 1,0
        elif plot_num ==2:
            plot_pos = 0,1
        else:
            
            #axes
            continue
        
        percent = data['percent']
        reasons = data['reasons']

        # Map reasons to labels (customize if needed)
        reason_labels = {
            'AS_Path': "Attack Success: Shorter AS_Path length",
            'time': "Attack Success: Update arrived earlier",
            'HPP': "Attack Success: More preferred neighbor",
        }

        total_hijacks = sum(reasons.values())

        # Get reason percentages
        slices = []
        labels = []
        colors = []
        explode = []


        for reason, count in reasons.items():
            pct = (count / total_hijacks) * percent
            slices.append(pct)
            labels.append(reason_labels.get(reason, reason))
            colors.append(color_map.get(reason, 'gray'))
            explode.append(0)
        # Add "Safe" slice
        safe_pct = 100 - percent
        if safe_pct > 0:
            slices.append(safe_pct)
            labels.append(f"Attack Failed")
            colors.append(color_map['Safe'])
            explode.append(0.1)

        # Plot pie chart
        
        #fig2, ax2 = plt.subplots(figsize=(24, 16))
        print(plot_num,'plot num <--')
        
        wedges, texts, autotexts = axes[plot_pos].pie(slices, explode=explode,labels=None, colors=colors, autopct='%1.0f%%', startangle=90, textprops={'color': "black", 'fontsize':f'{0}','weight':'bold'})
        # else:
        #     wedges, texts, autotexts = axes[plot_pos].pie(
        #         slices, explode=explode,labels=None, colors=colors, autopct='%1.0f%%', startangle=90, textprops={'color': "black", 'fontsize':f'{label_text_size}','weight':'bold'}
        #     )
        #if plot_num ==0 and export_leg:
        #    legend = fig.legend(wedges, labels, title="Result", loc="center left", bbox_to_anchor=(1, 0.75),fontsize = legend_text_size,title_fontsize=legend_text_size)        
            #a = fig.get_legend_handles_labels()
            #print(legend)
            #export_legend(legend)
        #if horz:
        # if plot_num <2:
        #     axes[plot_pos].set_title(f"Hijacking results for {owner}",fontsize=title_text_size, weight='bold',loc='left')#,x=0.15)    
        # else:
        axes[plot_pos].set_title(f"{owner}\nHijacking\nResults",fontsize=title_text_size, weight='bold',loc='left',x=-.8,y=0.3)    
            #axes[plot_num].set_title(f"{owner}\nhijacking\nresults",fontsize=title_text_size-4, weight='bold',loc='left',x=-.5,y=.4) 
    axes[1,1].axis('off')
            
    if show:
        plt.show()
    if save:
        plt.savefig(f"figures/multi_pie.png", dpi=600)    

#prepare_bar_chart(data,show=True)
#plot_hijack_pie(data[0],show=True)
#exit(0)
#plot_hijack_multi_pie([data[0],data[-1]],vert=True,show=True,export_leg = False)
#plot_hijack_multi_pie([data[0],data[-1]],horz=True,show=True,export_leg = False)
#plot_hijack_multi_pie([data[3],data[2]],horz=True,show=True,export_leg = False)
plot_hijack_custum_pie([data[1],data[2],data[3]],show=True)
# for d in data:
#     print('making data for ',d['owner'])
#     plot_hijack_pie(d,False,True)


exit(0)

# for result in results:
# for i in range(len(results)):
#     for key in results[i]['origin_results_won']:
#         print(len(results[i]['origin_results_won']),key)
        
#         #print(key,results[0]['origin_results_lost'][key])
# exit(0)
    
#         print(key,result[key])
# exit(0)
#     if result['num_benign_updates'] > 1:
#         print(result['hijacker_asn'], result['prefix_hijacked'])
#         #print(result['unknown_neighbor'])
        
#         for key in result:
#             if key == 'num_benign_updates' or 'origin_results' in key:
#                 print(key, result[key])
#             if key =='unknown_neighbor':
#                 print("~~~~")
#                 print(result[key])
#                 print("~~~~")
# exit(0)        
# import requests 
# resp = requests.get(url)
# json = resp.json()
# state =  json["data"]['bgp_state']
# for things in state:
#     target = things['target_prefix']
#     if ':' in target:
#         continue
#     url = f'https://stat.ripe.net/data/prefix-overview/data.json?resource={target}'
#     resp = requests.get(url)
#     #print(resp)
#     json = resp.json()
#     asns = json['data']['asns']
#     print(target,',',asns)
# exit(0)    
print('wins')
#categories =  'hijacker_asn,hijacked_prefix,num_benign_updates,HPP,AS_Path,Origin_Type,LPP,time,default,unknown_neighbor'

categories = 'hijacker_asn,hijacked_prefix,num_benign_updates,'
for key in results[0]['origin_results_lost']:
    #print(key,results[0]['origin_results_lost'][key])
    categories=categories+key+','
print(categories)
categories = categories[:-1]
# for result in results:
#     for key in result:
#         print(key) 
#     exit(0)
for result in results:
    #print(result)        
    #print(result['hijacker_asn'])
    winstr = f"{result['hijacker_asn']},{result['prefix_hijacked']},{result['num_benign_updates']},"
    
    for reason in result['origin_results_won']:
        num_wins = len(result['origin_results_won'][reason])
        winstr=winstr+str(num_wins)+','
        #print(reason,num_wins)
        #if num_wins>0:
         #   print(reason,num_wins)
    print(winstr[:-1])#,len(winstr[:-1].split(',')))
    # for index in range(len(winstr[:-1].split(','))):
    #     print (index,categories.split(',')[index])
print('~~~~~~~~~~~`')    
print('losses')

print(categories)
for result in results:
    #print(result)        
    #print(result['hijacker_asn'])
    winstr = f"{result['hijacker_asn']},{result['prefix_hijacked']},{result['num_benign_updates']},"
    
    for reason in result['origin_results_lost']:
        num_wins = len(result['origin_results_lost'][reason])
        winstr=winstr+str(num_wins)+','
        #if num_wins>0:
         #   print(reason,num_wins)
    print(winstr[:-1])    
    # print('losses')
    # for reason in result['origin_results_lost']:
    #     num_loss = len(result['origin_results_lost'][reason])
    #     if num_loss>0:
    #         print(reason,num_loss)        
        
    #if 'default' in result['results'].keys():
     #   print(result['hijacker_asn'],result['results']['HPP'],result['results']['AS_Path'],result['results']['Origin_Type'],result['results']['LPP'],result['results']['time'],result['results']['default'])
    #else:
        #print(result['hijacker_asn'],result['results']['HPP'],result['results']['AS_Path'],result['results']['Origin_Type'],result['results']['LPP'],result['results']['time'],result['results']['default'])        
prefixes = set()
for result in results:
    prefixes.add(result['prefix_hijacked'])
print('~~~~~~~~~`')
print('prefix results')
prefix_categories =  'hijacker_asn,num_benign_updates,HPP,AS_Path,Origin_Type,LPP,time,default,unknown_neighbor'
print(prefix_categories)
for prefix in prefixes:
    print(prefix)
    for result in results:
        if result['prefix_hijacked']!=prefix:
            continue
        winstr = f"{result['hijacker_asn']},{result['num_benign_updates']},"
        
        for reason in result['origin_results_won']:
            num_wins = len(result['origin_results_won'][reason])
            winstr=winstr+str(num_wins)+','
            #if num_wins>0:
            #   print(reason,num_wins)
        print(winstr[:-1])