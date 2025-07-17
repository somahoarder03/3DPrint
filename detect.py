from ultralytics import YOLO
import cv2
import argparse

def sanity_check():
    print("Running sanity check...")
    model_path = "./model/best.pt"
    model = load(model_path)
    if model is None:
        print("Sanity check failed: Could not load model.")
        exit(1)
    image_path="./dummy_image.jpg"
    res = model.predict(image_path)
    print("Sanity check successful.")
    exit(0)

def load(model_path):
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        print(f"Error: {e}")
        return None

def detect_image(model, image_path="./dummy_image.jpg"):

    print(f"Performing detection on {image_path}...")
    try:
        res=model.predict(image_path)
        for result in res:
            img = result.orig_img.copy()  # Original image
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls_id]
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow("Detected Image", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error during image detection: {e}")
        exit(1)
    return None

def detect_live(model):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Unable to access camera")
        exit()
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame")
            break

        results = model.predict(frame)

        annotated = results[0].plot()

        cv2.imshow("Prediction", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Exited")
    cam.release()
    cv2.destroyAllWindows()

def main():

    model_path="./model/best.pt"
    model=load(model_path)

    ch=input("Enter 1 to test detection\nEnter 2 to test live\nEnter q to exit\n")
    if ch=="1":
        detect_image(model)
    elif ch=="2":
        detect_live(model)
    elif ch=="q":
        exit()
    else:
        print("Invalid input")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Sanity Check')
    args = parser.parse_args()

    if args.test:
        sanity_check()
    else:
        main()