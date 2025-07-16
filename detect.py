from ultralytics import YOLO
import cv2

model = YOLO("model/best.py")

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Unable to access camera")
    exit()

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to capture frame")
        break


    results = model.predict()
    annotated = results[0].plot()

    cv2.imshow("Prediction", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Exited")
cam.release()
cv2.destroyAllWindows()
