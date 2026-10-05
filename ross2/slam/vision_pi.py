import cv2
import time
import numpy as np
import threading
from typing import Generator
from loguru import logger
from picamera2 import Picamera2
from ultralytics import YOLO

# PICAR
from picarx.utils import reset_mcu
from picarx import Picarx
from time import sleep
import readchar

reset_mcu()
sleep(0.2)

manual = '''
Press key to call the function(non-case sensitive):

    O: speed up
    P: speed down
    W: forward
    S: backward
    A: turn left
    D: turn right
    F: stop
    T: take photo

    Ctrl+C: quit
'''

# Initialize Picar
px = Picarx()

# Initialize the camera GLOBALLY
try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    logger.info("Global Pi 5 Camera Hardware locked and started.")
except Exception as e:
    logger.error(f"Failed to initialize global camera: {e}")

# Initialize models once at startup
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Using cv2.data.haarcascades prevents the persistence read error
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
yolo = YOLO('yolo26n.pt')

def move(operate, speed):
    if operate == 'stop':
        px.stop()
    else:
        if operate == 'forward':
            px.set_dir_servo_angle(0)
            px.forward(speed)
        elif operate == 'backward':
            px.set_dir_servo_angle(0)
            px.backward(speed)
        elif operate == 'turn left':
            px.set_dir_servo_angle(-30)
            px.forward(speed)
        elif operate == 'turn right':
            px.set_dir_servo_angle(30)
            px.forward(speed)

def movement_control():
    speed = 0
    status = "stop"

    sleep(2)
    print(manual)

    # Keyboard control --- must be put under a while loop to work
    while True:
        print("\rstatus: %s , speed: %s    "%(status, speed), end='', flush=True)

        # readkey
        key = readchar.readkey().lower()
        
        # operation
        if key in ('wsadfop'):
            # throttle
            if key == 'o':
                if speed <=90:
                    speed += 10
            elif key == 'p':
                if speed >=10:
                    speed -= 10
                if speed == 0:
                    status = 'stop'
            # direction
            elif key in ('wsad'):
                if speed == 0:
                    speed = 10
                if key == 'w':
                    # Speed limit when reversing,avoid instantaneous current too large
                    if status != 'forward' and speed > 60:
                        speed = 60
                    status = 'forward'
                elif key == 'a':
                    status = 'turn left'
                elif key == 's':
                    if status != 'backward' and speed > 60: # Speed limit when reversing
                        speed = 60
                    status = 'backward'
                elif key == 'd':
                    status = 'turn right'
            # stop
            elif key == 'f':
                status = 'stop'
            # move
            move(status, speed)

        # quit
        elif key == readchar.key.CTRL_C:
            print('\nquiting movement script ...')
            px.stop()
            break # Exits the while loop and terminates the thread

        sleep(0.1)

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


    elif model=="yolo":
        results = yolo(frame, classes=[0], conf=0.5, verbose=False)
        human_count = len(results[0].boxes)
        frame = results[0].plot()


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


movement_thread_started = False 

def stream_frames_movement(
    camera_index: int = 0, enable_detection: bool = False, model: str = "cascade"
) -> Generator[bytes, None, None]:
    """Yields frames from the globally running Picamera2 buffer."""

    global movement_thread_started
    logger.info(f"New client connected! (Detection: {enable_detection}, Model: {model})")

    # Start the keyboard listener in a background thread only once
    if not movement_thread_started:
        threading.Thread(target=movement_control, daemon=True).start()
        movement_thread_started = True

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
