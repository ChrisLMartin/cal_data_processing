import argparse
from TEST_cal_data_import_TEST import data_in, efc_calcs
#from datetime import datetime
import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

def multi_files(file_list):
    for filename in file_list:
        main(filename)
    plt.show()
    
def main(filename):
    s_id, df_p, df_v, df_vp = data_in(filename)
    df_p, df_v = efc_calcs(s_id, df_p, df_v)
    cal_data_plot(s_id, df_v)

def cal_data_plot(sample_id, df_val):
    
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
    
if __name__ == '__main__':
     multi_files(files)