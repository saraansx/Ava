from managers.camera_manager import CameraManager
from BRAIN.vision.vision_cortex import VisionCortex
import logging

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
        description = self.cortex.analyze_image(image_path, prompt)
        
        return f"[Visual Observation]: {description}"
