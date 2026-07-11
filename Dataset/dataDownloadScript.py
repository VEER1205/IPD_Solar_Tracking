import requests
import os 
from datetime import datetime,timedelta


start_date = datetime(2025,2,17)
end_date = datetime(2025,12,31)

baseUrl = r"https://midcdmz.nlr.gov/tsi/SRRLASI"

save_folder = r"D:\code1\IPD_Solar_Tracking\Dataset\Download Images"
os.makedirs(save_folder,exist_ok=True)

current_date = start_date
while current_date <= end_date:
    yearStr = current_date.strftime("%Y")
    dateStr = current_date.strftime("%Y%m%d")

    fileName = f"{dateStr}.zip"
    url = f"{baseUrl}/{yearStr}/{fileName}"

    print(f"Attempting To Download: {dateStr}")

    try:
        response = requests.get(url=url)

        if response.status_code == 200:
            filePath = os.path.join(save_folder,fileName)
            with open(filePath,"wb") as file:
                file.write(response.content)
            print(f"Successfully saved: {fileName}")
        else:
            print(f"File not found or failed. HTTP Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Network error for {dateStr}: {e}")

    # CRITICAL ADDITION: Increment the date to prevent an infinite loop
    current_date += timedelta(days=1)
    
print("Download process complete.")