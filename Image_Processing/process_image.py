import os
from datetime import datetime
import cv2
import numpy as np

class ImageFunction:
    @staticmethod
    def ignore_empty_rows(img, bbox, threshold=240, direction='top-down'):
        """
        Find the unimportant rows in the image based on the threshold.

        Parameters:
            img (np.ndarray): The input image (grayscale).
            bbox (list): The bounding box coordinates [x, y, w, h].
            threshold (int): The threshold value to determine empty rows. Default is 240.
            direction (str): The direction to search for empty rows ('top-down' or 'bottom-up'). Default is 'top-down'.
        
        Returns:

            bbox (list): The  bounding box coordinates [x, y, w, h] after ignoring empty rows.
        """

        img = img if direction == 'top-down' else img[::-1]

        for idx, row in enumerate(img):
            if np.mean(row) < threshold:
                num_rows = idx 
                break

        bbox[1] = bbox[1] + num_rows if direction == 'top-down' else bbox[1] - num_rows
        bbox[-1] -= num_rows

        return bbox
    
    @staticmethod
    def cropping_img(image, bbox):
        """
        Crop the image based on the bounding box coordinates.

        Parameters:
            image (np.ndarray): The input image.
            bbox (list): The bounding box coordinates [x, y, w, h].
        
        Returns:
            cropped_img (np.ndarray): The cropped image based on the bounding box.
        """
        x1 = bbox[0]
        y1 = bbox[1]
        x2 = bbox[0] + bbox[2]
        y2 = bbox[1] + bbox[3]

        cropped_img = image[y1:y2, x1:x2]
        return cropped_img

    @staticmethod
    def processing_image(gray):
        """
        Process the image to find the bounding box of the object.
        Returns:
            cropped_sample (np.ndarray): The cropped and enhanced image.
        """
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        best_rect = None
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > max_area and area > 1000:
                max_area = area
                best_rect = [x, y, w, h]

        if best_rect is None:
            raise ValueError("No suitable contour found.")

        cropped_img = ImageFunction.cropping_img(gray, best_rect)
        best_rect = ImageFunction.ignore_empty_rows(cropped_img, best_rect)
        best_rect = ImageFunction.ignore_empty_rows(cropped_img, best_rect, direction='bottom-up')
        cropped_sample = ImageFunction.cropping_img(gray, best_rect)

        # clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(2, 2))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        cropped_sample = clahe.apply(cropped_sample)

        # Ensure 3-channel BGR image
        if len(cropped_sample.shape) == 2 or (len(cropped_sample.shape) == 3 and cropped_sample.shape[2] == 1):
            cropped_sample = cv2.cvtColor(cropped_sample, cv2.COLOR_GRAY2BGR)

        return cropped_sample
    
    @staticmethod 
    def crop_and_align(img, padding=10):
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        # Threshold the image
        _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            print("No contours found.")
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if len(img.shape) == 2 else img

        # Use the largest contour
        cnt = max(contours, key=cv2.contourArea)

        # Get the minimum area rectangle (rotated rect)
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # returns float32
        box = np.array(box, dtype=np.float32)

        # Compute rotation matrix to align the object
        center = rect[0]
        angle = rect[2]

        # Adjust angle to ensure the shorter side is horizontal
        height, width = rect[1]
        if width < height:
            angle -= 90

        # Rotate the entire image
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rot_mat, (img.shape[1], img.shape[0]), flags=cv2.INTER_CUBIC)

        # Transform box points using the same rotation matrix
        transformed = cv2.transform(np.array([box]), rot_mat)
        pts = np.int32(transformed[0])  # Ensure valid shape and type

        if pts.shape[0] < 3:
            print("Transformed box has fewer than 3 points.")
            return img

        # Get bounding box from rotated contour
        x, y, w, h = cv2.boundingRect(pts)
        x = max(x - padding, 0)
        y = max(y - padding, 0)
        cropped = rotated[y:y + h + 2 * padding, x:x + w + 2 * padding]

        # Ensure output is 3-channel BGR
        if len(cropped.shape) == 2 or cropped.shape[2] == 1:
            cropped = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)

        return cropped
    
    @staticmethod
    def save(image, annotated_img, output_dir, output_dir_ori):
        for dir_path in [output_dir, output_dir_ori]:
            if not os.path.exists(dir_path):
                return False
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"result_{timestamp}.jpg")
        original_path = os.path.join(output_dir_ori, f"result_{timestamp}.jpg")
        
        cv2.imwrite(output_path, annotated_img)
        cv2.imwrite(original_path, image)
        
        return True