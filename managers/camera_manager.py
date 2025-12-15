import cv2
import threading
import time
import base64
import logging

class CameraManager:
    def __init__(self):
        self.logger = logging.getLogger("CameraManager")
        self.cap = None
        self.running = False
        self.latest_frame = None
        self.lock = threading.Lock()
        
        self.start_camera()

    def start_camera(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        self.logger.info("Initializing Camera...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            self.logger.error("Could not allow webcam access.")
            self.running = False
            return

        self.logger.info("Camera Active (Background Mode)")

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.latest_frame = frame
            time.sleep(0.03)

        self.cap.release()

    def get_latest_frame_b64(self):
        """Returns the latest frame as a base64 string, or None if not available."""
        with self.lock:
            frame = self.latest_frame
        
        if frame is None:
            return None

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return jpg_as_text

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
