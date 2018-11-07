# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 10:14:20 2018

@author: christopher.martin
"""

import datetime
import pandas as pd

# Set excel shrinkage spreadsheet path
path_in = "S:\Current Projects\R&D\Shrinkage.xlsx"
# Read records into pandas dataframe
df = pd.read_excel(path_in, "Records", index_col="Reading ID")
# Select only relevant columns
df = df[["Mix", "Specimen"]]
# Duplicate Mix column to be used for date
df["Date"] = df["Mix"]
# Convert date column to datetime objects
df["Date"] = pd.to_datetime(df["Date"].astype(str).str[:8], format='%Y%m%d')
# Convert datetime objects to dates
df["Date"] = df["Date"].dt.date
# Combine Mix and Specimen columns into single column of strings
df["SpecimenID"] = df["Mix"].astype(str) + df["Specimen"]
# Drop Mix and Specimen columns
df = df[["SpecimenID", "Date"]]
# Drop all duplicate rows
df = df.drop_duplicates("SpecimenID")
# Create array of test days
days = [x for x in range(1, 15)] + \
    [y for y in range(16, 29, 2)] + \
    [z for z in range(35, 57, 7)]
dates = [datetime.date.today() - datetime.timedelta(x) for x in days]
# Filter for samples within previous 56 days
df = df[df["Date"].isin(dates)]
# Set output path for CSV
path_out = "S:\Current Projects\R&D\ShrinkageCSV.csv"
# Create CSV
df["SpecimenID"].to_csv(path_out, index=False)
