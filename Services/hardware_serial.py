import requests
from Config import Settings

def moveServo(panelAzimuth: float ,panelElevation) -> bool:
    payload = {
        "azimuth":panelAzimuth,
        "elevation":panelElevation
        }
    try:
        request = requests.post(url = Settings.ESP32_MAIN_URL,json = payload,timeout=10.0)
        if request.status_code == 200:
            return True
        else:
            print(f"Error Moving Servos {request.status_code}")
            return False   
    except Exception as e:
        print(f"ESP32 Main Board Is offline... Error:{e}" )
        return False
    
def takeImage() -> bytes | None:
    try:
        request = requests.get(Settings.ESP32_CAM_URL,timeout=10.0)
        if request.status_code == 200:
            return request.content
        else:
            print(f"CAM ERROR statu:{request.status_code}")
            return None
        
    except Exception as e:
        print(f"ESP32 CAM Is offline... \nError:{e}")
        return None
    