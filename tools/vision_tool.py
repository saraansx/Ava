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
            description, usage = self.cortex.analyze_image(image_path, prompt)
            
            if usage:
                from rich.console import Console
                from rich.text import Text
                
                console = Console()
                model_name = usage.get('model', 'Unknown Model').split('/')[-1]
                total_tokens = usage.get('total_tokens', 0)
                
                stats_text = Text(f"\n[Vision Cortex] Model: {model_name} | Tokens: {total_tokens}", style="dim white")
                console.print(stats_text)

        finally:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    self.logger.info(f"Deleted image: {image_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete image: {e}")
        
        return f"[Visual Observation]: {description}"
