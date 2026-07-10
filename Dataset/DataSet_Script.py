import os 
import pandas as pd 
import re
import shutil

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
     

# extractImage()
# cleanImages()
print(len(os.listdir(r"D:\code1\IPD_Solar_Tracking\Dataset\Images")))