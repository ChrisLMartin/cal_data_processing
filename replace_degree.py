# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 11:26:00 2018

@author: christopher.martin
"""

import os


def replace_degree_symbol():
    paths = (os.path.join(root, filename)
            for root, _, filenames in os.walk('C:/Users/christopher.martin/Documents/Python/cal_data/2018-05')
            for filename in filenames)
    
    for path in paths:
        newname = path.replace('°', 'deg')
        if newname != path:
            os.rename(path, newname)
        
if __name__ == '__main__':
    replace_degree_symbol()