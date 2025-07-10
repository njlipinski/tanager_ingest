import os

def clean(filepath, outputpath):
    
    keywords = ['garbage', 'garbabe', 'white reference']
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Read all lines
        lines = f.readlines()

        # Grab row 2 
        if len(lines) < 2:
            print("File does not have enough rows.")
            return

        row2 = lines[1].strip().split(',')
        cols = len(row2)

        for idx in range(1, cols):
            cell_val = row2[idx].strip().lower()

        # Print each cell in row 2
        for idx, value in enumerate(row2, start=1):
            val = value.strip().lower()
            if not any (kw in val for kw in keywords):
                print(f"Column {idx}: {value}")

if __name__ == "__main__":
    input = "./inputs/test.csv"
    output = "./inputs/"

    clean(input, output)

