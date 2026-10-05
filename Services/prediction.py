import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import numpy as np
import tensorflow as tf
from Services.hardware_serial import takeImage 

try:
    model = tf.keras.models.load_model("Models/efficientnet_b4_solar.keras")
    print("TensorFlow EfficientNetB4 loaded successfully.")
except Exception as e:
    print(f"Warning: Model not found or failed to load. {e}")
    model = None

def predict() -> float:
    print("Fetching live sky image from ESP32-CAM...")
    image_bytes = takeImage()
    
    if not image_bytes:
        print("Camera feed failed. Defaulting to 0 W/m².")
        return 0.0
        
    try:
        img_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("Failed to decode image payload. Defaulting to 0 W/m².")
            return 0.0
        
        resized_frame = cv2.resize(frame, (380, 380))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        input_tensor = np.expand_dims(rgb_frame, axis=0) / 255.0
        
        if model is not None:
            prediction = model.predict(input_tensor, verbose=0)
            irradiance = float(prediction[0][0])
            print(f"Predicted Irradiance: {irradiance:.1f} W/m²")
            return irradiance
        else:
            print(f"Model Faile To Predict...")
            return 0
            
    except Exception as e:
        print(f"Inference error: {e}")
        return 0.0