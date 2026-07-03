import pvlib
import math
import pandas as pd


def getSunAngles():
    tz = "Asia/Kolkata"
    time = pd.Timestamp.now(tz=tz)

    latitude = 19.0760
    longitude = 72.8777

    solarPosition = pvlib.solarposition.get_solarposition(time,latitude,longitude)

    sunAzimuth = solarPosition['azimuth'].iloc[0]
    sunElevation = solarPosition['elevation'].iloc[0]

    return sunAzimuth,sunElevation 

def CalculateSolarDeviation(panelAzimuth:float,panelElevation:float)-> float:
    
    sunAzimuth,sunElevation = getSunAngles()

    azimuthDelta = abs(sunAzimuth - panelAzimuth)
    elevationDelta = abs(sunElevation - panelElevation)

    return max(azimuthDelta,elevationDelta)


def evaluateNetEnergy(predictedIrradiance: float) -> bool:
    PANEL_AREA = 0.5        
    PANEL_EFFICIENCY = 0.20 
    PERFORMANCE_RATIO = 0.75
    MOTOR_ENERGY_COST = 5.0 
    SAFETY_MARGIN = 2.0
    
    expectedGain = PANEL_AREA * PANEL_EFFICIENCY * predictedIrradiance * PERFORMANCE_RATIO
    
    return expectedGain > (MOTOR_ENERGY_COST + SAFETY_MARGIN)

def checkShouldMove(panelAzimuth:float,panelElevation:float) -> bool:
    
    ANGLE_THRESHOLD = 5.0
    
    # 1. Check the physical hardware angle gate first
    deviation = CalculateSolarDeviation(panelAzimuth,panelElevation)
    if deviation < ANGLE_THRESHOLD:
        return False 
        
   
    predictedIrradiance = 400.0 
    return evaluateNetEnergy(predictedIrradiance)