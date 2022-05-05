# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 09:42:50 2022

@author: isabe
"""

import rasterio as rio
import numpy as np
import pandas as pd
import glob

file_list = glob.glob("C:/Users/isabe/Documents/UNIGE/Memoire/Data/bio_crop/.tif")

lc18 = rio.open(next((s for s in file_list if "18" in s), None)).read(1)
lc09 = rio.open(next((s for s in file_list if "09" in s), None)).read(1)
lc97 = rio.open(next((s for s in file_list if "97" in s), None)).read(1)
lc85 = rio.open(next((s for s in file_list if "85" in s), None)).read(1)

def format_lc(r):
    r = r[r != 0]
    r = pd.Series(r)
    return r

lc2018_pd = format_lc(lc18)
lc2009_pd = format_lc(lc09)
lc1997_pd = format_lc(lc97)
lc1985_pd = format_lc(lc85)

series_list = [lc1985_pd, lc1997_pd, lc2009_pd, lc2018_pd]
cats = np.unique(lc18)
cats = np.ndarray.tolist(cats)[1:]
#%%
def calculate_interval_level(y1, y2, tdiff):
    
    pda = series_list[y1]
    pdb = series_list[y2]
    
    df_confusion = pd.crosstab(pda, pdb)

    term1 = []
    for j in range(len(cats)):
        t = df_confusion.iloc[j]
        tsum = t.sum()
        t1 = tsum-df_confusion.iloc[j,j]
        term1.append(t1)
    term1 = sum(term1)

    term2 = []
    for j in range(len(cats)):
        t = df_confusion.iloc[j]
        t2 = t.sum()
        term2.append(t2)
    term2 = sum(term2)

    St = ((term1/term2)/tdiff)*100
    return St

print('st 1985-1997', calculate_interval_level(0, 1, 12))
print('st 1997-2009', calculate_interval_level(1, 2, 12))
print('st 2009-2018', calculate_interval_level(2, 3, 9))
#%%
def uniform_change():
    term1 = []
    for i in range(len(series_list))[:2]:
        pda = series_list[0+i]
        pdb = series_list[1+i]
    
        df_confusion = pd.crosstab(pda, pdb)
        for j in range(len(cats)):
            t = df_confusion.iloc[j]
            tsum = t.sum()
            t1 = tsum-df_confusion.iloc[j,j]
            term1.append(t1)
        
    t1 = sum(term1)
    U = ((t1/4129062)/33)*100
    return U

print ("U", uniform_change())
#%%
# J number of categories;
# i index for a category at the initial time point for a particular time interval;
# j index for a category at the final time point for a particular time interval;
# m index for the losing category in the transition of interest;
# n index for the gaining category in the transition of interest;
# T number of time points;
# t index for the initial time point of interval [Yt, Yt+1], where t ranges from 1 to T−1;
# Yt year at time point t;

#%%
# create array with the names of the categories
from collections import Counter
def calculate_category_level(y1, y2, tdiff, time_int_label):
    pda = series_list[y1]
    pda_count = Counter(pda)
    pdb = series_list[y2]
    pdb_count = Counter(pdb)

    gain_list = pdb[(pdb!=pda)]
    gain_count = Counter(gain_list)
    loss_list = pda[(pda!=pdb)]
    loss_count = Counter(loss_list)
    
    g_hold = []
    gtj_hold = []
    l_hold = []
    ltj_hold = []
    holder = pd.DataFrame(
        gain_count.values(), 
        columns = ['total_gain'],
        index = gain_count.keys())
    lholder = pd.DataFrame(
        loss_count.values(), 
        columns = ['total_loss'],
        index = loss_count.keys())
    
    for k in gain_count: 
        Gtj = ((gain_count[k]/tdiff)/pdb_count[k])*100
        g_hold.append(k)
        gtj_hold.append(Gtj)
        
    gain_df = pd.DataFrame(
        gtj_hold,
        columns = ['Gtj'],
        index = g_hold)
    
    holder = holder.join(gain_df)
    
    for k in loss_count: 
        Ltj = ((loss_count[k]/tdiff)/pda_count[k])*100
        l_hold.append(k)
        ltj_hold.append(Ltj)
    
    loss_df = pd.DataFrame(
        ltj_hold,
        columns = ['Ltj'],
        index = l_hold)
    
    holder = holder.join(lholder, how="right")
    holder = holder.join(loss_df)
    holder['Time_int'] = time_int_label
    return holder

cat1 = calculate_category_level(0, 1, 12, "1985-1997")
cat2 = calculate_category_level(1, 2, 12, "1997-2009")
cat3 = calculate_category_level(2, 3, 9, "2009-2018")

cat_all = pd.concat([cat1, cat2, cat3])

cat_all.to_csv('C:/Users/isabe/Documents/UNIGE/Memoire/Data_analysis/LU_cat_level_4.csv')
#%%
def calculate_transition_level(y1, y2, tdiff, time_int_label):
    
    pda = series_list[y1]
    pdb = series_list[y2]

    df = pd.DataFrame(list(zip(pda, pdb)),
               columns =['pda', 'pdb'])
    df = df[df.pda != df.pdb]
    df['trans'] = df["pda"].astype(str) + df["pdb"].astype(str)
    trans_count = Counter(df['trans'])

    trans_df = pd.DataFrame(list(zip(trans_count.keys(), trans_count.values())),
               columns =['trans', 'count'])
    trans_df['t'] = trans_df['trans'].str[0:3].astype(int)
    trans_df['t1'] = trans_df['trans'].str[3:].astype(int)

    pda_count = Counter(pda)   
    pdb_count = Counter(pdb) 
    gain_list = pdb[(pdb!=pda)]
    gain_count = Counter(gain_list)
    gain = pd.DataFrame(list(zip(gain_count.keys(), gain_count.values())),
               columns =['cat', 'gain'])
    loss_list = pda[(pda!=pdb)]
    loss_count = Counter(loss_list)
    loss = pd.DataFrame(list(zip(loss_count.keys(), loss_count.values())),
               columns =['cat', 'loss'])
    initial = pd.DataFrame(list(zip(pda_count.keys(), pda_count.values())),
               columns =['cat', 'initial_count'])
    initial2 = pd.DataFrame(list(zip(pda_count.keys(), pda_count.values())),
               columns =['cat', 'initial_count2'])
    jt1 = pd.DataFrame(list(zip(pdb_count.keys(), pdb_count.values())),
               columns =['cat', 't1_count'])
    jt2 = pd.DataFrame(list(zip(pdb_count.keys(), pdb_count.values())),
               columns =['cat', 't1_count2'])

    trans_df = trans_df.set_index('t').join(initial.set_index('cat'))
    trans_df.reset_index(inplace=True)
    trans_df = trans_df.rename(columns = {'index':'t'})
    trans_df = trans_df.set_index('t1').join(gain.set_index('cat'))
    trans_df.reset_index(inplace=True)
    trans_df = trans_df.rename(columns = {'index':'t1'})
    trans_df = trans_df.set_index('t1').join(jt1.set_index('cat'))
    trans_df.reset_index(inplace=True)
    trans_df = trans_df.rename(columns = {'index':'t1'})
    trans_df = trans_df.set_index('t').join(loss.set_index('cat'))
    trans_df.reset_index(inplace=True)
    trans_df = trans_df.rename(columns = {'index':'t'})    
    trans_df = trans_df.set_index('t1').join(initial2.set_index('cat'))
    trans_df.reset_index(inplace=True)
    trans_df = trans_df.rename(columns = {'index':'t1'})
    trans_df = trans_df.set_index('t').join(jt2.set_index('cat'))
    trans_df.reset_index(inplace=True)
    trans_df = trans_df.rename(columns = {'index':'t'})
    
    trans_df = trans_df.drop(['trans'], axis=1)
    trans_df['Rtin'] = ((trans_df['count']/tdiff)/trans_df['initial_count'])*100
    trans_df['Qmj'] = ((trans_df['count']/tdiff)/trans_df['t1_count'])*100
    trans_df['Wtn'] = ((trans_df['gain']/tdiff)/(4129062-trans_df['initial_count2']))*100
    trans_df['Vtm'] = ((trans_df['loss']/tdiff)/(4129062-trans_df['t1_count2']))*100
    trans_df['Time_int'] = time_int_label
    
    return trans_df
    
test = calculate_transition_level(0, 1, 12, "1985-1997")    
test.to_csv('C:/Users/isabe/Documents/UNIGE/Memoire/Data_analysis/LU_10_transition.csv')
test = calculate_transition_level(1, 2, 12, "1997-2009")    
test.to_csv('C:/Users/isabe/Documents/UNIGE/Memoire/Data_analysis/LU_10_transition.csv', mode='a')
test = calculate_transition_level(2, 3, 9, "2009-2018")    
test.to_csv('C:/Users/isabe/Documents/UNIGE/Memoire/Data_analysis/LU_10_transition.csv', mode='a')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    