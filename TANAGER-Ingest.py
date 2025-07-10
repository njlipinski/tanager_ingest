"""
Load excel files from a directory and ingest them into a database.

Find directory
Load excel files
Format data
    Split into columns
    Save CSV into output folder
Ingest data into database

"""


import xlrd
import csv
from decimal import Decimal
import os
os.makedirs("output", exist_ok=True)

input_dir = "./inputs/"