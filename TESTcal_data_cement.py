# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:47:14 2017

@author: christopher.martin

v1.01
"""

import argparse
from cal_data_import import append_df_to_excel
from datetime import datetime
import numpy as np
import os
import pandas as pd
#import sys

# Excel workbook path and filename. If a filename only is called from command
# line, output will be in the same directory as .txt files used as arguments.
# Takes too long running on the network
output_excel_filename = 'CalorimetryDataOPCAutomated.xlsx'
#output_excel_location = os.path.normpath('S:/Current Projects/R&D/{}'.format(output_excel_filename))
output_excel_location = os.path.normpath('C:/Users/christopher.martin/Documents/Python/cal_data_processing/{}'.format(output_excel_filename))

# Parse command line file arguments, used with .bat file for drag and drop
parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='*')
args = parser.parse_args()
files = list(vars(args).values())[0]

def multi_cal_files(file_list, output_filename=output_excel_location):
    '''
    Takes a [file_list] of Calmetrix cc2 export TSV files and calls data import 
    function on each file, with results saved to excel workbook at 
    [output_filename].
    
    Parameters:
        file_list: list of Calmetrix cc2 export TSV files, with filenames in 
            the form "/[sample-id]_[xx]degC_Ch[x]_[yyy-mm-dd]_[hh-mm-ss].txt"
            NOTE: DO NOT USE UNDERSCORES IN SAMPLE-ID
        output_filename: excel workbook "*.xlsx". 
            Default: output_excel_location
    Returns: None
    '''
    for file in file_list:
        main(file, output_filename)
        
        
def main(in_file, out_file):
    '''
    Takes an [in_file] of type Calmetrix cc2 export TSV and runs data import, 
    with results saved to excel workbook at [out_file].
    
    Parameters:
        in_file: Calmetrix cc2 export TSV file, with filename in the form
            "/[sample-id]_[xx]degC_Ch[x]_[yyy-mm-dd]_[hh-mm-ss].txt"
            NOTE: DO NOT USE UNDERSCORES IN SAMPLE-ID
        out_file: excel workbook "[name].xlsx"
    Returns: None
    '''
    s_id, df_p, df_v, df_vp = data_in(in_file)
    df_p, df_v = opc_calcs(s_id, df_p, df_v)
    write_to_excel(s_id, df_p, df_v, df_vp, out_file)
    
    
def data_in(input_filename):
    '''
    Reads data from [input_filename] of type Calmetrix cc2 export TSV into
    pandas DataFrames.
    
    Parameters:
        input_filename: Calmetrix cc2 export TSV file, with filename in the 
        form "/[sample-id]_[xx]degC_Ch[x]_[yyy-mm-dd]_[hh-mm-ss].txt"
        NOTE: DO NOT USE UNDERSCORES IN SAMPLE-ID
    Returns:
        sample_id: id from [input_filename], all characters before first 
            underscore
        df_param_indexed: long df of mix parameters, with parameter names as 
            index. If newlines have been used in any field of CC2 logger 
            details fields, there will be problems reading in to df_param and 
            df_val
        df_val: df of all recorded time, power, and energy values
        df_val_params: df with sample id for first rows of excel sheets, to 
            allow simpler excel graphing and annotation
    '''
    # Underscores in sample ID cause problems here
    # Check to make sure using geopolymer sample naming system
    sample_id = os.path.basename(input_filename).split('_')[0]
    '''TEST THIS
    year = datetime.today().year
    if not sample_id.startswith(str(year)):
        print('Bad sample id (does not start with {}): {}'.format(year, sample_id))
        sys.exit()
        '''
    print('Processing sample {}'.format(sample_id))
    # Encoding set to latin1 due to presence of degree symbol
    # newlines in CC2 logger details fields will cause issues
    df_param = pd.read_table(input_filename, 
                             nrows=29, 
                             encoding="latin1", 
                             header=None)
    df_val = pd.read_table(input_filename, skiprows=29)
    df_param_indexed = df_param.set_index(0)
#    redundant due to parsing sample id from filename
#    sample_id = df_param_indexed.loc['Sample ID', 1]
    
    d1 = {1 : pd.Series(['', ''], index=['Sample ID', 'Label'])}
    df_val_params = pd.DataFrame(d1)
    df_val_params.loc['Sample ID', 1] = sample_id
    df_val_params.loc['Label', 1] = sample_id

    return (sample_id, df_param_indexed, df_val, df_val_params)


def opc_calcs(sample_id, df_param_indexed, df_val):
    '''
    Takes [sample_id] and copies of [df_param_indexed] and [df_val] from 
    data_in() and removes data prior to isothermal (first local minimum), 
    calculates specific power and energy values, and adds a hyperlink to the
    excel parameter row for easier navigation between sheets.
    
    Parameters:
        sample_id: from data_in(), id of calorimetry sample
        df_param_indexed: df of mix parameters, with parameter names as index
        df_val: df of all recorded time, power, and energy values
    Returns:
        df_param_indexed_transpose: wide df of parameters, with excel hyperlink
            for worksheet navigation
        df_val: df of calorimetry values, starting from isothermal (if found)
            with energy and power values per mass of binder
    '''
    df_param_indexed = df_param_indexed.copy()
    df_val = df_val.copy()
    
    # Remove for cc1 data exported with cc2
    mix_start = datetime.strptime(
            df_param_indexed.loc['Mix Time', 1], "%d-%b-%Y %H:%M:%S")
    log_start = datetime.strptime(
            df_param_indexed.loc['Start Time', 1], "%d-%b-%Y %H:%M:%S")
    time_difference = (log_start - mix_start).total_seconds()

    # select values from DataFrame and calculate mass of binder in sample
    # may be worth checking if any of these values are 0 at some point in the future
    
    m_water = float(df_param_indexed.loc['Water Mass, g', 1])
    m_cem = float(df_param_indexed.loc['Cement Mass, g', 1])
    m_sample = float(df_param_indexed.loc['Sample Mass, g', 1])
    m_sample_cem = m_sample / (m_cem + m_water) * m_cem
    
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


#    sample_id = df_param_indexed.loc['Sample ID', 1]
#    add link to each sheet in excel on paramters sheet, goes to label cell B2 20180111
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
    '''
    Takes [sample_id] from data_in(), [df_param_indexed_transpose], [df_val], 
    and [df_val_params] from efc_calcs(), and [output_filename] from main().
    Writes [df_param_indexed_transpose] to [param_sheet], and [df_val] and 
    [df_val_params] to spreadsheet titled [sample_id] in [output_filename].
    Checks if workbook, sheets, and entries exist prior to writing, prompts to
    replace.
    
    Parameters:
        sample_id: from data_in(), id of calorimetry sample
        df_param_indexed_transpose: wide df of mix parameters
        df_val: df of calorimetry values
        df_val_params: df with sample id for first rows of excel sheets
        output_filename:  excel workbook "*.xlsx". 
            Default: output_excel_location
    Returns: None
    '''
    param_sheet = 'Parameters'

    # try to open existing workbook: File not found -> create, add parameter sheet with header, add value sheet
    # if file is found, check if current sample exists; if not, write parameters without header, add value   
    try:
        df_existing_param = pd.read_excel(output_filename, sheet_name=param_sheet)
        if sample_id not in df_existing_param.values:
            print('Writing parameters')
            append_df_to_excel(output_filename, df_param_indexed_transpose, param_sheet, index=False, header=False)
        else:
            print('A parameter row with Sample ID {} already exists in this workbook.'.format(sample_id))
    except FileNotFoundError:
        print('Writing parameters')
        append_df_to_excel(output_filename, df_param_indexed_transpose, param_sheet, index=False)
        pass

    wb = pd.ExcelFile(output_filename)

    if sample_id not in wb.sheet_names:
        print('Writing values')
        append_df_to_excel(output_filename, df_val_params, sample_id, header=False)
        append_df_to_excel(output_filename, df_val, sample_id, index=False)
    else:
        print('A values sheet with Sample ID {} already exists in this workbook.'.format(sample_id))
        pass


if __name__ == '__main__':
    multi_cal_files(files)
