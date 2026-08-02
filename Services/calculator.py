import pvlib
import math
import pandas as pd
from ..Config import Settings

def getSunAngles():
    time = pd.Timestamp.now(tz=Settings.TIME_ZONE)

    solarPosition = pvlib.solarposition.get_solarposition(time,Settings.LATITUDE,Settings.LONGITUDE)

    sunAzimuth = solarPosition['azimuth'].iloc[0]
    sunElevation = solarPosition['elevation'].iloc[0]

    return sunAzimuth,sunElevation 

def evaluateNetEnergy(predictedIrradiance: float) -> bool:
    motorEnergyCost = Settings.SERVO_V_M * Settings.SERVO_I_M * Settings.SERVO_DELTA_TIME
    SAFETY_MARGIN = 2.0
    expectedGain = Settings.PANEL_AREA * Settings.PANEL_EFFICIENCY * predictedIrradiance * Settings.PERFORMANCE_RATIO
    
    return expectedGain > (motorEnergyCost + SAFETY_MARGIN)

