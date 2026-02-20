# ========================================
# YOLO LESION DETECTION + VISUALIZATION
# ========================================

from ultralytics import YOLO
import cv2
import os

# load model once when server starts
# Get absolute path of current file (yolo_service.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct full path to models/best.pt
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

model = YOLO(MODEL_PATH)

def predict_ultrasound(image_path):

    # run detection
    results = model(image_path)

    result = results[0]

    # read original image
    img = cv2.imread(image_path)

    boxes = result.boxes

    # if no lesion
    if boxes is None or len(boxes) == 0:
        return "No lesion detected in ultrasound image.", None

    # draw bounding boxes
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # draw rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # label
        cv2.putText(
            img,
            "Lesion",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

    # estimate lesion size
    largest = max(boxes, key=lambda b: b.xywh[0][2] * b.xywh[0][3])
    width = float(largest.xywh[0][2])
    height = float(largest.xywh[0][3])
    size_cm = round((width + height) / 200, 2)

    findings = f"Lesion detected in breast ultrasound. Approx size {size_cm} cm."

    # save annotated image
    output_path = f"annotated_{os.path.basename(image_path)}"
    cv2.imwrite(output_path, img)

    return findings, output_path
