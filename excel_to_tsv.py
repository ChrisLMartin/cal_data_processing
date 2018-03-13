# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 20:35:48 2018

@author: christopher.martin
"""

#import argparse
import pandas as pd


#parser = argparse.ArgumentParser()
#parser.add_argument('parameters', nargs=3)
#args = parser.parse_args()
#files = list(vars(args).values())

xl_input = 'CalorimetryData2018Automated.xlsx'
# xl_location = os.path.normpath('C:/Users/christopher.martin/Documents/Python/cal_data_processing/{}'.format(xl_name))
xl_sheet = '20171213-02'
tsv_output = xl_sheet + '.tsv'

def excel_to_tsv(xl_input, xl_sheet, tsv_output):
    df = pd.read_excel(xl_input, sheetname=xl_sheet, skiprows=2)
    df.to_csv(tsv_output, sep='\t',  index=False)
    
#if __name__ == '__main__':
#    excel_to_tsv(files)