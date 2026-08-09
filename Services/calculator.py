import pvlib
import math
import pandas as pd
from Config import Settings

def getSunAngles():
    time = pd.Timestamp.now(tz=Settings.TIME_ZONE)

    solarPosition = pvlib.solarposition.get_solarposition(time,Settings.LATITUDE,Settings.LONGITUDE)

    sunAzimuth = float(solarPosition['azimuth'].iloc[0])
    sunElevation = float(solarPosition['elevation'].iloc[0])

    return sunAzimuth,sunElevation 

def checkAngles():
    sunAzimuth,sunElevation = getSunAngles()
    if(sunElevation < 0 ):
        print("Sun Is Below The Panel:- ")
        return

    deltaAzimuth = abs(Settings.PANEL_AZIMUTH - sunAzimuth)
    deltaElevation = abs(Settings.PANEL_ELEVATION - sunElevation)

    if deltaAzimuth < Settings.THRESHOLD_ANGLE and deltaElevation < Settings.THRESHOLD_ANGLE:
        print("No Need Of Moving:-")
        print(f"Current Sun Angles:- ({sunAzimuth,sunElevation})")
        print(f"Current Panel Angles:- ({Settings.PANEL_AZIMUTH,Settings.PANEL_ELEVATION})")
        
    else:
        print("Calling Predict Function:- ")
        Settings.PANEL_ELEVATION = sunElevation
        Settings.PANEL_AZIMUTH = sunAzimuth    
        print(f"Updated {Settings.PANEL_ELEVATION = } AND { Settings.PANEL_AZIMUTH =}")

def evaluateNetEnergy(predictedIrradiance: float) -> bool:
    motorEnergyCost = Settings.SERVO_V_M * Settings.SERVO_I_M * Settings.SERVO_DELTA_TIME
    SAFETY_MARGIN = 2.0
    expectedGain = Settings.PANEL_AREA * Settings.PANEL_EFFICIENCY * predictedIrradiance * Settings.PERFORMANCE_RATIO
    
    return expectedGain > (motorEnergyCost + SAFETY_MARGIN)

