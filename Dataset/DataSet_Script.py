import os
import pandas as pd
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
    
    # 1. Reconstruct the NREL filename from your dateTime column
    # Example: 202401010000 -> 20240101000000_11.jpg
    df['filename'] = df['dateTime'].astype(str)
    
    # 2. Rename the massive sensor column to something easy for TensorFlow
    df.rename(columns={'Global CMP22 (vent/cor) [W/m^2]': 'irradiance'}, inplace=True)
    
    # 3. Create a fast-lookup list of the clean images actually on your drive
    print("🔍 Scanning the cleaned image directory...")
    existing_images = set(os.listdir(OUTPUT_PATH))
    
    # 4. THE MERGE: Keep ONLY the rows where the image file actually exists
    final_df = df[df['filename'].isin(existing_images)]
    
    # 5. Isolate just the two columns MobileNetV2 cares about
    # final_df = final_df[['filename', 'irradiance']]
    
    # Safety check: drop any rows that have blank irradiance numbers
    final_df = final_df.dropna()
    
    # Export the final dataset
    final_df.to_csv(f"D:\code1\IPD_Solar_Tracking\Dataset\Cleaned_DataSet.csv", index=False)
    
    print(f"🚀 Merge Complete! Final mapping saved to: D:\code1\IPD_Solar_Tracking\Dataset\Cleaned_DataSet.csv")
    print(f"🎯 Total valid training pairs ready for the CNN: {len(final_df)}")

if __name__ == "__main__":
    # Ensure the output directory actually exists before running operations
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    # extract_images()
    # clean_images()
    execute_merge()