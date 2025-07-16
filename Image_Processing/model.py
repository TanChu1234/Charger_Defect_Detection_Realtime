import os
os.environ["OMP_NUM_THREADS"] = "1"
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
from pylibdmtx.pylibdmtx import decode

# CATEGORIES = {
#     "defect": ["Scratch", "Text_Scratch", "Qr_Code_Scratch"], #["Text_Defect", "Defect", "QR_Code_Defect"], #, "Qr_Code_Defect"], 
#     "qrcode": ["Qr_code"],
#     "sn": ["Serial_Number"]
#     # "qrcode": ["Logo_Defect"],
#     # "sn": ["QR_Code"]
# }

CATEGORIES = {
    "defect": ["Text_Defect", "Defect", "QR_Code_Defect"],
    "qrcode": ["Qr_code"],
    "sn": ["Serial_Number"]
    # "qrcode": ["Logo_Defect"],
    # "sn": ["QR_Code"]
}

class DetectionModel:
    def __init__(self):
        self.model = YOLO('weights/best_yolov12n_train110_scratch_v1.6.pt')
        # self.model = YOLO('weights/best_yolov12n_train86_scratch_v1.5.1.pt')        
        self.ocr = PaddleOCR(det=False, rec=True, use_angle_cls=True, lang='en')
        self.test_with_dummy_image()
        self.categories = CATEGORIES
        
    def test_with_dummy_image(self):
        dummy_img = np.full((640, 640, 3), 255, dtype=np.uint8)
        self.model(dummy_img)
        # print("Detection model preloaded successfully")

    def order_points(self, pts):
        # pts: array of 4 points
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # Top-left
        rect[2] = pts[np.argmax(s)]  # Bottom-right

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # Top-right
        rect[3] = pts[np.argmax(diff)]  # Bottom-left

        return rect
    
    def read_qr_or_datamatrix(self, img_np):
        # Assume img_np is your input image in BGR format
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
        cv2.imwrite('thresh.png', thresh)  # Save for debugging
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        qr_results = None #temporary variable to store the result
        if contours:  # Check if any contours found
            max_contour = max(contours, key=cv2.contourArea)
            
            epsilon = 0.02 * cv2.arcLength(max_contour, True)
            approx = cv2.approxPolyDP(max_contour, epsilon, True)

            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype(np.float32)
                rect = self.order_points(pts)
                dst = np.array([
                    [0, 0],
                    [99, 0],
                    [99, 99],
                    [0, 99]
                ], dtype="float32")
                M = cv2.getPerspectiveTransform(rect, dst)
                warped = cv2.warpPerspective(img_gray, M, (100, 100))
                cv2.imwrite('warped.png', warped)  # Save for debugging
                # _, thresh_warped = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                # 1. Apply CLAHE (improve local contrast)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(warped)

                # 2. Use Otsu thresholding (less aggressive than adaptive)
                _, thresh_warped = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                # 3. Very light dilation to connect thin lines without removing details
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # smaller kernel
                morphed = cv2.dilate(thresh, kernel, iterations=1)
                cv2.imwrite('thresh_warped.png', thresh_warped)  # Save for debugging   
                # Decode DataMatrix using pylibdmtx
                qr_results = decode(morphed)
             
        if qr_results is not None and qr_results != []:  # Check if any barcode was found
            return qr_results[0].data.decode().split('+')[-1]
        else:
            return None  # No barcode found
    
    def read_serial_number(self, img_np):
        # Convert to grayscale if the image is BGR
        if len(img_np.shape) == 3 and img_np.shape[2] == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_np  # Assume already grayscale

        # Optional: Improve OCR accuracy
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Run OCR
        result = self.ocr.ocr(gray, det=False, rec=True, cls=True)
        print(f"OCR Result: {result}")

        if result and result[0]:
            text = result[0][0][0]
            text = text.replace('$', 'S')
            return text
        else:
            return None
    
    def detection(self, image):    
        orginal_image = image.copy()
        results = self.model(image)
        result = results[0]
        
        found_defect = False
        qr_data = None
        serial_data = None
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]
            # conf = box.conf[0]
            if class_name in self.categories["defect"]:
                found_defect = True            
            
            if class_name == self.categories["qrcode"][0]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                qr_crop = orginal_image[y1:y2, x1:x2]
                cv2.imwrite('qr_crop.png', qr_crop)  # Save for debugging
                qr_data = self.read_qr_or_datamatrix(qr_crop)
                # continue
            elif class_name == self.categories["sn"][0]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])      
                serial_crop = orginal_image[y1:y2, x1:x2]
                cv2.imwrite('serial_crop.png', serial_crop) 
                serial_data = self.read_serial_number(serial_crop)
                # continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 0, 255) if class_name in self.categories["defect"] else (0, 255, 0)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            # label = f"{class_name} {conf:.2f}"
            # label = f"{class_name}"
            # cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        
        return image, found_defect, qr_data, serial_data
    
