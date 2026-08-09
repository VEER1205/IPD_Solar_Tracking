from fastapi import APIRouter
from fastapi.params import Depends
from Models.DataClass import predictParams

router = APIRouter()

@router.get("/move")
def predict(panelAngles:predictParams = Depends()):
    pass

    