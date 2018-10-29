# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 15:43:08 2018

@author: christopher.martin
"""

#from binascii import hexlify
#import sys

file_path = "log_test/1809-0187-P80_23degC_Ch01_2018-10-03_11-37-17.cc2log"



with open(file_path, "rb") as f, open("./test1.txt", "wb") as g:
    for line in f:
        g.write(line.replace(b'\x7f\xff\xff\xff', b'\n').replace(b'\x00\x00\x00', b'\n'))

with open("./test1.txt", "rb") as f:
    for line in f:
        print(line)
        
#with open(file_path, "rb") as f:
#    byte = f.read(1)
#    byte_string = b''
#    while byte:
#        if byte == b'\n':
#            print(byte_string)
#        else:
#            byte_string += byte
#        byte = f.read(1)
    

#with open(file_path, "rb") as f:
#    for line in f:
#        for byte in line:
#            print(byte, end=' ')
#        print()
        
#with open(file_path, "r", encoding="mbcs") as f:
#    for line in f:
#        try:
#            print(line)
#        except UnicodeEncodeError as uni_e:
#            print(uni_e, file=sys.stderr)
#            continue
            
#    byte = f.read(1)
#    hexadecimal = binascii.hexlify(byte)