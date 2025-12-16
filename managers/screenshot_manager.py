import os
import logging
from PIL import ImageGrab
from datetime import datetime

class ScreenshotManager:
    def __init__(self, temp_dir="temp"):
        self.logger = logging.getLogger("ScreenshotManager")
        self.temp_dir = temp_dir
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def capture_screen(self):
        """Captures the screen and saves it to a temporary file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            file_path = os.path.join(self.temp_dir, filename)
            
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            
            self.logger.info(f"Screenshot captured and saved to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return None

    def delete_screenshot(self, file_path):
        """Deletes the specific screenshot file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted screenshot: {file_path}")
            else:
                self.logger.warning(f"File not found for deletion: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to delete screenshot {file_path}: {e}")
