import cv2

# 1. Initialize the HOG descriptor and set the SVM detector
hog = cv2.HOGDescriptor()
default_detector = cv2.HOGDescriptor_getDefaultPeopleDetector()
hog.setSVMDetector(default_detector)

# 2. Load the image
image = cv2.imread("people.jpg")

# 3. Resize image for faster processing (Optional but recommended)
image = cv2.resize(image, (640, 480))

# 4. Detect humans in the image
boxes, weights = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

# 5. Draw bounding boxes around detected humans
for (x, y, w, h) in boxes:
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# 6. Display the output image
cv2.imshow("Human Detection", image)

# 7. Keep the window open until a key is pressed
cv2.waitKey(0)
cv2.destroyAllWindows()