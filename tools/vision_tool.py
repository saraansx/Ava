from managers.camera_manager import CameraManager
from BRAIN.vision.vision_cortex import VisionCortex
import logging
import os

class VisionTool:
    def __init__(self):
        self.logger = logging.getLogger("VisionTool")
        self.camera = CameraManager()
        self.cortex = VisionCortex()

    def execute(self, prompt="Describe strictly what you see."):
        self.logger.info("Opening eyes...")
        
        image_path = self.camera.capture_image()
        
        if not image_path:
            return "Failed to capture image from camera."
        
        self.logger.info("Processing visual data...")
        try:
            description = self.cortex.analyze_image(image_path, prompt)
        finally:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    self.logger.info(f"Deleted image: {image_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete image: {e}")
        
        return f"[Visual Observation]: {description}"
