import os
import csv
import re
import rocks_minerals


DB_OF_ORIGIN = "WWU TANAGER Lab"

# Skip these garbage/test entries
SKIP_WORDS = [
    "gar",
    "white reference",
    "bad",
    "test",
    "_gr10",
    "2023_08_08_lunar_simulant_fullhem_foruwinn_a",
]  # 'garbabe','garbage', 'garabge', 'gargabge',<-- these show up but are covered by gar

SMALL_DIAMETER_PROBE = "i0 e0 az0"
STANDARD_PROBE = "i12 e35 az0"

# Save these viewing geometries:
VIEWING_GEOMETRIES = {
    # Handheld probes
    "small_diameter_probe": {"i0 e0 az0"},
    "standard_probe": {"i12 e35 az0"},
    # possible forward scatter geometries:
    "fwd_geo": {
        "i30 e-45 az0",
        "i30 e-50 az0",
        "i-30 e45 az0",
        "i-30 e50 az0",
        "i45 e-30 az0",
        "i-45 e30 az0",
        "i50 e-30 az0",
        "i-50 e30 az0",},
    # possible specular geometries:
    "spec_geo": {
        "i30 e-30 az0",
        "i30 e-30 az0",
        "i-30 e30 az0",
        "i45 e-45 az0",
        "i-45 e45 az0",},
    # possible standard geometries:
    "std_geo": {
        "i30 e0 az0",
        "i35 e0 az0",
        "i0 e30 az0",
        "i0 e35 az0",},
    # possible backscatter geometries:
    "back_geo": {
        "i30 e45 az0",
        "i30 e50 az0",
        "i-30 e-45 az0",
        "i-30 e-50 az0",
        "i45 e30 az0",
        "i50 e30 az0",
        "i-45 e-30 az0",
        "i-50 e-30 az0",},
    # possible very forward geometries:
    "v_fwd_geo": {
        "i45 e-60 az0",
        "i-45 e60 az0",
        "i50 e-60 az0",
        "i-50 e60 az0",
        "i60 e-45 az0",
        "i-60 e45 az0",
        "i-60 e50 az0",
        "i60 e-50 az0",
        "i-70 e58 az0",
        "i70 e-58 az0",},
    }


# Both full resolution and abbreviated version, in case full version looks too wordy
RESOLUTION = "3 nm @ 700 nm (VNIR 350-1000 nm); 8 nm @ 1400 nm (SWIR1 1000-1800 nm); 8 nm @ 2100 nm (SWIR2 1800-2500 nm)"
RESOLUTION_SHORT = "3 nm @ 700 nm and 8 nm @ 1400/2100 nm"

REF_NAMES = [
    "blackcurtains", "blackoutcupboards", "spectralon", "aluwhite", "caltargets",
    "colorchecker", "samplecup",
]
REF_COLORS = [
    "red", "yellow", "green", "blue", "grey70", "gray70", "grey33", "gray33",
    "grey30", "gray30", "cyan", "black",
]


def hardcoded_values(sample_name):
    """Return hardcoded values for specific samples"""
    samplename_low = sample_name.strip().lower()
    if (
        sample_name == "906165_flush_si510"
        or sample_name == "906167_0.2mm_indent_si510"
    ):
        return ("XRD sample holder", "Reference")
    if samplename_low == 'gypsum_125':
        return ("gypsum", "Mineral")
    if samplename_low =='powdered_hematite':
        return ("powdered hematite", "Mineral")


def matches_acronym(sample_name, acronyms):
    """
    Check if sample_name contains any acronym with '_', '-', or ' ' as suffix.
    """
    for acronym in acronyms:
        for suffix in ("_", "-", " "):
            if f"{acronym}{suffix}" in sample_name:
                return True
    return False


