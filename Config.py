from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    PANEL_AREA: float    
    PANEL_EFFICIENCY: float  
    PERFORMANCE_RATIO: float
    SERVO_V_M: float 
    SERVO_I_M: float  
    SAFETY_MARGIN: float 
    PANEL_AZIMUTH: float 
    PANEL_ELEVATION: float 
    LATITUDE:float
    LONGITUDE:float
    TIME_ZONE:str
    SERVO_DELTA_TIME:float

    model_config = SettingsConfigDict(env_file=".env")