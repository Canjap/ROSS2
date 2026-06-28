import cv2

hog = cv2.HOGDescriptor()
default_detector = cv2.HOGDescriptor_getDefaultPeopleDetector()
hog.setSVMDetector(default_detector)

image = cv2.imread("people.jpg")

image = cv2.resize(image, (640, 480))

boxes, weights = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

for (x, y, w, h) in boxes:
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Human Detection", image)

cv2.waitKey(0)
cv2.destroyAllWindows()