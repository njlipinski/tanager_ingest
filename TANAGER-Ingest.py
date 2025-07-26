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

def upload(filename):
    print(filename)

if __name__ == "__main__":
    # Grab folders from drive -- if it isn't in PROCESSED.txt, or IGNORE.txt
    drive_folder = "G:/.shortcut-targets-by-id/1Kk3263MO82bp4TH5a619NNfT7gl5nYWq/processed_spectra"
    base_output = "./output/"
    os.makedirs(base_output, exist_ok=True)

    # keywords to skip
    keywords = [
        "scratch", 
        "bad", 
        "recon", 
        "test", 
        "testing", 
        "tests", 
        "training", 
        "troubleshooting", 
        "troubleshoot", 
        "check",
        "validation", 
        "repeatability", 
        "recalibration"
        ]

    # iterate thru Google Drive folder
    for root, dirs, files in os.walk(drive_folder):
        folder_name = os.path.basename(root)

        if root == drive_folder:
            continue

        folder_name_lower = folder_name.lower()
        if any (keyword in folder_name_lower for keyword in keywords):
            print(f"Skipping folder: {folder_name}")
            continue

        csv_files = [f for f in files if f.lower().endswith('.csv')]

        if csv_files:
            output_subfolder = os.path.join(base_output, folder_name)
            os.makedirs(output_subfolder, exist_ok=True)

            for csv_file in csv_files:
                input_path = os.path.join(root, csv_file)

                try:
                    # clean file
                    filename = clean(input_path, output_subfolder)
                    # Upload to VISOR
                    upload(filename)

                except Exception as e:
                    print(f"Error processng {csv_file}")

    # place file into input with any necessary data
    # Record what folder you grabbed in PROCESSED.txt
        
    print("complete")

