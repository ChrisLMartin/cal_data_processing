# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:47:14 2017

@author: christopher.martin

v1.01
"""

import argparse
from cal_data_import import append_df_to_excel, query_yes_no
from datetime import datetime
import numpy as np
import os
import pandas as pd

#pd.options.mode.chained_assignment = None

# Excel workbook path and filename. If a filename only is called from command
# line, output will be in the same directory as .txt files used as arguments.
output_excel_filename = 'CalorimetryData2018Automated.xlsx'
# output_excel_location = os.path.normpath('S:/Current Projects/R&D/{}'.format(output_excel_filename))
output_excel_location = os.path.normpath(
        'C:/Users/christopher.martin/Documents/Python/cal_data/{}'.format(output_excel_filename))

# Parse command line file arguments, used with .bat file for drag and drop
parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]


def multi_cal_files(file_list, output_filename=output_excel_location):

    for file in file_list:
        main(file, output_filename)
        
def main(in_file, out_file):
    s_id, df_p, df_v, df_vp = data_in(in_file)
    df_p, df_v = efc_calcs(s_id, df_p, df_v)
    write_to_excel(s_id, df_p, df_v, df_vp, out_file)

def data_in(input_filename):
    # Tab delimited cal data file location for pandas to read
    # may be worth converting all cal files held in script directory,
    # or selecting only files that haven't been converted
    sample_id = os.path.basename(input_filename).split('_')[0]
    print('Processing sample {}'.format(sample_id))
    # import data from file, and split parameters from recorded data.
    # Encoding set to latin1 due to presence of degree symbol
    df_param = pd.read_table(input_filename, 
                             nrows=29, 
                             encoding="latin1", 
                             header=None)
    df_val = pd.read_table(input_filename, skiprows=29)

    # make parameter names the index
    df_param_indexed = df_param.set_index(0)
#    redundant due to parsing sample id from filename
#    sample_id = df_param_indexed.loc['Sample ID', 1]
    
#    Create small paramters for top of value sheet, to be used in excel graphs, per RG request 20180111
    d1 = {1 : pd.Series(['', ''], index=['Sample ID', 'Label'])}
    df_val_params = pd.DataFrame(d1)
    df_val_params.loc['Sample ID', 1] = sample_id
    df_val_params.loc['Label', 1] = sample_id

    return (sample_id, df_param_indexed, df_val, df_val_params)


def efc_calcs(sample_id, df_param_indexed, df_val): 
    # Remove for cc1 data exported with cc2
    mix_start = datetime.strptime(
            df_param_indexed.loc['Mix Time', 1], "%d-%b-%Y %H:%M:%S")
    log_start = datetime.strptime(
            df_param_indexed.loc['Start Time', 1], "%d-%b-%Y %H:%M:%S")
    time_difference = (log_start - mix_start).total_seconds()

    # select values from DataFrame and calculate mass of binder in sample
    # may be worth checking if any of these values are 0 at some point in the future
    m_slag = float(df_param_indexed.loc['Suppl 1 Mass, g', 1])
    m_fa = float(df_param_indexed.loc['Suppl 2 Mass, g', 1])
    m_water = float(df_param_indexed.loc['Water Mass, g', 1])
    m_agg = float(df_param_indexed.loc['Aggr Mass, g', 1])
    m_sample = float(df_param_indexed.loc['Sample Mass, g', 1])
    m_sample_scm = m_sample / (m_slag + m_fa + m_water + m_agg) * (m_slag + m_fa)
    
    # Set values to 0 prior to isothermal
    # look from min_search_start minutes to min_search_end minutes
    min_search_start = 60 
    min_search_end = 600
    idx_min = np.argmin(
            df_val['Power,W'].values[min_search_start:min_search_end]) + min_search_start
    if idx_min >= 599:
        idx_min = 0
    df_val = df_val[idx_min:]
    df_val['Heat,J'] = df_val['Heat,J'].apply(lambda x: x - df_val['Heat,J'].values[0])
    
    # add columns to df with power and energy per SCM
    # create time in decimal days for RG charts 20180111
    # header names require numbers for cc1 data exported with cc2
    print('Applying calculations to values.')
    df_val['Power/SCM,W/g'] = df_val['Power,W'].values / m_sample_scm
    df_val['Heat/SCM,J/g'] = df_val['Heat,J'].values / m_sample_scm
    df_val['Tmix,s'] = df_val['Tlog,s'].values - time_difference
    df_val['Tmix,days'] = df_val['Tmix,s'].values / 86400 # 60 * 60 * 24
    df_val = df_val.drop('Tlog,s', axis=1) # remove for cc1 data exported with cc2

    
#    rearrange columns to place Tmixs first 
    print('Rearranging values columns.')
    cols = df_val.columns.tolist()
    cols = cols[-2:] + cols[:-2]
#    cols = cols[0:1] + cols[-1:] + cols[1:-1] # For cc1 data exported with cc2
    df_val = df_val[cols]

#    add link to each sheet in excel on paramters sheet, goes to label cell B2 20180111
    print('Adding excel sheet hyperlink to parameter row.')
    d2 = {1 : pd.Series(
            '=HYPERLINK("[{}]\'{}\'!B2", "Sheet")'.format(
                    output_excel_filename, sample_id), index=['Link'])}
    df_param_link = pd.DataFrame(d2)
    df_param_indexed_transpose = df_param_link.append(
            df_param_indexed).transpose()

    return (df_param_indexed_transpose, df_val)


def write_to_excel(sample_id, 
                   df_param_indexed_transpose, 
                   df_val, 
                   df_val_params, 
                   output_filename=output_excel_location):
    
    param_sheet = 'Parameters'

    # try to open existing workbook: File not found -> create, add parameter sheet with header, add value sheet
    # if file is found, check if current sample exists; if not, write parameters without header, add value   
    try:
        print('Trying to open workbook {}.'.format(output_filename))
        df_existing_param = pd.read_excel(output_filename, 
                                          sheet_name=param_sheet)
        if sample_id not in df_existing_param.values:
            print('Writing parameters {}.'.format(sample_id))
            start_action = datetime.now()
            append_df_to_excel(output_filename, 
                               df_param_indexed_transpose, 
                               param_sheet, 
                               index=False, 
                               header=False)
            stop_action = datetime.now()
            duration = stop_action - start_action
            print('Duration: {} seconds.'.format(duration.total_seconds()))
        else:
            #should add check that there aren't already multiple paramter rows with same id, which can
            #occur if the filename and sample id in file don't match (filename manually changed)
            idx_sample_id = df_existing_param.index[df_existing_param[
                    'Sample ID'] == sample_id][0]
            print(
                'A parameter row with Sample ID {} already exists in this workbook.'.format(sample_id))
            overwrite_parameter = query_yes_no(
                    'Do you want to overwrite this parameter row?')
            if overwrite_parameter:
                print('Overwriting parameters {}.'.format(sample_id))
                start_action = datetime.now()
                append_df_to_excel(output_filename, 
                                   df_param_indexed_transpose, 
                                   param_sheet, 
                                   startrow=idx_sample_id+1, 
                                   index=False, 
                                   header=False)
                stop_action = datetime.now()
                duration = stop_action - start_action
                print('Duration: {} seconds.'.format(duration.total_seconds()))
    except FileNotFoundError:
        print('Creating workbook {}.'.format(output_filename))
        append_df_to_excel(output_filename, 
                           df_param_indexed_transpose, 
                           param_sheet, 
                           index=False)
        pass

    wb = pd.ExcelFile(output_filename)

    if sample_id not in wb.sheet_names:
        print('Writing values sheet {}.'.format(sample_id))
        start_action = datetime.now()
        append_df_to_excel(output_filename, 
                           df_val_params, 
                           sample_id, 
                           header=False)
        append_df_to_excel(output_filename, 
                           df_val, 
                           sample_id, 
                           index=False)
        stop_action = datetime.now()
        duration = stop_action - start_action
        print('Duration: {}'.format(duration.total_seconds()))
    else:
        print('A values sheet with Sample ID {} already exists in this workbook.'.format(sample_id))
        overwrite_sheet = query_yes_no('Do you want to overwrite this values sheet?')
        if overwrite_sheet:
            print('Overwriting values sheet {}.'.format(sample_id))
            start_action = datetime.now()
            append_df_to_excel(output_filename, 
                               df_val_params, 
                               sample_id, 
                               startrow=0, 
                               header=False)
            append_df_to_excel(output_filename, 
                               df_val, 
                               sample_id, 
                               startrow=2, 
                               index=False)
            stop_action = datetime.now()
            duration = stop_action - start_action
            print('Duration: {}'.format(duration.total_seconds()))
            

if __name__ == '__main__':
    multi_cal_files(files)