def get_header_info(sample_name_in):
    """
    Takes TANAGER Sample Name and returns human readable name,
    sample type (as material class), locality, and grain size
    """
    sample_name = sample_name_in.strip().upper()

    if matches_acronym(sample_name, ["TS"]):
        return ("Twin Sisters Dunite", "Rock", "Twin Sisters Mountains", "Whole Object")
    if matches_acronym(sample_name, ["TM"]):
        return ("Table Mountain Andesite", "Rock", "Mount Baker, WA", "Whole Object")
    if matches_acronym(sample_name, ["APA"]):
        return ("Artist Point Andesite", "Rock", "Mount Baker, WA", "Whole Object")
    if matches_acronym(sample_name, ["DF"]):
        return ("Dry Falls Basalt","Rock","Columbia River Flood Basalts","Whole Object")
    if matches_acronym(sample_name, ["FC"]):
        return ("Frenchman Coulee Basalt","Rock", "Columbia River Flood Basalts", "Whole Object")
    if matches_acronym(sample_name, ["GR"]):
        return ("Grand Ronde Basalt", "Rock", "Columbia River Flood Basalts", "Whole Object")
    if matches_acronym(sample_name, ["SM"]):
        return ("Saddle Mountain","Rock", "Columbia River Flood Basalts", "Whole Object")
    if matches_acronym(sample_name, ["KD", "KDT"]):
        return ("Ka'u Desert Trail Basalt","Rock","Hawaii Volcanoes National Park","Whole Object")
    if matches_acronym(sample_name, ["PC", "PCT"]):
        return ("Puna Coast Trail Basalt","Rock","Hawaii Volcanoes National Park","Whole Object")
    if matches_acronym(sample_name, ["MIT"]):
        return ("Mauna Iki Trail Basalt","Rock","Hawaii Volcanoes National Park","Whole Object")
    if matches_acronym(sample_name, ["CRB"]):
        return ("Columbia River Flood Basalts","Rock","Columbia River Flood Basalts","Whole Object")
    return None


def get_sample_type_mods(filepath, sample_name):
    """Hardcoded 'Sample type's derived from filepath names"""
    filepath_low = filepath.strip().lower()
    samplename_low = sample_name.strip().lower()

    if "mix" in filepath_low or "mix" in samplename_low:
        return (sample_name, "Mixture")
    if "lunar_simulant" in filepath_low or "lunar_simulant" in samplename_low:
        return (sample_name, "Rock")
    if any(ref in filepath_low or ref in samplename_low for ref in REF_NAMES):
        return (sample_name, "Reference")
    if any(color in filepath_low or color in samplename_low for color in REF_COLORS):
        if "witness" in filepath_low or "validation" in filepath_low:
            return (sample_name, "Reference")
    if any(rock in filepath_low or rock in samplename_low for rock in rocks_minerals.rocks):
        return (sample_name, "Rock")
    if any(mineral in filepath_low or mineral in samplename_low for mineral in rocks_minerals.minerals):
        return (sample_name, "Mineral")
    return None


def alivia_exceptions(sample_name):
    """ process these exact spectrum_ids with standard logic (not alivia's conventions)"""
    exceptions = {
        'Kieserite',
        'DF_18_003_<125um',
        'GR_19_01_75-106um',
        'TS_20_28_<125um',
        'Epsomite_75-106um',
        'Epsomite',
        'JSC',
        'TS-20-28-powdered-finer125um',
        'gypsum',
        'basalt'
    }
    return sample_name in exceptions


def get_alivia_shorthand(abbreviation):
    """ Returns full name of Alivia's abbreviated mineral names """
    abbreviations = {
        "mon": "montmorillonite",
        "sap": "saponite", 
        "non": "nontronite",
        "bas": "basalt",
        "dun": "dunite",
        "hem": "hematite",
        "eps": "epsomite",
        "ep": "epsomite",
        "jsc": "JSC-Mars-1 soil simulant",
        "anh": "anhydrite",
        "gyp": "gypsum",
        "and": "andesite"
    }
    return abbreviations.get(abbreviation.strip().lower())


def parse_mineral_component(component):
    """
    Parse a single component into mineral name and percentage.
    Returns (mineral_name, percentage) or (None, None) if invalid.
    """
    # Match pattern: numbers followed by letters
    match = re.match(r'^(\d+(?:\.\d+)?)([a-zA-Z]+)$', component.strip())
    if not match:
        return None, None
    
    percentage, mineral = match.groups()
    mineral_full = get_alivia_shorthand(mineral)
    
    if mineral_full is None:
        return mineral, percentage
        
    return mineral_full, percentage


def get_alivia_components(sample_name):
    # Grab mineral and %, expand to full name if needed
    # Repeat for 1-4 minerals
    # Return full name
    components = re.split(r'[_\-\s]+', sample_name.strip())
    mineral_parts = []

    for component in components:
        if not component:
            continue
        mineral_name, percentage = parse_mineral_component(component)

        if mineral_name and percentage is not None:
            mineral_parts.append(f"{mineral_name} {percentage}%")

    if not mineral_parts:
        return sample_name
    return ", ".join(mineral_parts)


