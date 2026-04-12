import cv2
import numpy as np
from ultralytics import YOLO
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment



try:
    model = YOLO("yolov8n.pt")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None


PERSON_CLASS_ID = 0
CHAIR_CLASS_ID = 56

def analyze_room_image(image_bytes: bytes):
    if not model:
        return {"error": "Vision model is not loaded"}


    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image format"}


    results = model(img)

    people = []
    chairs = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])


            x1, y1, x2, y2 = box.xyxy[0]
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            centroid = [float(cx), float(cy)]


            if conf > 0.3:
                if cls_id == PERSON_CLASS_ID:
                    people.append({
                        "centroid": centroid,
                        "box": [float(x1), float(y1), float(x2), float(y2)],
                        "conf": conf
                    })
                elif cls_id == CHAIR_CLASS_ID:
                    chairs.append({
                        "centroid": centroid,
                        "box": [float(x1), float(y1), float(x2), float(y2)],
                        "conf": conf
                    })

    num_people = len(people)
    num_chairs = len(chairs)

    pairs = []


    if num_people > 0 and num_chairs > 0:
        people_coords = [p["centroid"] for p in people]
        chairs_coords = [c["centroid"] for c in chairs]


        dist_matrix = cdist(people_coords, chairs_coords, metric='euclidean')


        row_ind, col_ind = linear_sum_assignment(dist_matrix)

        for person_idx, chair_idx in zip(row_ind, col_ind):
            distance = float(dist_matrix[person_idx, chair_idx])
            pairs.append({
                "person_index": int(person_idx),
                "chair_index": int(chair_idx),
                "distance": distance
            })



    is_full = num_people >= num_chairs if num_chairs > 0 else False

    return {
        "room_status": "full" if is_full else "available",
        "counts": {
            "people": num_people,
            "chairs": num_chairs
        },
        "pairs": pairs,
        "details": {
            "people": people,
            "chairs": chairs
        }
    }
