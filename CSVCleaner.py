import os

def get_header_info(sample_name):
    """
    Takes TANAGER Sample Name and returns human readable name, 
    sample type (as material class), locality, and grain size
    """
    header_info = []
    if sample_name == 'TS':
        header_info[0] = 'Twin Sisters Dunite'
        header_info[1] = 'Rock'
        header_info[2] = ''
        header_info[3] = 'Whole Object'
    if sample_name == 'TM':
        header_info[0] = 'Table Mountain Andesite'
        header_info[1] = 'Rock'
        header_info[2] = 'Mount Baker, WA'
        header_info[3] = 'Whole Object'
    if sample_name == 'DF':
        header_info[0] = 'Dry Falls Basalt'
        header_info[1] = 'Rock'
        header_info[2] = 'Columbia River Flood Basalts'
        header_info[3] = 'Whole Object'
    if sample_name == 'FC':
        header_info[0] = 'Frenchman Coulee Basalt'
        header_info[1] = 'Rock'
        header_info[2] = 'Columbia River Flood Basalts'
        header_info[3] = 'Whole Object'
    if sample_name == 'GR':
        header_info[0] = 'Grand Ronde Basalt'
        header_info[1] = 'Rock'
        header_info[2] = 'Columbia River Flood Basalts'
        header_info[3] = 'Whole Object'
    if sample_name == 'KD' or 'KDT':
        header_info[0] = "Ka'u Desert Trail Basalt"
        header_info[1] = 'Rock'
        header_info[2] = 'Hawaii Volcanoes National Park'
        header_info[3] = 'Whole Object'
    if sample_name == 'PC' or 'PCT':
        header_info[0] = "Puna Coast Trail Basalt"
        header_info[1] = 'Rock'
        header_info[2] = 'Hawaii Volcanoes National Park'
        header_info[3] = 'Whole Object'
    if sample_name == 'MIT':
        header_info[0] = "Mauna Iki Trail Basalt"
        header_info[1] = 'Rock'
        header_info[2] = 'Hawaii Volcanoes National Park'
        header_info[3] = 'Whole Object'
    if sample_name == 'CRB':
        header_info[0] = "Columbia River Flood Basalts"
        header_info[1] = 'Rock'
        header_info[2] = 'Columbia River Flood Basalts'
        header_info[3] = 'Whole Object'
    return header_info

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
    key_geometries = ['i=30 e=-45 az=0', 'i=30 e=-30 az=0', 'i=30 e=0 az=0', 'i=30 e=45 az=0', 'i=45 e=-60 az=0']
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Read all lines
        cell = [line.strip().split(',') for line in f.readlines()]

        # Grab row 2 
        if len(cell) < 2:
            print("File does not have enough rows.")
            return

        row2 = cell[1]
        row3 = cell[2]
        cols = len(row2)

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
                def add_row(label, value):
                    if value:  # excludes None, empty strings, and False
                        header.append([label, value])

                with open(outputname, 'w', encoding='utf-8') as out:
                    # Row 1 (Database of Origin)
                    col_A_header = cell[0][0] if len(cell[0]) > 0 else ''
                    col_B_header = cell[0][1] if len(cell[0]) > 0 else ''
                    out.write(f"{col_A_header},{col_B_header}\n")
                    header_info = get_header_info(sample_name)
                    add_row("Sample ID", sample_name)
                    add_row("Original Sample ID", sample_name)
                    add_row("Sample Name", header_info[0])
                    add_row("Material class", header_info[1])
                    add_row("Locality", header_info[2])
                    add_row("Grain Size", header_info[3])
                    resolution = ''
                    add_row("Resolution", resolution)
                    out.writerows(header)

                    # Remaining rows
                    for row in cell[2:]:
                        col_A = row[0] if len(row) > 0 else ''
                        col_B = row[idx] if len(row) > idx else ''
                        out.write(f"{col_A},{col_B}\n")
            else:
                continue

def print(filepath):
    # Print each cell in row 2
    for idx, value in enumerate(row2, start=1):
        val = value.strip().lower()
        if not any (kw in val for kw in keywords):
            print(f"Column {idx}: {value}")

if __name__ == "__main__":
    input = "./inputs/test.csv"
    output = "./inputs/test1/"

    clean(input, output)
