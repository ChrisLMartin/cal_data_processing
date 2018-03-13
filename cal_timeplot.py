import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

def cal_data_plot(input_filename):
    # plot power and energy per SCM against time in hours
    
    df_param = pd.read_table(input_filename, nrows=29, encoding="latin1", header=None)
    df_param_indexed = df_param.set_index(0)
    sample_id = df_param_indexed.loc['Sample ID', 1]
#    admixtures = df_param_indexed.loc['Admix Dose', 1]
    df_val = pd.read_table(input_filename, skiprows=29)
    
    m_slag = float(df_param_indexed.loc['Suppl 1 Mass, g', 1])
    m_fa = float(df_param_indexed.loc['Suppl 2 Mass, g', 1])
    m_water = float(df_param_indexed.loc['Water Mass, g', 1])
    m_agg = float(df_param_indexed.loc['Aggr Mass, g', 1])
    m_sample = float(df_param_indexed.loc['Sample Mass, g', 1])
    m_sample_scm = m_sample / (m_slag + m_fa + m_water + m_agg) * (m_slag + m_fa)

    mix_start = datetime.strptime(df_param_indexed.loc['Mix Time', 1], "%d-%b-%Y %H:%M:%S")
    log_start = datetime.strptime(df_param_indexed.loc['Start Time', 1], "%d-%b-%Y %H:%M:%S")
    time_difference = (log_start - mix_start).total_seconds()
    
    min_search_start = 60 
    min_search_end = 600
    idx_min = np.argmin(df_val['Power,W'].values[min_search_start:min_search_end]) + min_search_start
    if idx_min >= 599:
        idx_min = 0
    df_val = df_val[idx_min:]
    df_val['Heat,J'] = df_val['Heat,J'].apply(lambda x: x - df_val['Heat,J'].values[0])
    
    # store cal data in np array then add columns to df with power and energy per SCM
    array_val = df_val.values
    df_val['Power/SCM,W/g'] = array_val[:, 2] / m_sample_scm
    df_val['Heat/SCM,J/g'] = array_val[:, 3] / m_sample_scm
    df_val['Tmix,s'] = df_val['Tlog,s'].values - time_difference
    df_val['Tmix,days'] = df_val['Tmix,s'].values / 86400               # 60 * 60 * 24
    df_val.drop('Tlog,s', axis=1, inplace=True) 
    
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
    
    
def multi_files(file_list):

    for filename in file_list:
        cal_data_plot(filename)
    plt.show()

if __name__ == '__main__':
     multi_files(files)