import os 
import pandas as pd 
import re
import shutil

def changeName():
    files = os.listdir(r"D:\code1\IPD_Solar_Tracking\Dataset\Images")
    for i in files:
        os.rename(os.path.join("D:\code1\IPD_Solar_Tracking\Dataset\Images",i),os.path.join("D:\code1\IPD_Solar_Tracking\Dataset\Images",f"{i[:12]}.jpg"))

def extractImage():
    inputPath = r"D:\code1\IPD_Solar_Tracking\Dataset\Download Images"
    outputPath = r"D:\code1\IPD_Solar_Tracking\Dataset\Images"

    fileList = os.listdir(inputPath)
    print(len(fileList))
    for item in fileList:
        print(f"Starting with {item}")
        shutil.unpack_archive(f"{inputPath}/{item}",outputPath)
        print(f"Unpack the File {item}")
    

def cleanImages():
    path = r"D:\code1\IPD_Solar_Tracking\Dataset\Images"

    Files = set(os.listdir(path))
    print(len(Files))

    print(Files)

    regex_expression = "^.+?(?=_11.jpg)"

    # match = re.search(regex_expression,Files)

    img = {item for item in Files if (match := re.search(regex_expression,item))}

    print(img)

    FilesRemove = Files.difference(img)

    for item in FilesRemove:
        os.remove(os.path.join(path,item))

    changeName()


def execute_merge():
    CSV_FILE = r"D:\code1\IPD_Solar_Tracking\Dataset\DataSet.csv"
    IMAGE_DIR = r"D:\code1\IPD_Solar_Tracking\Dataset\Images"

    print("Loading formatted CSV...")
    df = pd.read_csv(CSV_FILE)
    
    print("Scanning the physical image directory...")
    # Creates a fast-lookup set of all the actual files on your hard drive
    existing_images = set(os.listdir(IMAGE_DIR))
    
    # THE MERGE: Keep ONLY the rows where the CSV filename exists in the folder
    final_df = df[df['filename'].isin(existing_images)]
    
    # Isolate just the two columns MobileNetV2 cares about
    final_df = final_df[['filename', 'irradiance']]
    
    # Safety check: drop any rows that somehow have blank irradiance numbers
    final_df = final_df.dropna()
    
    # Export the final dataset
    final_df.to_csv(CSV_FILE, index=False)
    
    print(f"Merge Complete! Final clean dataset saved to: {CSV_FILE}")
    print(f"Total valid training pairs ready for the CNN: {len(final_df)}")

if __name__ == "__main__":
    extractImage()
    cleanImages()
    execute_merge()
