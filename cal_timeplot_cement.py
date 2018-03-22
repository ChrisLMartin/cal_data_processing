import argparse
from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Category10
from cal_data_cement import data_in, opc_calcs
#import matplotlib.pyplot as plt
#import numpy as np
#import scipy.signal as signal

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

def multi_files(file_list):
    s_ids, xs, ys, x1s, y1s = [], {}, {}, {}, {}
    
    for filename in file_list:
        s_id, xs[s_id], ys[s_id], x1s[s_id], y1s[s_id] = main(filename)
        s_ids.append(s_id)
#    plt.show()
#    print(xs.keys())
#    print(s_ids)
    
    xslol = [v for v in xs.values()]
    yslol = [v for v in ys.values()]
    colours = Category10[len(s_ids)]
    
    output_file("OPCCalPlots.html")
    
    p = figure(title="Full run", 
               x_axis_label='Time (h)', 
               y_axis_label='Specific Power (W/g cem mat)',
               width=1024,
               height=600)
    
    for (x, y, colr, leg) in zip(xslol, yslol, colours, s_ids):
        p.line(x, y, color = colr, legend=leg)
    
    show(p)
    
def main(filename):
    s_id, df_p, df_v, df_vp = data_in(filename)
    df_p, df_v = opc_calcs(s_id, df_p, df_v)
    x, y, x1, y1 = cal_data_plot(s_id, df_v)
    
    return s_id, x, y, x1, y1
    

def cal_data_plot(sample_id, df_val):    
#    plt.subplot(2,1,1)
    x = df_val['Tmix,s'].values/3600
    y = df_val['Power/Cement,W/g'].values
    time_range = [x * 60 for x in [5, 12]]
    x1 = df_val['Tmix,s'].values[time_range[0]:time_range[1]]/3600
    y1 = df_val['Power/Cement,W/g'].values[time_range[0]:time_range[1]]
    '''
    plt.subplot(1,2,1)
    plt.plot(x,y, label=(sample_id))
#    plt.plot(df_val.values[peakidx,0]/3600,df_val.values[peakidx,4])
    plt.title('Full run')
    plt.xlabel('Time (h)')
    plt.ylabel('Specific Power (W/g cem mat)')
#    plt.legend()

    plt.subplot(1,2,2)
    plt.plot(x1,y1, label=(sample_id))
    plt.title('Run detail ({} - {} h)'.format(time_range[0]/60, time_range[1]/60))
    plt.xlabel('Time (h)')
    plt.ylabel('Specific Power (W/g cem mat)')
    plt.legend()
    '''
    return x, y, x1, y1
    

if __name__ == '__main__':
     multi_files(files)