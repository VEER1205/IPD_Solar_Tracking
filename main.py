from fastapi import FastAPI,Depends
from Routers.tracker_routes import router
from functools import lru_cache
from Config import Settings
from Services.calculator import checkAngles
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    schedular = BackgroundScheduler()
    schedular.add_job(checkAngles,'interval',minutes=15)
    schedular.start()

    yield

    schedular.shutdown()

app = FastAPI(lifespan=lifespan)

@lru_cache()
def getSettings():
    return Settings()

@app.get("/Info")
def getInfo(setting : Settings = Depends(getSettings)):
    return {
        "PANEL AREA":setting.PANEL_AREA,
        "PANEL AZIMUTH":setting.PANEL_AZIMUTH,
        "PANEL ELEVATION":setting.PANEL_ELEVATION,
        "PANEL EFFICIENCY":setting.PANEL_EFFICIENCY,
        "SERVO Current":setting.SERVO_I_M,
        "SERVO Votage":setting.SERVO_V_M
    }

@app.get("/")
def Hello():
    return {
        "Status":"200",
        "Message":"API Is Running "
            }

app.include_router(router)