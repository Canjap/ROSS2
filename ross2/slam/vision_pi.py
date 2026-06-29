import cv2
import time
import numpy as np  # <-- Added missing numpy import
from typing import Generator
from loguru import logger
from picamera2 import Picamera2

# 1. Initialize the camera GLOBALLY
try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    logger.info("Global Pi 5 Camera Hardware locked and started.")
except Exception as e:
    logger.error(f"Failed to initialize global camera: {e}")

# Initialize both models once at startup
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def detector(frame, model):
    """Applies the selected detection math to the frame in-place."""
    if model == "cascade":
        # Cascade needs grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        for x, y, w, h in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(
                frame,
                "Target: Face",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

    elif model == "hog":
        # HOG can use the standard BGR frame directly
        boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
        
        # Convert boxes to numpy array for cleaner iteration
        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
        
        for (xA, yA, xB, yB) in boxes:
            cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
            
        person_count = len(boxes)
        cv2.putText(
            frame,
            f'People Count: {person_count}',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )
        
    return frame


def stream_local_frames(
    camera_index: int = 0, enable_detection: bool = False, model: str = "cascade"
) -> Generator[bytes, None, None]:
    """Yields frames from the globally running Picamera2 buffer."""
    
    logger.info(f"New client connected! (Detection: {enable_detection}, Model: {model})")

    try:
        while True:
            # Pull the most recent frame from the buffer
            frame = picam2.capture_array()
            
            if frame is None:
                time.sleep(0.01)
                continue

            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Pass the frame into the detector and let it draw the boxes
            if enable_detection:
                frame = detector(frame, model)

            # Encode and stream
            ret, encoded_jpg = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + encoded_jpg.tobytes() + b"\r\n"
            )
            
    except GeneratorExit:
        logger.info("Client disconnected. Leaving camera running for next connection.")
