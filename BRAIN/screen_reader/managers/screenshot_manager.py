import os
import logging
import uuid
from PIL import ImageGrab

class ScreenshotManager:
    def __init__(self, temp_dir="temp"):
        self.logger = logging.getLogger("ScreenshotManager")
        self.temp_dir = temp_dir
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def capture_screen(self):
        try:
            filename = f"screenshot_{uuid.uuid4().hex}.png"
            filepath = os.path.join(self.temp_dir, filename)
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            self.logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
