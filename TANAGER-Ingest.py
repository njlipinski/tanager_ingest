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

def upload(filename):
    print(filename)

if __name__ == "__main__":
    input = "./inputs/test.csv"
    output = "./output/"

    # Grab folder from drive -- if it isn't in PROCESSED.txt, or IGNORE.txt
    # place file into input with any necessary data
    # Record what folder you grabbed in PROCESSED.txt
    # Clean the file
    filename = clean(input, output)
    # Upload to VISOR
    upload(filename)