class PositionOffset:
    def __init__(self):
        self.model = YOLO('weights/best_yolov12_cls_n_v0.1.pt')
        self.is_wrong_position = False
        self.test_with_dummy_image()

    def test_with_dummy_image(self):
        dummy_img = np.full((640, 640, 3), 255, dtype=np.uint8)
        self.model(dummy_img)
        # print("Detection model preloaded successfully")
        
    def classify(self, image):
        results = self.model(image)
        result = results[0]
        class_id = int(result.probs.top1)          # Top class index
        class_name = result.names[class_id]   
        if class_name == "standard":
            cv2.putText(image, class_name, (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # self.is_wrong_position = False
        else:
            cv2.putText(image, class_name, (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # self.is_wrong_position = True
        
        
        return image, class_name #self.is_wrong_position
    
    
class AdapterDetectionModel:
    def __init__(self):
        self.model = YOLO('weights/best_yolov12n_train109_adapter_0.7.pt')
        self.test_with_dummy_image()
        
    def test_with_dummy_image(self):
        dummy_img = np.full((640, 640, 3), 255, dtype=np.uint8)
        self.model(dummy_img)
        # print("Detection model preloaded successfully")

    def detecting(self, image):
        raw_image = image.copy()
        rgb_image = cv2.cvtColor(raw_image, cv2.COLOR_GRAY2RGB)
        # rgb_image_rotated = cv2.rotate(rgb_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        results = self.model(rgb_image)
        result = results[0]
        # result_rotated = cv2.rotate(rgb_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return result, rgb_image
    
    # def crop_adapter(self,image):
        # result, rgb_image = self.detecting(image)
    
    def crop_adapter(self, result, image):
        adapter_crop = None
        rgb_image = image.copy()
        height, width = rgb_image.shape[:2]
        padding = 10
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]
            # conf = box.conf[0]
            if class_name == "Adapter":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Apply padding and clamp to image size
                x1_p = max(x1 - padding, 0)
                y1_p = max(y1 - padding, 0)
                x2_p = min(x2 + padding, width)
                y2_p = min(y2 + padding, height)
                
                # adapter_crop = rgb_image[y1:y2, x1:x2]
                adapter_crop = rgb_image[y1_p:y2_p, x1_p:x2_p]
                break    
        return adapter_crop
    
    def find_offset(self, result, image):
        # result, _ = self.detecting(image)

        adapter_bbox = []
        text_bbox = []
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]
            # conf = box.conf[0]
            if class_name == "Adapter":
                adapter_bbox = box.xyxy[0]
            elif class_name == "Text_Area":
                text_bbox = box.xyxy[0]
                
        x0, y0, x1, y1 = map(int, adapter_bbox)
        x2, y2, x3, y3 = map(int, text_bbox)
        
        d_left   = x2 - x0
        d_top    = y2 - y0
        d_right  = x1 - x3
        d_bottom = y1 - y3
        
        print(f"adapter: {adapter_bbox} - text_box: {text_bbox}")
        
        print(f"Distance: Left: {d_left} -- Top: {d_top} -- Right: {d_right} -- Bottom: {d_bottom}")
        
        # color = (0, 0, 255) if class_name in self.categories["defect"] else (0, 255, 0)
        # cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)
        # im = image[y2:y2 + h2, x2, x2 + w2]
        # cv2.imwrite("text.bmp", im)
        
        # font = cv2.FONT_HERSHEY_SIMPLEX
        
        # def draw_line_and_text(p1, p2, text, color=(0, 0, 255)):
        #     cv2.line(image, p1, p2, color, 1, cv2.LINE_AA)
        #     mid = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        #     cv2.putText(image, f"{text}px", mid, font, 0.5, color, 1, cv2.LINE_AA)

        # draw_line_and_text((x1, y2), (x2, y2), f"L: {d_left}")
        # draw_line_and_text((x2 + w2, y2), (x1 + w1, y2), f"R: {d_right}")

        # draw_line_and_text((x2, y1), (x2, y2), f"T: {d_top}")
        # draw_line_and_text((x2, y2 + h2), (x2, y1 + h1), f"B: {d_bottom}")

        # # Kiểm tra lệch trái-phải
        # warn_color = (0, 0, 255)  # đỏ
        # if abs(d_left - d_right) > tolerance:
        #     msg = f"⚠ Lệch trái-phải: {abs(d_left - d_right)} px"
        #     cv2.putText(image, msg, (10, 20), font, 0.6, warn_color, 2)

        # # Kiểm tra lệch trên-dưới
        # if abs(d_top - d_bottom) > tolerance:
        #     msg = f"⚠ Lệch trên-dưới: {abs(d_top - d_bottom)} px"
        #     cv2.putText(image, msg, (10, 45), font, 0.6, warn_color, 2)

        return image
    