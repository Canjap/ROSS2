import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# 2. Open the Default Webcam (0 is usually your built-in laptop camera)
cap = cv2.VideoCapture(0)

print("Press 'q' to quit the video stream.")

while True:
    # 3. Read a single frame from the camera
    ret, frame = cap.read()
    
    # If the camera didn't return a frame, break the loop
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    # 4. Resize for performance (Crucial for real-time video)
    frame = cv2.resize(frame, (640, 480))

    # 5. Detect humans
    # Note: winStride is increased to (8,8) and scale to 1.08 to make it run faster on video
    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.08)

    # 6. Format the boxes for Non-Maximum Suppression
    # HOG returns [x, y, w, h], but NMS needs [startX, startY, endX, endY]
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

    # 7. Apply Non-Maximum Suppression to remove overlapping boxes
    # overlapThresh=0.65 means if boxes overlap by 65% or more, merge them.
    final_boxes = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    # 8. Count the humans
    # The number of humans is just the length of our final_boxes list
    human_count = len(final_boxes)

    # 9. Draw the final boxes and the count on the frame
    for (startX, startY, endX, endY) in final_boxes:
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        
    # Put the text counter in the top left corner
    cv2.putText(frame, f"Humans Detected: {human_count}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 10. Display the live feed
    cv2.imshow("Live Human Counter", frame)

    # 11. Listen for the 'q' key to quit
    # waitKey(1) pauses for 1 millisecond to update the window. 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 12. Clean up and release the camera
cap.release()
cv2.destroyAllWindows()