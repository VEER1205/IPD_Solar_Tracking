from pydantic import BaseModel
from fastapi.params import Query

class predictParams(BaseModel):
    azimuth:int = Query(...)
    elevation : int  = Query(...)
    panelCurrentEnergyGenaration: int = Query()
    