from typing import Generator

import cv2
from loguru import logger
import time
# Load the cascade classifier globally once
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def stream_local_frames(
    camera_index: int = 0, enable_detection: bool = False
) -> Generator[bytes, None, None]:
    """Captures video frames and conditionally yields raw or annotated MJPEG streams."""
    cap = cv2.VideoCapture(camera_index)

    # Set lower resolution for performance optimization on the Pi
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        logger.error(f"Could not open video device at index {camera_index}")
        return

    logger.info(f"Streaming engine initialized (Detection Active: {enable_detection}).")

    try:
        while True:
            success, frame = cap.read()
            if not success:
                logger.warning("Dropped frame detected; restarting hardware read capture.")
                time.sleep(0.1)
                continue

            # Only run the heavy math and annotations if the user requested the detection endpoint
            if enable_detection:
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

            # Encode the frame back to JPEG format for network streaming
            ret, encoded_jpg = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encoded_jpg.tobytes() + b"\r\n"
            )
    finally:
        logger.info("Releasing camera hardware hook safely.")
        cap.release()
