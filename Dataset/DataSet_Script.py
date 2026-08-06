import os
import pandas as pd
import numpy as np
import re
import shutil
from pathlib import Path
from tqdm import tqdm

# --- CONFIGURATION & PATHS ---
BASE_DIR = Path(r"D:\code1\IPD_Solar_Tracking\Dataset")
INPUT_PATH = BASE_DIR / "Download Images"
OUTPUT_PATH = BASE_DIR / "Images"
CSV_FILE = BASE_DIR / "DataSet.csv"

def extract_images():
    """Unpacks all archives from the input directory to the output directory."""
    print("\n--- Extracting Images ---")
    
    # Check if directory exists to avoid errors
    if not INPUT_PATH.exists():
        print(f"Error: Path {INPUT_PATH} does not exist.")
        return

    file_list = os.listdir(INPUT_PATH)
    print(f"Found {len(file_list)} archives to process.")
    
    # Wrap the loop in tqdm for a progress bar
    for item in tqdm(file_list, desc="Extracting Archives", unit="file"):
        archive_path = INPUT_PATH / item
        try:
            shutil.unpack_archive(archive_path, OUTPUT_PATH)
        except Exception as e:
            # If extraction fails, print the error and move to the next file
            print(f"\n[Warning] Skipping {item} due to extraction error: {e}")
            continue

def clean_images():
    """Filters unwanted images using regex, deletes them, and renames the remaining ones."""
    print("\n--- Cleaning and Renaming Images ---")
    
    files = set(os.listdir(OUTPUT_PATH))
    print(f"Total files before cleaning: {len(files)}")

    # Compile regex once for performance: matches everything before "_11.jpg"
    regex_expression = re.compile(r"^.+?(?=_11\.jpg)")

    # Identify files to keep based on regex match
    images_to_keep = {item for item in files if regex_expression.search(item)}
    files_to_remove = files.difference(images_to_keep)

    # Delete unwanted files with a progress bar
    for item in tqdm(files_to_remove, desc="Deleting Unwanted", unit="file"):
        try:
            os.remove(OUTPUT_PATH / item)
        except Exception as e:
            print(f"\n[Warning] Failed to delete {item}: {e}")
            continue

    # Fetch the updated list of files after deletion
    remaining_files = os.listdir(OUTPUT_PATH)
    
    # Rename the remaining files (slice first 12 chars) with a progress bar
    for item in tqdm(remaining_files, desc="Renaming Kept Images", unit="file"):
        old_path = OUTPUT_PATH / item
        
        # Safety check: Ensure it's a file and avoid IndexErrors on short names
        if old_path.is_file() and old_path.suffix.lower() == '.jpg':
            new_name = f"{item[:12]}.jpg"
            new_path = OUTPUT_PATH / new_name
            
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    # If renaming fails (e.g., file locked or permission denied), skip it
                    print(f"\n[Warning] Skipping rename of {item} due to error: {e}")
                    continue

def execute_merge():
    print("📊 Loading CSV dataset...")
    df = pd.read_csv(CSV_FILE)

    imageList = np.array(os.listdir(OUTPUT_PATH))
    for i in range(len(imageList)):
        imageList[i] = imageList[i][:12]
    df["ImageBool"] = df["dateTime"].isin(imageList)
    df = df[df["ImageBool"]] 
    print(df.head(10))

if __name__ == "__main__":
    # Ensure the output directory actually exists before running operations
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    # extract_images()
    # clean_images()
    execute_merge()