def get_alivia_info(filepath, sample_name):
    """ Alternate naming schemes for Alivia and Max spectra """

    # TODO: Add link to Alivia's thesis in her dataset

    if alivia_exceptions(sample_name):
        return None
    
    filepath_low = filepath.strip().lower()
    samplename_low = sample_name.strip().lower()
    human_readable_name = ""

    check_path = {
        "alivia", 
        "max_claysulfate", 
        "max_goniometer", 
        "2023_01_18_kristiana_maficmixtures.csv", 
        "2023_02_13_kristiana_maficmixtures_jscadditional.csv",}

    if any(path in filepath_low for path in check_path):
        human_readable_name = get_alivia_components(samplename_low)
        return (human_readable_name,"Mixture")
    return None


def translate_expanse_name(sample_name):
    expanse_names = {
        "farragut": ("SC", "Pre-coating, Si on Twin Sisters Dunite, 240-grit"),
        "tripoli": ("SM", "Pre-coating, Si on Twin Sisters Dunite, 400-grit"),
        "zenobia": ("SF", "Pre-coating, Si on Twin Sisters Dunite, 600-grit"),
        "damascus": ("FC", "Pre-coating, Fe on Twin Sisters Dunite, 240-grit"),
        "hammurabi": ("FM", "Pre-coating, Fe on Twin Sisters Dunite, 400-grit"),
        "xuesen": ("FF", "Pre-coating, Fe on Twin Sisters Dunite, 600-grit"),
        "pella": ("UC", "Uncoated Twin Sisters Dunite, 240-grit"),
        "koto": ("UM", "Uncoated Twin Sisters Dunite, 400-grit"),
        "tynan": ("UF", "Uncoated Twin Sisters Dunite, 600-grit"),
    }
    return expanse_names.get(sample_name.strip().lower())


def get_max_info(filepath, sample_name):
    """
    Alternate naming schemes for Max spectra
    Returns: Sample name, material class, locality, spectrum_id(renamed)
    """
    # Skip this one:
    if "2023_10_24_Max_TS_20_08_Sediments_Recon.csv" in filepath:
        return None
    human_readable_name = ""
    new_spectrum_id = sample_name
    expanse_data = translate_expanse_name(sample_name)
    material_class = "Rock"
    locality = "Twin Sisters Mountains"
    
    # Pre-coating files
    pre_coat = {
        "2022_12_01_Max_LPSC_PreCoat2",
        "2022_12_05_Max_LPSC_PreCoat2.1", 
    }
    if any(pc in filepath for pc in pre_coat):
        new_spectrum_id = f"{new_spectrum_id}-{expanse_data[0]}-pre"
        human_readable_name = expanse_data[1]
        return (human_readable_name, material_class, locality, new_spectrum_id)
    
    # Post-coating files
    post_coat = {
        "2023_01_31_Max_LPSC_NanohematiteCoatedSlabs",
    }
    if any(pc in filepath for pc in post_coat):
        new_spectrum_id = f"{new_spectrum_id}-{expanse_data[0]}-post"
        human_readable_name = expanse_data[1]
        return (human_readable_name, material_class, locality, new_spectrum_id)
    
    return None


def add_row(header, label, value):
    """Add new row to CSV header; doesn't add empty values (prevents NaN error with VISOR)"""
    if value:  # excludes None, empty strings, and False
        header.append([label, value])


# Gather header info based on naming conventions
def apply_filters(filepath, sample_name_in):
    # Returns: 0)Sample name, 1)Material class, 2)Locality, 3)Grain size, 4)Spectrum id (if updated)
    sample_name = sample_name_in
    material_class = ""
    locality = ""
    grain_size = ""
    new_spectrum_id = ""

    hard_vals = hardcoded_values(sample_name)
    alivia_info = get_alivia_info(filepath, sample_name)
    max_info = get_max_info(filepath, sample_name)
    header_info = get_header_info(sample_name)
    sample_info = get_sample_type_mods(filepath, sample_name)

    if hard_vals:
        sample_name = hard_vals[0]
        material_class = hard_vals[1]
    elif alivia_info:
        sample_name = alivia_info[0]
        material_class = alivia_info[1]
    elif max_info:
        sample_name = max_info[0]
        material_class = max_info[1]
        locality = max_info[2]
        new_spectrum_id = max_info[3]
    elif header_info:
        sample_name = header_info[0]
        material_class = header_info[1]
        locality = header_info[2]
        grain_size = header_info[3]
    elif sample_info:
        sample_name = sample_info[0]
        material_class = sample_info[1]
    return (sample_name, material_class, locality, grain_size, new_spectrum_id)


