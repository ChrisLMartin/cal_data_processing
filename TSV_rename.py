# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 17:52:08 2018

@author: christopher.martin
"""

import os

[os.rename(f, f.replace('', '-')) for f in os.listdir('.') if not f.startswith('.')]

import glob, os

def rename(dir, pattern, titlePattern):
    for pathAndFilename in glob.iglob(os.path.join(dir, pattern)):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        os.rename(pathAndFilename, 
                  os.path.join(dir, titlePattern % title + ext))

# You could then use it in your example like this:

rename(r'c:\temp\xx', r'*.doc', r'new(%s)')