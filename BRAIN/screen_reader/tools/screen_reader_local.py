import logging
import os
import requests
import base64
from BRAIN.screen_reader.managers.screenshot_manager import ScreenshotManager

class ScreenReaderLocalTool:
    def __init__(self):
        self.logger = logging.getLogger("ScreenReaderLocalTool")
        self.name = "screen_reader"
        self.manager = ScreenshotManager()
        self.model = "llava:latest"
        self.base_url = "http://localhost:11434/api/generate"

    def execute(self, prompt="Describe what is on my screen."):
        self.logger.info(f"Local Screen Reader (Ollama - {self.model})...")
        
        image_path = self.manager.capture_screen()
        if not image_path:
            return "Failed to capture screen."

        try:
            # Prepare image as base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }

            self.logger.info(f"Sending visual query to Ollama ({self.model})...")
            response = requests.post(self.base_url, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                content = data.get("response", "")
                return f"[Screen Reader (Local)]: {content}"
            else:
                self.logger.error(f"Ollama API Error ({response.status_code}): {response.text}")
                return "My local vision is blurry. Is Ollama running with llava:latest?"

        except requests.exceptions.ConnectionError:
            return "I cannot connect to the local Ollama server. Please ensure Ollama is running."
        except Exception as e:
            self.logger.error(f"Ollama Error: {e}")
            return f"Error using local vision model: {e}"
        finally:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except:
                    pass
