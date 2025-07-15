"""
Load excel files from a directory and ingest them into a database.

Find directory
Load excel files
    Format data
        Split into columns
        Save CSV into output folder
    Assign Sample type
    Assign Sample ID
Ingest data into database

"""


import xlrd
import csv
import pandas as pd
from decimal import Decimal
import os
from CSVCleaner import clean
os.makedirs("output", exist_ok=True)

input_dir = "./inputs/"


# Load your Excel file
df = pd.read_excel('your_file.xlsx')  # replace with your actual filename

# Loop through columns from the 2nd to the last
for col in df.columns[1:]:
    new_df = df[[df.columns[0], col]]  # column 1 and current column
    new_df.to_csv(f'{col}_split.csv', index=False)  # save as CSV
