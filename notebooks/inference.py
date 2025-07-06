import os
import cv2
from ultralytics import YOLO

# --- CONFIGURATION ---
model_path = r'weights\best.pt'  # Replace with your trained YOLO model path
# image_folder = r"D:\CHARGER\Sample_20_06\New folder"  # Replace with path to your image folder
image_folder = r"D:\CHARGER\Sample_20_06\New folder (3)\gray_images" # Replace with path to your image folder

# output_folder = os.path.join(image_folder, "cropped_objects")
annotated_folder = os.path.join(image_folder, "annotated")
# os.makedirs(output_folder, exist_ok=True)
os.makedirs(annotated_folder, exist_ok=True)

# --- LOAD MODEL ---
model = YOLO(model_path)

# --- RUN INFERENCE ON EACH IMAGE ---
for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
        img_path = os.path.join(image_folder, filename)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Could not load {filename}")
            continue

        # Run inference
        results = model(img)[0]  # First result from list

        # Save each cropped object
        for i, box in enumerate(results.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            area = (x2 - x1) * (y2 - y1)
            # print(f"  🔹 Object {i + 1}: Area = {area} pixels²")
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Green box, thickness 2
            cropped = img[y1:y2, x1:x2]
            # out_name = f"{os.path.splitext(filename)[0]}.jpg"
            # cv2.imwrite(os.path.join(output_folder, out_name), cropped)
        annotated_path = os.path.join(annotated_folder, filename)
        cv2.imwrite(annotated_path, img)
        print(f"Processed: {filename}")

print("✅ Done! Cropped objects saved.")