# Main cleaning method used by tanager_main to prepare data for ingestion
def clean(filepath, outputpath):
    """
    Takes TANAGER CSV files and splits them into individual samples to upload.
    Discards garbage and white reference data.
    Only saves preferred viewing geometries.
    """

    os.makedirs(outputpath, exist_ok=True)
    filename = os.path.basename(filepath)

    # Viewing geometries to be used for this file (only one of each)
    fwd = ""
    spec = ""
    std = ""
    back = ""
    v_fwd = ""

    with open(filepath, "r", encoding="utf-8") as f:
        # Read all lines
        cell = [
            line.strip().split(",") for line in f.readlines()
        ]  # 2d array of cells [row][col]

        if len(cell) < 2:
            print("File does not have enough rows.")
            return

        row2 = cell[1]  # Row of sample names
        row3 = cell[2]  # Row of viewing geometries
        cols = len(row2)  # Number of columns
        # Find the index of the row where the first column contains "wavelength"
        start_idx = None
        for i, row in enumerate(cell):
            if len(row) > 0 and row[0].strip().lower() == "wavelength":
                start_idx = i
                break
            if start_idx is None:
                continue

        for idx in range(1, cols):
            # sample_name here is actually the Spectrum ID in Visor
            sample_name = row2[idx].strip().lower()
            
            # Skip these results: bad files or garbage data
            if any(sw in sample_name for sw in SKIP_WORDS):
                continue

            # Save only results from preferred Viewing Geometry
            view_geo = row3[idx].replace("=", "")  # strip = sign for consistency

            if any(view_geo in geometries for geometries in VIEWING_GEOMETRIES.values()):
                outputname = os.path.join(outputpath, f"{sample_name}_{idx}.csv")

                header = []

                with open(outputname, "w", encoding="utf-8", newline="") as out:
                    writer = csv.writer(out)

                    # Get header info using filters built for different naming conventions
                    filtered_data = apply_filters(filepath, sample_name)

                    # Add probe type and filename in Other Information
                    probe_type = ""
                    if view_geo == SMALL_DIAMETER_PROBE:
                        probe_type = "small diameter probe"
                    elif view_geo == STANDARD_PROBE:
                        probe_type = "standard probe"
                    else:
                        probe_type = "TANAGER"  # or if there are mixed types
                    add_row(
                        header,
                        "Other Information",
                        f"Probe Type: {probe_type}; Filename: {filepath}", # TODO: Change filepath --> filename, currently using path to bugtest
                    )

                    # Append TANAGER viewing gemoetry to Spectrum ID if present
                    view_geo_tag = ""
                    if view_geo == "fwd_geo":
                        view_geo_tag = "_fwd"
                    if view_geo == "spec_geo":
                        view_geo_tag = "_spec"
                    if view_geo == "std_geo":
                        view_geo_tag = "_std"
                    if view_geo == "back_geo":
                        view_geo_tag = "_back"
                    if view_geo == "v_fwd_geo":
                        view_geo_tag = "_v.fwd"

                    if filtered_data:
                        add_row(header, "Sample Name", filtered_data[0])
                        add_row(header, "Material class", filtered_data[1])
                        add_row(header, "Locality", filtered_data[2])
                        add_row(header, "Grain Size", filtered_data[3])
                        if filtered_data[4]: # Renames spectrum id
                            sample_name = filtered_data[4] 

                    else:
                        print(f"Header info not found for {sample_name}")

                    add_row(header, "Database of origin:", DB_OF_ORIGIN)
                    # Note: We renamed "Sample ID" to "Spectrum ID" in VISOR; this is the unique name for each DB entry.
                    # The real Sample Name is preserved in "Original Sample ID"
                    add_row(header, "Spectrum ID", f"{sample_name}{view_geo_tag}")
                    add_row(header, "Original Sample ID", sample_name)
                    add_row(header, "Viewing geometry", view_geo)
                    add_row(header, "Resolution", RESOLUTION)

                    writer.writerows(header)

                    # Remaining rows
                    for row in cell[start_idx:]:  # Starts after the "wavelength" cell
                        col_A = row[0] if len(row) > 0 else ""
                        col_B = row[idx] if len(row) > idx else ""
                        writer.writerow([col_A, col_B])
            else:
                continue
    return sample_name
