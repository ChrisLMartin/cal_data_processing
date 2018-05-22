import argparse
from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Category10
from bokeh.layouts import gridplot
from cal_data_import import data_in, efc_calcs
#import csv
#from datetime import datetime
#import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

#filename = 'C:/Users/christopher.martin/Documents/Python/cal_data/2018-03/20180306-53_23degC_Ch08_2018-03-06_14-09-20.txt'


def multi_files(file_list):
    # d = {}
    s_ids, ts, ps, hs = [], {}, {}, {}
    for filename in file_list:
        s_id, ts[s_id], ps[s_id], hs[s_id] = main(filename)
        s_ids.append(s_id)
    cal_plot(s_ids, ts, ps, hs)


def main(filename):
    s_id, df_p, df_v, _ = data_in(filename)
    _, df_v = efc_calcs(s_id, df_p, df_v)
    t = df_v['Tmix,s'].values / 3600
    p = df_v['Power/SCM,W/g'].values
    h = df_v['Heat/SCM,J/g'].values

    return s_id, t, p, h


def cal_plot(s_ids, ts, ps, hs):
    tslol = [v for v in ts.values()]
    pslol = [v for v in ps.values()]
    hslol = [v for v in hs.values()]
    colours = Category10[len(s_ids)]

    plot_w = 1000
    plot_h = 450
    
    output_file("EFCCalPlots.html")

    p1 = figure(title="Full run",
                x_axis_label='Time (h)',
                y_axis_label='Specific Power (W/g cem mat)',
                width=plot_w,
                height=plot_h)
    
    for (t, pwr, colr, leg) in zip(tslol, pslol, colours, s_ids):
        p1.line(t, pwr, color=colr, legend=leg)

    p2 = figure(title="Full run",
                x_axis_label='Time (h)',
                y_axis_label='Specific Energy (W/g cem mat)',
                width=plot_w,
                height=plot_h,
                x_range=p1.x_range)
   
    for (t, h, colr, leg) in zip(tslol, hslol, colours, s_ids):
        p2.line(t, h, color=colr, legend=leg)
    
    p = gridplot([[p1], [p2]])
    
    show(p)

    
#    for k, v in d.items():
#        print("Sample ID: {} - Total energy at 24 hours: {:.2f} J/g".format(k, v))
#    with open('energy_24h.txt', 'w') as csv_file:
#        writer = csv.writer(csv_file)
#        for k, v in d.items():
#            writer.writerow([k, v])
#    plt.show()


"""
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
"""

if __name__ == '__main__':
    multi_files(files)
