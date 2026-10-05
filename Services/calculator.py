import math
import pvlib
import pandas as pd
from Services.hardware_serial import moveServo
from Services.prediction import predict
from Config import Settings

def getSunAngles() -> tuple[float, float]:
    time = pd.Timestamp.now(tz=Settings.TIME_ZONE)
    
    solar_position = pvlib.solarposition.get_solarposition(
        time, Settings.LATITUDE, Settings.LONGITUDE
    )
    
    sun_azimuth = float(solar_position['azimuth'].iloc[0])
    sun_elevation = float(solar_position['elevation'].iloc[0])
    
    print(f"Time: {time}")
    return sun_azimuth, sun_elevation 

def evaluateNetEnergy(predicted_irradiance: float, delta_azimuth: float, delta_elevation: float) -> bool:

    total_error_deg = math.sqrt(delta_azimuth**2 + delta_elevation**2)
    total_error_rad = math.radians(total_error_deg)

    power_aligned = (
        Settings.PANEL_AREA 
        * Settings.PANEL_EFFICIENCY 
        * predicted_irradiance 
        * Settings.PERFORMANCE_RATIO
    )
    
    marginal_gain_joules = power_aligned * (1 - math.cos(total_error_rad)) * Settings.POLLING_INTERVAL_SECONDS
    
    servo_cost_joules = Settings.SERVO_V_M * Settings.SERVO_I_M * Settings.SERVO_DELTA_TIME
    safety_margin_joules = 2.0
    
    print(f"[ENERGY] Marginal Gain: {marginal_gain_joules:.2f} J | Motor Cost: {servo_cost_joules:.2f} J")
    
    return marginal_gain_joules > (servo_cost_joules + safety_margin_joules)

def checkAngles():
    sun_azimuth, sun_elevation = getSunAngles()

    if sun_elevation < 0:
        print("Sun is below the horizon. System in standby.")
        return

    delta_azimuth = abs(Settings.PANEL_AZIMUTH - sun_azimuth)
    delta_elevation = abs(Settings.PANEL_ELEVATION - sun_elevation)

    # Threshold check to prevent micro-adjustments
    if delta_azimuth < Settings.THRESHOLD_ANGLE and delta_elevation < Settings.THRESHOLD_ANGLE:
        print("No Need Of Moving: Panel within threshold.")
        print(f"Current Sun Angles: ({sun_azimuth:.1f}, {sun_elevation:.1f})")
        print(f"Current Panel Angles: ({Settings.PANEL_AZIMUTH:.1f}, {Settings.PANEL_ELEVATION:.1f})")
        return

    print("Threshold exceeded. Calling Predict Function...")
    irradiance = predict()
    if irradiance > 0 and evaluateNetEnergy(irradiance, delta_azimuth, delta_elevation):
        servo_azimuth = sun_azimuth - 45.0 
        servo_azimuth = max(0.0, min(270.0, servo_azimuth))
        
        # Clamp elevation to standard 0-90 degree limits
        servo_elevation = max(0.0, min(90.0, sun_elevation))

        if moveServo(panelElevation=servo_elevation, panelAzimuth=servo_azimuth):
            Settings.PANEL_ELEVATION = sun_elevation
            Settings.PANEL_AZIMUTH = sun_azimuth
            print(f"Updated Settings.PANEL_ELEVATION = {Settings.PANEL_ELEVATION:.1f} AND Settings.PANEL_AZIMUTH = {Settings.PANEL_AZIMUTH:.1f}")
        else:
            print("Can't Move The Servos: Actuator communication failed.")
    else:
        print("Movement gated: Irradiance too low or motor cost exceeds marginal gain.")