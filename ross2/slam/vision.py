import cv2
from loguru import logger
from typing import Generator

def stream_local_annotated_frames(model=None, camera_index: int = 0) -> Generator[bytes, None, None]:
    """
    Captures frames from a local camera device, runs object detection 
    inference, and yields multipart JPEG stream chunks.
    """
    logger.info(f"Initializing local video capture on device index {camera_index}")
    cap = cv2.VideoCapture(camera_index)
    
    # Standard baseline resolution for network streaming speed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        logger.error(f"Failed to open video device at index {camera_index}")
        raise RuntimeError(f"Could not open video device at index {camera_index}")

    try:
        while True:
            success, frame = cap.read()
            if not success:
                logger.warning("Blank frame grabbed or camera disconnected.")
                break
                
            # --- Object Detection Program Hook Boundary ---
            # When your partner hands over their model pipeline:
            # if model is not None:
            #     results = model(frame)
            #     frame = results[0].plot() 
            
            # Simulated Pipe Tracking Box for testing before model integration:
            h, w, _ = frame.shape
            cv2.rectangle(frame, (int(w*0.25), int(h*0.25)), (int(w*0.75), int(h*0.75)), (0, 255, 0), 2)
            cv2.putText(frame, "Pipe (Demo: 88%)", (int(w*0.25), int(h*0.25) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # -----------------------------------------------------

            # Compress frame to a lightweight JPEG buffer
            ret, encoded_jpg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            # Yield frame using standard HTTP multipart stream boundaries
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded_jpg.tobytes() + b'\r\n')
    finally:
        logger.info("Releasing local camera video capture device resource.")
        cap.release()