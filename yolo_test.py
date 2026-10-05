import cv2
from ultralytics import YOLO
import time
import numpy as np  # <-- Added missing numpy import
from typing import Generator
from loguru import logger
from picamera2 import Picamera2

try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    logger.info("Global Pi 5 Camera Hardware locked and started.")
except Exception as e:
    logger.error(f"Failed to initialize global camera: {e}")


model = YOLO('yolo26n.pt')

while True:
    frame = picam2.capture_array()

    if frame is None:
        time.sleep(0.01)
        continue
    
    # Convert RGB to BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)    
    results = model(frame, classes=[0], conf=0.5)

    human_count = len(results[0].boxes)
    print(f'Humans detected: {human_count}')

    annotated_frame = results[0].plot()

    ret, encoded_jpg = cv2.imencode(".jpg", annotated_frame)
    if not ret:
        continue
    yeild

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
