# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 14:08:19 2018

@author: christopher.martin
"""

from cal_data_cement import data_in, opc_calcs
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference, Series


in_file = "../cal_data/2018-03/1802-0269-P06-2_23degC_Ch08_2018-03-19_15-11-41.txt"

s_id, df_p, df_v, df_vp = data_in(in_file)
df_p, df_v = opc_calcs(s_id, df_p, df_v)
    
wb = Workbook()
ws = wb.active
cs = wb.create_chartsheet()

columns = df_v.columns.tolist()
values = df_v.values.tolist()

ws.append(columns)
for row in values:
    ws.append(row)

chart = LineChart()
labels = Reference(ws)

    
wb.save("test.xlsx")
