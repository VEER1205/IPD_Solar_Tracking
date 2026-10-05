from fastapi import APIRouter, HTTPException, UploadFile, File
from Models.DataClass import predictParams
from Services.hardware_serial import moveServo
from Services.calculator import getSunAngles
from Services.prediction import predict, model  # Ensure 'model' is importable from prediction.py
from Config import Settings
import numpy as np
import cv2

router = APIRouter()

# 1. Manual Angle Testing
@router.post("/test/move")
def manual_move(azimuth: float, elevation: float):
    """Manually forces the servos to specific angles and updates system state."""
    success = moveServo(panelAzimuth=azimuth, panelElevation=elevation)
    
    if success:
        Settings.PANEL_AZIMUTH = azimuth
        Settings.PANEL_ELEVATION = elevation
        return {
            "status": "success", 
            "message": "Servos moved manually.",
            "current_state": {
                "azimuth": azimuth, 
                "elevation": elevation
            }
        }
    raise HTTPException(status_code=503, detail="Actuator communication failed.")

# 2. Live Camera Prediction
@router.get("/test/predict/live")
def predict_live():
    """Fetches a live frame from the ESP32-CAM and returns the AI irradiance prediction."""
    irradiance = predict()
    return {
        "status": "success",
        "source": "ESP32-CAM",
        "irradiance_W_m2": round(irradiance, 2)
    }

# 3. Upload Image Prediction
@router.post("/test/predict/upload")
async def predict_upload(file: UploadFile = File(...)):
    """Allows manual upload of a local sky image to test the EfficientNetB4 model."""
    if model is None:
        raise HTTPException(status_code=503, detail="TensorFlow model is not loaded.")
        
    try:
        # Read and decode the uploaded file bytes
        contents = await file.read()
        img_array = np.asarray(bytearray(contents), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # FIX 1: Check if the frame is None immediately before OpenCV tries to resize it
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file format.")

        # Preprocess identically to your hardware loop
        resized_frame = cv2.resize(frame, (380, 380))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # FIX 2: Use float32. Removed the duplicate block containing the / 255.0 math.
        input_tensor = np.expand_dims(rgb_frame, axis=0).astype(np.float32)
        
        # Run inference
        prediction_val = model.predict(input_tensor, verbose=0)
        irradiance = float(prediction_val[0][0])
        
        return {
            "status": "success",
            "filename": file.filename,
            "irradiance_W_m2": round(irradiance, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Inference failed: {e}")

# 4. Calculate Sun Angles Only
@router.get("/test/angles")
def calculate_sun_angles():
    """Calculates the current astronomical sun angles without moving the hardware."""
    sun_azimuth, sun_elevation = getSunAngles()
    return {
        "status": "success",
        "timestamp": "Current",
        "astronomical_angles": {
            "azimuth": round(sun_azimuth, 2),
            "elevation": round(sun_elevation, 2)
        }
    }