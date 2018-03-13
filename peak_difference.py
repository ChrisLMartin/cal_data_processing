# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:32:28 2018

@author: christopher.martin
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import splrep, splev


def find_derivative(input_file, sheet):
    df = pd.read_excel(input_file, sheetname=sheet, skiprows=2)
    data = df[['Tmix,s', 'Power/Cement,W/g']].values
    t = data[:,0][120:]
    s1 = data[:,1][120:]
    spl = splrep(t, s1, k=5, s=10**-9)
    
    d2 = splev(t, spl, der=2)
#    highest_peak = np.argmax(s1)
    inflection_point = np.where(d2==0)
#    print(highest_peak, inflection_point)
    return t, s1

xl_filename = 'CalorimetryDataOPCAutomated.xlsx'
xl_sheet = '1712-0143-P06-2'

t, s1 = find_derivative(xl_filename, xl_sheet)

fig, ax = plt.subplots()

#def two_scales(ax1, time, data1, data2, c1, c2):
#    """
#    Parameters
#    ----------
#    ax : axis
#        Axis to put two scales on
#    time : array-like
#        x-axis values for both datasets
#    data1: array-like
#        Data for left hand scale
#    data2 : array-like
#        Data for right hand scale
#    c1 : color
#        Color for line 1
#    c2 : color
#        Color for line 2
#    Returns
#    -------
#    ax : axis
#        Original axis
#    ax2 : axis
#        New twin axis
#    """
#    hour_time = time / 3600
#    
#    ax2 = ax1.twinx()
#    
#    ax1.plot(hour_time, data1, color=c1)
#    ax1.set_xlabel('time (h)')
#    ax1.set_ylabel('data')
#
#    ax2.plot(hour_time, data2, color=c2)
#    ax2.set_ylabel('first der')
#    return ax1, ax2
#

#
## Create axes
#fig, ax = plt.subplots()
#ax1, ax2 = two_scales(ax, t, splev(t, s1), splev(t, s1, der=2), 'r', 'b')
#
## Change color of each axis
#def color_y_axis(ax, color):
#    """Color your axes."""
#    for t in ax.get_yticklabels():
#        t.set_color(color)
#    return None
#color_y_axis(ax1, 'r')
#color_y_axis(ax2, 'b')
#plt.show()

#if __name__ == '__main__':
#     find_derivative(xl_filename, xl_sheet)