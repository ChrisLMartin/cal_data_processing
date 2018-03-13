import argparse
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
#import scipy.signal as signal

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

def cal_data_plot(input_filename):
    # plot power and energy per SCM against time in hours
    
    df_param = pd.read_table(input_filename, nrows=29, encoding="latin1", header=None)
    df_param_indexed = df_param.set_index(0)
    sample_id = df_param_indexed.loc['Sample ID', 1]
    df_val = pd.read_table(input_filename, skiprows=29)
    
    m_water = float(df_param_indexed.loc['Water Mass, g', 1])
    m_cem = float(df_param_indexed.loc['Cement Mass, g', 1])
    m_sample = float(df_param_indexed.loc['Sample Mass, g', 1])
    m_sample_cem = m_sample / (m_cem + m_water) * m_cem

    # store cal data in np array then add columns to df with power and energy per SCM
    df_val['Power/Cement,W/g'] = df_val['Power,W'].values / m_sample_cem
    df_val['Heat/Cement,J/g'] = df_val['Heat,J'].values / m_sample_cem
    
    # find peaks
#    peakidx = signal.argrelextrema(df_val.values[:,4], np.greater)
    
    
    
#    plt.subplot(2,1,1)
    plt.subplot(1,2,1)
    plt.plot(df_val.values[:,0]/3600,df_val.values[:,4], label=(sample_id))
#    plt.plot(df_val.values[peakidx,0]/3600,df_val.values[peakidx,4])
    plt.title('Full run')
    plt.xlabel('Time (h)')
    plt.ylabel('Specific Power (W/g cem mat)')
#    plt.legend()

    time_range = [x * 60 for x in [7, 16]]
    plt.subplot(1,2,2)
    plt.plot(df_val.values[time_range[0]:time_range[1],0]/3600,df_val.values[time_range[0]:time_range[1],4], label=(sample_id))
    plt.title('Run detail ({} - {} h)'.format(time_range[0]/60, time_range[1]/60))
    plt.xlabel('Time (h)')
    plt.ylabel('Specific Power (W/g cem mat)')
    plt.legend()
    
    
def multi_files(file_list):

    for filename in file_list:
        cal_data_plot(filename)
    plt.show()

if __name__ == '__main__':
     multi_files(files)