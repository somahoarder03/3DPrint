import time
from ultralytics import YOLO
import cv2
import argparse
#from picamera2 import Picamera2
import requests


from flask import Flask,render_template,Response

app=Flask(__name__)

def sanity_check():
    print("Running sanity check...")
    model_path = "./model/best.pt"
    model = load(model_path)
    if model is None:
        print("Sanity check failed: Could not load model.")
        exit(1)
    image_path="./dummy_image.jpg"
    model.predict(image_path)
    print("Sanity check successful.")
    exit(0)

def load(model_path="./model/best.pt"):
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        print(f"Error: {e}")
        return None

def postprocess(result,model):
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

def detect_image(model=load(), image_path="./dummy_image.jpg"):

    print(f"Performing detection on {image_path}...")
    try:
        res=model.predict(image_path)
        if res is None:
            print("Invalid image path")

        annotated=res[0].plot()
        img=cv2.imencode('.jpg', annotated)[1]
        return img.tobytes()
    except Exception as e:
        print(f"Error during image detection: {e}")
        exit(1)

def detect_live(model=load()):

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()

    try:
        while True:
            frame=picam2.capture_array()

            results = model.predict(frame,verbose=False)

            annotated = results[0].plot()
            jpeg=cv2.imencode('.jpg', annotated)[1]
            try:

                is_defect_detected = bool(results and results[0].boxes)

                # Yield the frame in the multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                time.sleep(0.05)
            except Exception as e:
                print(f"Error sending frame to server: {e}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("User Interrupted")
    except Exception as e:
        print(f"Error during : {e}")
    finally:
        picam2.stop()
        print("Camera released. Exited.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(detect_live(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/dummy_image')
def dummy_image():
    return Response(detect_image(), mimetype='image/jpeg')


def main():

    model_path="./model/best.pt"
    model=load(model_path)

    ch=input("Enter 1 to test detection\nEnter 2 to test live\nEnter q to exit\n")

    global app
    app.run(host='0.0.0.0', port=5000, threaded=True)
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