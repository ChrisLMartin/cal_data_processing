import argparse
from cal_data_import import data_in, efc_calcs
import csv
#from datetime import datetime
import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

#filename = 'C:/Users/christopher.martin/Documents/Python/cal_data/2018-03/20180306-53_23degC_Ch08_2018-03-06_14-09-20.txt'

def multi_files(file_list):
    d = {}
    for filename in file_list:
        s_id, d[s_id] = main(filename)
    for k, v in d.items():
        print("Sample ID: {} - Total energy at 24 hours: {:.2f} J/g".format(k, v))
    with open('energy_24h.txt', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for k, v in d.items():
            writer.writerow([k, v])
    plt.show()
    
def main(filename):
    s_id, df_p, df_v, df_vp = data_in(filename)
    df_p, df_v = efc_calcs(s_id, df_p, df_v)
    e24 = cal_data_plot(s_id, df_v)
    
    return s_id, e24

def cal_data_plot(sample_id, df_val):
    
    e24 = df_val.loc[(df_val['Tmix,s'] > 86370) & (df_val['Tmix,s'] < 86430), ['Heat/SCM,J/g']].values[0][0]
#    plt.subplot(2,1,1)
    plt.subplot(1,2,1)
#    plt.plot(df_val.values[:,0]/3600,df_val.values[:,4], label=(sample_id + ': ' + admixtures))
    plt.plot(df_val['Tmix,s'].values[:]/3600,df_val['Power/SCM,W/g'].values[:], label=(sample_id))
#    plt.title('Full run')
    plt.xlabel('Time (h)')
    plt.ylabel('Specific Power (W/g cem mat)')
#    plt.legend()

    plt.subplot(1,2,2)
#    plt.plot(df_val.values[90:1200,0]/3600,df_val.values[90:1200,4], label=(sample_id + ': ' + admixtures))
    plt.plot(df_val['Tmix,s'].values[:]/3600,df_val['Heat/SCM,J/g'].values[:], label=(sample_id))
#    plt.title('Run detail (1.5 - 20 h)')
    plt.xlabel('Time (h)')
#    plt.ylabel('Specific Power (W/g cem mat)')
    plt.ylabel('Specific Energy (J/g cem mat)')
    plt.legend()
    
    return e24
    
if __name__ == '__main__':
     multi_files(files)