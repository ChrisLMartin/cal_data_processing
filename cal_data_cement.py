# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:47:14 2017

@author: christopher.martin

v1.01
"""

import argparse
from cal_data_import import append_df_to_excel, multi_cal_files
from datetime import datetime
import os
import pandas as pd

# Excel workbook path and filename. If a filename only is called from command
# line, output will be in the same directory as .txt files used as arguments.
# Takes too long running on the network
output_excel_filename = 'CalorimetryDataOPCAutomated.xlsx'
output_excel_location = os.path.normpath('S:/Current Projects/R&D/{}'.format(output_excel_filename))
#output_excel_location = os.path.normpath('C:/Users/christopher.martin/Documents/Python/cal_data_processing/{}'.format(output_excel_filename))

# Parse command line file arguments, used with .bat file for drag and drop
parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]


def cal_data_to_excel(input_filename, output_filename=output_excel_location):
    # Tab delimited cal data file location for pandas to read
    # may be worth converting all cal files held in script directory,
    # or selecting only files that haven't been converted
    # network directory "//ICAL8000/Users/Public/Documents/Calmetrix/CalCommander 2/Export/YYYY-MM/"

    # import data from file, and split parameters from recorded data.
    # Encoding set to latin1 due to presence of degree symbol in data
    df_param = pd.read_table(input_filename, nrows=29, encoding="latin1", header=None)
    df_val = pd.read_table(input_filename, skiprows=29)

    # make parameter names the index
    df_param_indexed = df_param.set_index(0)

#    Create small paramters for top of value sheet, to be used in excel graphs, per RG request 20180111
    d1 = {1 : pd.Series(['', ''], index=['Sample ID', 'Label'])}
    df_val_params = pd.DataFrame(d1)
    df_val_params.loc['Sample ID', 1] = df_param_indexed.loc['Sample ID', 1]
    df_val_params.loc['Label', 1] = df_param_indexed.loc['Sample ID', 1]

   

    # Calculate time from mix
    # Remove for cc1 data exported with cc2
    mix_time = datetime.strptime(df_param_indexed.loc['Mix Time', 1], "%d-%b-%Y %H:%M:%S")
    start_time = datetime.strptime(df_param_indexed.loc['Start Time', 1], "%d-%b-%Y %H:%M:%S")
    time_difference = (start_time - mix_time).total_seconds()

    # select values from DataFrame and calculate mass of binder in sample
    # may be worth checking if any of these values are 0 at some point in the future
    
    m_water = float(df_param_indexed.loc['Water Mass, g', 1])
    m_cem = float(df_param_indexed.loc['Cement Mass, g', 1])
    m_sample = float(df_param_indexed.loc['Sample Mass, g', 1])
    m_sample_cem = m_sample / (m_cem + m_water) * m_cem
    
    # add columns to df with power and energy per cement
    # create time in decimal days for RG charts 20180111
    # header names require numbers for cc1 data exported with cc2
    df_val['Power/Cement,W/g'] = df_val['Power,W'].values / m_sample_cem
    df_val['Heat/Cement,J/g'] = df_val['Heat,J'].values / m_sample_cem
    df_val['Tmix,s'] = df_val['Tlog,s'].values - time_difference
    df_val['Tmix,days'] = df_val['Tmix,s'].values / 86400 # 60 * 60 * 24
    df_val.drop('Tlog,s', axis=1, inplace=True) # remove for cc1 data exported with cc2
    
#    rearrange columns to place Tmixs first 
    cols = df_val.columns.tolist()
    cols = cols[-2:] + cols[:-2]
#    cols = cols[0:1] + cols[-1:] + cols[1:-1] # For cc1 data exported with cc2
    df_val = df_val[cols]

    param_sheet = 'Parameters'
    sample_id = df_param_indexed.loc['Sample ID', 1]
#    add link to each sheet in excel on paramters sheet, goes to label cell B2 20180111
    d2 = {1 : pd.Series('=HYPERLINK("[{}]\'{}\'!B2", "Sheet")'.format(output_excel_filename, sample_id), index=['Link'])}
    df_param_link = pd.DataFrame(d2)
    df_param_indexed_transpose = df_param_link.append(df_param_indexed).transpose()

    # try to open existing workbook: File not found -> create, add parameter sheet with header, add value sheet
    # if file is found, check if current sample exists; if not, write parameters without header, add value   
    try:
        df_existing_param = pd.read_excel(output_filename, sheet_name=param_sheet)
        if sample_id not in df_existing_param.values:
            append_df_to_excel(output_filename, df_param_indexed_transpose, param_sheet, index=False, header=False)
        else:
            print('A parameter row with Sample ID {} already exists in this workbook. From {}'.format(sample_id, input_filename))
    except FileNotFoundError:
        append_df_to_excel(output_filename, df_param_indexed_transpose, param_sheet, index=False)
        pass

    wb = pd.ExcelFile(output_filename)

    if sample_id not in wb.sheet_names:
        append_df_to_excel(output_filename, df_val_params, sample_id, header=False)
        append_df_to_excel(output_filename, df_val, sample_id, index=False)
    else:
        print('A values sheet with Sample ID {} already exists in this workbook. From {}'.format(sample_id, input_filename))
        pass


if __name__ == '__main__':
    multi_cal_files(files)
