# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 08:40:50 2018

@author: christopher.martin
"""

import matplotlib.pyplot as plt
import os
import pandas as pd



def file_walk():
    paths = (os.path.join(root, filename)
            for root, _, filenames in os.walk('//ICAL8000/Users/Public/Documents/Calmetrix/CalCommander/Export')
            for filename in filenames)
    tti_dict = {}
    for path in paths:
        mix_id, tti = find_tti(path)
        print(mix_id)
        tti_dict[mix_id] = tti
        if mix_id == 'Water':
            break
    return tti_dict
        
def find_tti(input_filename):
    mix_id = input_filename.split(sep='_')[1]
    df = pd.read_table(input_filename, nrows=7, error_bad_lines=False, encoding="latin1", header=None)
    df = df.set_index(0).transpose()
#    keys = ['Mix ID', 'Time to Iso (hh:mm)']
#    assert keys[0] in df.columns, '{} does not exist'.format(keys[0])
#    assert keys[1] in df.columns, '{} does not exist'.format(keys[1])
    return mix_id, df['Time to Iso (hh:mm)'].values[0]

def analyse_ttis():
    tti_dict = file_walk()
    ttis_hm = list(tti_dict.values())
    ttis_m = []
    ttis_h = []
    for time in ttis_hm:
        tti_split = time.split(sep=':')
        ttis_m.append(int(tti_split[0]) * 60 + int(tti_split[1]))
        ttis_h.append(float(tti_split[0]) + float(tti_split[1])/60)
    plt.subplot(1,2,1)
    plt.hist(ttis_h, bins=20)
    plt.subplot(1,2,2)
    plt.boxplot(ttis_h)
    
if __name__ == '__main__':
    analyse_ttis()