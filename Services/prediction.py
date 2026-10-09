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
    
    # 1. Raise an error if the camera is disconnected or fails to send bytes
    if not image_bytes:
        raise ValueError("Camera feed failed: No image bytes received from ESP32-CAM.")
        
    img_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # 2. Raise an error if the image data is corrupted (e.g., partial Wi-Fi packet)
    if frame is None:
        raise ValueError("Image decoding failed: The payload was corrupted or is not a valid image format.")
        
    resized_frame = cv2.resize(frame, (380, 380))
    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    
    # 3. CRITICAL FIX applied here again: Removed / 255.0 and added float32 cast 
    # to prevent the model from outputting 0 on perfectly good images.
    input_tensor = np.expand_dims(rgb_frame, axis=0).astype(np.float32)
    
    if model is not None:
        prediction = model.predict(input_tensor, verbose=0)
        irradiance = float(prediction[0][0])
        print(f"Predicted Irradiance: {irradiance:.1f} W/m²")
        return irradiance
    else:
        # 4. Raise an error if the model failed to load at startup
        raise RuntimeError("Inference failed: TensorFlow model is not loaded.")