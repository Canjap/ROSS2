import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)

print("Press 'q' to quit the video stream.")

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    frame = cv2.resize(frame, (640, 480))

    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.08)

    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

    final_boxes = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    human_count = len(final_boxes)

    for (startX, startY, endX, endY) in final_boxes:
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        
    cv2.putText(frame, f"Humans Detected: {human_count}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Live Human Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()