import os 
import pandas as pd 
import re

path = os.getcwd()
path = os.path.join(path,"Dataset")
print(path)

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
     