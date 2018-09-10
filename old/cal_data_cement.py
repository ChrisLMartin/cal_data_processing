# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:47:14 2017

@author: christopher.martin

v2.00

20180910

"""

import argparse
from cal_data_import import append_df_to_excel, data_in, tidy_val_df
from datetime import datetime
import os
import pandas as pd
import sys

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
    s_id = check_name(in_file)
    df_p, df_v, df_vp = data_in(in_file, s_id)
    m_cem = opc_calcs(df_p)
    df_p, df_v = tidy_df(s_id, df_p, df_v, m_cem)
    write_to_excel(s_id, df_p, df_v, df_vp, out_file)
    
def check_name(input_filename):
    '''
    Parameters:
        input_filename: Calmetrix cc2 export TSV file, with filename in the 
            form "/[sample-id]_[xx]degC_Ch[x]_[yyy-mm-dd]_[hh-mm-ss].txt"
            NOTE: DO NOT USE UNDERSCORES IN SAMPLE-ID
            
    Returns:
        sample_id: id from [input_filename], all characters before first 
            underscore
    '''
    
    # Underscores in sample ID cause problems here
    # Check to make sure using geopolymer sample naming system
    sample_id = os.path.basename(input_filename).split('_')[0]
    year = datetime.today().year
    year = str(year)[-2:]
    if not sample_id.startswith(year):
        print('Bad sample id (does not start with {}): {}'.format(year, sample_id))
        sys.exit()
    
    return sample_id 
    

def opc_calcs(df_param_indexed):
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
    
    '''  commented 20180210 after Calmetrix update
    # Remove for cc1 data exported with cc2
    mix_start = datetime.strptime(
            df_param_indexed.loc['Mix Time', 1], "%d-%b-%Y %H:%M:%S")
    log_start = datetime.strptime(
            df_param_indexed.loc['Start Time', 1], "%d-%b-%Y %H:%M:%S")
    time_difference = (log_start - mix_start).total_seconds()
    '''
    # select values from DataFrame and calculate mass of binder in sample
    # may be worth checking if any of these values are 0 at some point in the future
    
    m_water = float(df_param_indexed.loc['Water Mass, g', 1])
    m_cem = float(df_param_indexed.loc['Cement Mass, g', 1])
    m_sample = float(df_param_indexed.loc['Sample Mass, g', 1])
    m_sample_cem = m_sample / (m_cem + m_water) * m_cem
    
    return m_sample_cem


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
