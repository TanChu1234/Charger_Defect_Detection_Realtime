import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
from pylibdmtx.pylibdmtx import decode

CATEGORIES = {
    "defect": ["Scratch", "Text_Scratch", "Qr_Code_Scratch"],
    "qrcode": ["Qr_code"],
    "sn": ["Serial_Number"]
}
class DetectionModel:
    def __init__(self):
        self.model = YOLO('weights/yolov11n_v4.pt')
        self.ocr = PaddleOCR(det=False, rec=True, use_angle_cls=True, lang='en')
        self.found_defect = False
        self.test_with_dummy_image()
        self.categories = CATEGORIES
    def test_with_dummy_image(self):
        dummy_img = np.full((800, 800, 3), 255, dtype=np.uint8)
        self.model(dummy_img)
        print("Detection model preloaded successfully")

    def order_points(self, pts):
        """
        Orders the given four points in a consistent order: top-left, top-right,
        bottom-right, bottom-left.

        This function is commonly used to prepare a set of four points representing
        a quadrilateral for perspective transforms (e.g., with cv2.getPerspectiveTransform).

        Parameters:
            pts (ndarray): A NumPy array of shape (4, 2) representing four (x, y) points.

        Returns:
            rect (ndarray): A NumPy array of shape (4, 2) with points ordered as:
                            [top-left, top-right, bottom-right, bottom-left].
        """
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def read_qr_or_datamatrix(self, img_np):
        # Assume img_np is your input image in BGR format
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 4:
                # Order points
                pts = approx.reshape(4, 2).astype(np.float32)
                rect = self.order_points(pts)
                dst = np.array([
                    [0, 0],
                    [100 - 1, 0],
                    [100 - 1, 100 - 1],
                    [0, 100 - 1]
                ], dtype="float32")

                M = cv2.getPerspectiveTransform(rect, dst)
                warped = cv2.warpPerspective(img_gray, M, (100, 100))
                _, thresh_warped = cv2.threshold(warped, 200, 255, cv2.THRESH_BINARY)
        # Decode DataMatrix using pylibdmtx
        qr_results = decode(thresh_warped)
        
        print(qr_results)
        if qr_results:  # Check if any barcode was found
            return qr_results[0].data.decode().split('+')[-1]
        else:
            return None  # No barcode found
    
    def read_serial_number(self, img_np):
        # # Convert to grayscale if needed
        # if len(img_np.shape) == 3:
        #     if img_np.shape[2] == 1:  # Single-channel (H, W, 1) → reshape to (H, W)
        #         gray = img_np[:, :, 0]  # Remove last dimension
        #     elif img_np.shape[2] == 3:  # BGR → grayscale
        #         gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        #     else:
        #         raise ValueError(f"Unsupported image shape: {img_np.shape}")
        # elif len(img_np.shape) == 2:  # Already grayscale
        #     gray = img_np
        # else:
        #     raise ValueError(f"Unsupported image shape: {img_np.shape}")

        # Optional: Improve OCR accuracy
        gray = cv2.threshold(img_np, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Run OCR
        result = self.ocr.ocr(gray, det=False)

        if result and result[0]:
            text = result[0][0][0]
            text = text.replace('$', 'S')
            return text
        else:
            return None
    
    def detection(self, image):    
        results = self.model(image)
        result = results[0]
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]
            # conf = box.conf[0]

            if class_name in self.categories["defect"]:
                self.found_defect = True
            
            # Check QR_Code and Serial_Number
            if class_name == self.categories["qrcode"][0]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                qr_crop = image[y1:y2, x1:x2]
                qr_data = self.read_qr_or_datamatrix(qr_crop)
                # continue
            elif class_name ==  self.categories["sn"][0]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])      
                serial_crop = image[y1:y2, x1:x2]
                serial_data = self.read_serial_number(serial_crop)
                # print("Serial Number Data:", serial_data)
                # continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 0, 255) if class_name in self.categories["defect"] else (0, 255, 0)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            # label = f"{class_name} {conf:.2f}"
            label = f"{class_name}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return image, self.found_defect, qr_data, serial_data
    
class PositionOffset:
    def __init__(self):
        self.model = YOLO('weights\best_yolov12_cls_n_v0.1.pt')
        self.position_ng = False
        self.test_with_dummy_image()

    def test_with_dummy_image(self):
        dummy_img = np.full((640, 640, 3), 255, dtype=np.uint8)
        self.model(dummy_img)
        print("Detection model preloaded successfully")
        
    def classify(self, image):
        results = self.model(image)
        result = results[0]
        class_id = int(result.probs.top1)          # Top class index
        class_name = result.names[class_id]   
        if class_name == "standard":
            self.position_ng = False
        else:
            self.position_ng = True
        cv2.putText(image, class_name, (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        return image, self.position_ng