import cv2
import time
import os
import logging

class CameraManager:
    def __init__(self, temp_folder="temp"):
        self.logger = logging.getLogger("CameraManager")
        self.temp_folder = temp_folder
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

    def capture_image(self):
        """Captures a single image from the webcam and saves it to a temp file."""
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                self.logger.error("Could not open webcam.")
                return None


            time.sleep(1)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                timestamp = int(time.time())
                image_path = os.path.join(self.temp_folder, f"vision_capture_{timestamp}.jpg")
                image_path = os.path.abspath(image_path)
                
                cv2.imwrite(image_path, frame)
                self.logger.info(f"Image captured: {image_path}")
                return image_path
            else:
                self.logger.error("Failed to read frame from camera.")
                return None

        except Exception as e:
            self.logger.error(f"Camera Access Error: {e}")
            return None
