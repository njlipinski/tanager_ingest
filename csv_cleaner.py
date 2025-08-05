import os
import csv
import rocks_minerals

def hardcoded_values(sample_name):
    if sample_name == "906165_flush_si510" or sample_name == "906167_0.2mm_indent_si510":
        return(
            "XRD sample holder",
            "Reference"
        )

def matches_acronym(sample_name, acronyms):
    """
    Check if sample_name contains any acronym with '_', '-', or ' ' as suffix.
    """
    for acronym in acronyms:
        for suffix in ('_', '-', ' '):
            if f"{acronym}{suffix}" in sample_name:
                return True
    return False

def get_header_info(sample_name_in):
    """
    Takes TANAGER Sample Name and returns human readable name, 
    sample type (as material class), locality, and grain size
    """
    sample_name = sample_name_in.strip().upper()

    if matches_acronym(sample_name, ['TS']):
        return(
            'Twin Sisters Dunite',
            'Rock',
            'Twin Sisters Mountains',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['TM']):
        return(
            'Table Mountain Andesite',
            'Rock',
            'Mount Baker, WA',
            'Whole Object'
        )
    # currently APA unused
    if matches_acronym(sample_name, ['APA']):
        return(
            "Artist Point Andesite",
            'Rock',
            'Mount Baker, WA',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['DF']):
        return(
            'Dry Falls Basalt',
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['FC']):
        return(
            'Frenchman Coulee Basalt',
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['GB']):
        return(
            'Grand Ronde Basalt',
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['SM']):
        return(
            "Saddle Mountain",
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['KD','KDT']):
        return(
            "Ka'u Desert Trail Basalt",
            'Rock',
            'Hawaii Volcanoes National Park',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['PC','PCT']):
        return(
            "Puna Coast Trail Basalt",
            'Rock',
            'Hawaii Volcanoes National Park',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['MIT']):
        return(
            "Mauna Iki Trail Basalt",
            'Rock',
            'Hawaii Volcanoes National Park',
            'Whole Object'
        )
    if matches_acronym(sample_name, ['CRB']):
        return(
            "Columbia River Flood Basalts",
            'Rock',
            'Columbia River Flood Basalts',
            'Whole Object'
        )
    return None

def get_sample_type_mods(filepath, sample_name):
    """ Hardcoded 'Sample type's derived from filepath names """
    filepath_low = filepath.strip().lower()
    samplename_low = sample_name.strip().lower()
    mods = ""
    ref_names = [
        "blackcurtains", 
        "blackoutcupboards",
        "spectralon", 
        "aluwhite", 
        "caltargets", 
        "colorchecker", 
        "samplecup"]
    ref_colors = [
        "red",
        "yellow", 
        "green", 
        "blue", 
        "grey70",
        "gray70",
        "grey33",
        "gray33",
        "grey30",
        "gray30", 
        "cyan",
        "black"]
    if "mix" in filepath_low or "mix" in samplename_low:
        mods = "Mixture"
    elif "lunar_simulant" in filepath_low or "lunar_simulant" in samplename_low:
        mods = "Rock"
    elif any (ref in filepath_low or ref in samplename_low for ref in ref_names):
        mods = "Reference"
    elif any (color in filepath_low or color in samplename_low for color in ref_colors):
        if "witness" in filepath_low or "validation" in filepath_low:
            mods = "Reference"
    elif any (rock in filepath_low or rock in samplename_low for rock in rocks_minerals.rocks):        
        mods = "Rock"
    elif any (mineral in filepath_low or mineral in samplename_low for mineral in rocks_minerals.minerals):
        mods = "Mineral"
    return mods

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
    filename = os.path.basename(filepath)

    # Skip these entries
    keywords = ['gar', 'garabge', 'gargabge', 'white reference', 'bad'] # 'garbabe','garbage', <-- these show up but are covered by garb
    # Save these entries
    small_diameter_probe = 'i0 e0 az0'
    standard_probe = 'i12 e35 az0'
    fwd_geo = 'i30 e-45 az0'
    spec_geo = 'i30 e-30 az0'
    std_geo = 'i30 e0 az0'
    back_geo = 'i30 e45 az0'
    v_fwd_geo = 'i45 e-60 az0'
    key_geometries = [small_diameter_probe, standard_probe, std_geo, fwd_geo, spec_geo, back_geo, v_fwd_geo]
    
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
            view_geo = row3[idx].replace("=","") # strip = sign for consistency
            if any(kg in view_geo for kg in key_geometries):
                outputname = os.path.join(outputpath, f"{sample_name}_{idx}.csv")
                
                header = []

                with open(outputname, 'w', encoding='utf-8', newline='') as out:
                    writer = csv.writer(out)

                    DB_of_Origin = 'WWU TANAGER Lab'

                    header_info = get_header_info(sample_name)
                    sample_mod = get_sample_type_mods(filename, sample_name)
                    hard_vals = hardcoded_values(sample_name)

                    # Add probe type in Other Information
                    probe_type = ""
                    if view_geo == small_diameter_probe:
                        probe_type = "small diameter probe"
                    elif view_geo == standard_probe:
                        probe_type = "standard probe"
                    else: probe_type = "TANAGER" # or if there are mixed types
                    add_row(header, "Other Information", f"Probe Type: {probe_type}; Filename: {filepath}")
                    
                    # Append TANAGER viewing gemoetry to Spectrum ID if present
                    view_geo_tag = ""
                    if view_geo == fwd_geo: view_geo_tag = "_fwd"
                    if view_geo == spec_geo: view_geo_tag = "_spec"
                    if view_geo == std_geo: view_geo_tag = "_std"
                    if view_geo == back_geo: view_geo_tag = "_back"
                    if view_geo == v_fwd_geo: view_geo_tag = "_v.fwd"

                    add_row(header, "Database of origin:", DB_of_Origin)
                    # Note: We renamed "Sample ID" to "Spectrum ID" in VISOR; this is the unique name for each DB entry.
                    # The real Sample Name is preserved in "Original Sample ID"
                    add_row(header, "Spectrum ID", f"{sample_name}{view_geo_tag}")
                    add_row(header, "Original Sample ID", sample_name)
                    add_row(header, "Viewing geometry", view_geo)
                    if hard_vals:
                        add_row(header, "Sample Name", hard_vals[0])
                        add_row(header, "Material class", hard_vals[1])
                    elif header_info:
                        add_row(header, "Sample Name", header_info[0])
                        add_row(header, "Material class", header_info[1])
                        add_row(header, "Locality", header_info[2])
                        add_row(header, "Grain Size", header_info[3])
                    elif sample_mod:
                        add_row(header, "Material class", sample_mod)

                    else:
                        print(f"Header info not found for {sample_name}")

                    # Both full resolution and abbreviated version, in case full version looks too wordy
                    resolution = '3 nm @ 700 nm (VNIR 350-1000 nm); 8 nm @ 1400 nm (SWIR1 1000-1800 nm); 8 nm @ 2100 nm (SWIR2 1800-2500 nm)'
                    resolution_short = '3 nm @ 700 nm and 8 nm @ 1400/2100 nm'
                    add_row(header, "Resolution", resolution)
                    

                    writer.writerows(header)

                    # Remaining rows
                    for row in cell[start_idx:]: # Starts after the "wavelength" cell
                        col_A = row[0] if len(row) > 0 else ''
                        col_B = row[idx] if len(row) > idx else ''
                        writer.writerow([col_A, col_B])
            else:
                continue
    return sample_name
