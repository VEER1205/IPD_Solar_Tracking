from fastapi import FastAPI
from Routers.tracker_routes import router

app = FastAPI()

@app.get("/")
def Hello():
    return {
        "Status":"200",
        "Message":"API Is Running "
            }

app.include_router(router)