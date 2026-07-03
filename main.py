from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def Hello():
    return {
        "Status":"200",
        "Message":"API Is Running "
            }