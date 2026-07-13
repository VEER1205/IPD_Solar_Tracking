import requests
import os 
from datetime import datetime, timedelta
from tqdm import tqdm

def download_solar_data():
    start_date = datetime(2024, 12, 26)
    end_date = datetime(2024, 12, 26)
    base_url = r"https://midcdmz.nlr.gov/tsi/SRRLASI"
    
    save_folder = r"D:\code1\IPD_Solar_Tracking\Dataset\Download Images"
    os.makedirs(save_folder, exist_ok=True)
    
    # Calculate total days for the overall progress bar
    total_days = (end_date - start_date).days + 1
    current_date = start_date

    # 1. Use requests.Session() to reuse the underlying TCP connection (makes downloading faster)
    with requests.Session() as session:
        
        # 2. Setup the overall progress bar
        with tqdm(total=total_days, desc="Overall Progress", unit="day") as pbar:
            
            while current_date <= end_date:
                year_str = current_date.strftime("%Y")
                date_str = current_date.strftime("%Y%m%d")
                
                file_name = f"{date_str}.zip"
                url = f"{base_url}/{year_str}/{file_name}"
                file_path = os.path.join(save_folder, file_name)

                try:
                    # 3. Use stream=True so large zip files don't crash your RAM
                    # 4. Add a timeout to prevent the script from hanging on bad connections
                    response = session.get(url, stream=True, timeout=30)

                    if response.status_code == 200:
                        # Get the total file size from the server headers
                        total_size = int(response.headers.get('content-length', 0))
                        
                        # 5. Setup the progress bar for the individual file
                        with open(file_path, "wb") as file, tqdm(
                            desc=file_name,
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            leave=False # Hides this bar when the file is done to keep the console clean
                        ) as file_pbar:
                            
                            # Write the file in chunks instead of all at once
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    file.write(chunk)
                                    file_pbar.update(len(chunk))
                                    
                    else:
                        # 6. Use tqdm.write instead of print so the progress bar doesn't break visually
                        tqdm.write(f"Skipped {file_name}: HTTP Status {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    tqdm.write(f"Network error for {date_str}: {e}")

                # Increment date and update the overall progress bar
                current_date += timedelta(days=1)
                pbar.update(1)

    print("\nDownload process complete.")

if __name__ == "__main__":
    download_solar_data()