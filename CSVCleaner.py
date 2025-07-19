import os
import csv

def get_header_info(sample_name_in):
    """
    Takes TANAGER Sample Name and returns human readable name, 
    sample type (as material class), locality, and grain size
    """
    sample_name = sample_name_in.strip().upper()
    if 'TS' in sample_name:
        return(
            'Twin Sisters Dunite',
            'Rock',
            'Twin Sisters Mountains',
            'Whole Object'
        )
    if 'TM' in sample_name:
        return(
            'Table Mountain Andesite',
            'Rock',
            'Mount Baker, WA',
            'Whole Object'
        )
    if 'DF' in sample_name:
        return(
            'Dry Falls Basalt',
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if 'FC' in sample_name:
        return(
            'Frenchman Coulee Basalt',
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if 'GR' in sample_name:
        return(
            'Grand Ronde Basalt',
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if 'KD' in sample_name or 'KDT' in sample_name:
        return(
            "Ka'u Desert Trail Basalt",
            'Rock',
            'Hawaii Volcanoes National Park',
            'Whole Object'
        )
    if 'PC' in sample_name or 'PCT' in sample_name:
        return(
            "Puna Coast Trail Basalt",
            'Rock',
            'Hawaii Volcanoes National Park',
            'Whole Object'
        )
    if 'MIT' in sample_name:
        return(
            "Mauna Iki Trail Basalt",
            'Rock',
            'Hawaii Volcanoes National Park',
            'Whole Object'
        )
    if 'CRB' in sample_name:
        return(
            "Columbia River Flood Basalts",
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    return None

def add_row(header, label, value):
    """ Add new row to CSV header; doesn't add empty values (prevents NaN error with VISOR) """
    if value:  # excludes None, empty strings, and False
        header.append([label, value])

def clean(filepath, outputpath):
    """
    Takes TANAGER CSV files and splits them into individual samples to upload.
    Discards garbage and white reference data.
    Only saves preferred viewing geometries.
    """

    os.makedirs(outputpath, exist_ok=True)
    # Skip these entries
    keywords = ['garbage', 'garbabe', 'white reference']
    # Save these entries
    small_diameter_probe = 'i=0 e=0 az=0'
    standard_probe = 'i=12 e=35 az=0'
    key_geometries = [small_diameter_probe, standard_probe, 'i=30 e=-45 az=0', 'i=30 e=-30 az=0', 'i=30 e=0 az=0', 'i=30 e=45 az=0', 'i=45 e=-60 az=0']
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Read all lines
        cell = [line.strip().split(',') for line in f.readlines()] # 2d array of cells [row][col]

        if len(cell) < 2:
            print("File does not have enough rows.")
            return

        row2 = cell[1] # Row of sample names
        row3 = cell[2] # Row of viewing geometries
        cols = len(row2) # Number of columns
        # Find the index of the row where the first column contains "wavelength"
        start_idx = None
        for i, row in enumerate(cell):
            if len(row) > 0 and row[0].strip().lower() == "wavelength":
                start_idx = i
                break
            if start_idx is None:
                continue

        for idx in range(1, cols):
            # Skip any results that contain garbage data
            sample_name = row2[idx].strip().lower()
            if any(kw in sample_name for kw in keywords):
                continue

            # Save only results from preferred Viewing Geometry
            view_geo = row3[idx]
            if any(kg in view_geo for kg in key_geometries):
                outputname = os.path.join(outputpath, f"{sample_name}_{idx}.csv")
                
                header = []

                with open(outputname, 'w', encoding='utf-8', newline='') as out:
                    writer = csv.writer(out)

                    DB_of_Origin = 'TANAGER lab'

                    header_info = get_header_info(sample_name)

                    add_row(header, "Database of origin:", DB_of_Origin)
                    add_row(header, "Sample ID", sample_name)
                    add_row(header, "Original Sample ID", sample_name)
                    add_row(header, "Viewing geometry", view_geo)
                    if header_info:
                        add_row(header, "Sample Name", header_info[0])
                        add_row(header, "Material class", header_info[1])
                        add_row(header, "Locality", header_info[2])
                        add_row(header, "Grain Size", header_info[3])
                    else:
                        print("Error with header")
                    # Both full resolution and abbreviated version available, waiting to hear back which one is preferred
                    resolution = '3 nm @ 700 nm (VNIR, 350-1000 nm), 8 nm @ 1400/2100 nm (SWIR1, 1000-1800 nm / SWIR2, 1800-2500 nm)'
                    resolution_short = '3 nm @ 700 nm and 8 nm @ 1400/2100 nm'
                    add_row(header, "Resolution", resolution)
                    
                    # Add probe type in Other Information
                    probe_type = ""
                    if view_geo == small_diameter_probe:
                        probe_type = "small diameter probe"
                    elif view_geo == standard_probe:
                        probe_type = "handheld probe"
                    else: probe_type = "TANAGER"
                    add_row(header, "Other Information", f"Probe Type: {probe_type}")
                    writer.writerows(header)

                    # Remaining rows
                    for row in cell[start_idx:]: # Starts after the "wavelength" cell
                        col_A = row[0] if len(row) > 0 else ''
                        col_B = row[idx] if len(row) > idx else ''
                        writer.writerow([col_A, col_B])
            else:
                continue
    return outputpath

if __name__ == "__main__":
    input = "./inputs/test.csv"
    output = "./inputs/test1/"

    clean(input, output)
