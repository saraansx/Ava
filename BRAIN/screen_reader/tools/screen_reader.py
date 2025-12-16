import os
import logging
import base64
import json
import requests
from BRAIN.screen_reader.managers.screenshot_manager import ScreenshotManager

class ScreenReaderTool:
    def __init__(self):
        self.logger = logging.getLogger("ScreenReaderTool")
        self.name = "screen_reader"
        self.manager = ScreenshotManager()
        self.api_key = os.getenv("SCREEN_READER_API_KEY")
        self.model = "meta-llama/llama-3.2-90b-vision-instruct" 
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def execute(self, prompt="Describe what is on my screen."):
        if not self.api_key:
            self.logger.error("SCREEN_READER_API_KEY not found in env.")
            return "I cannot read the screen because the API key is missing."

        self.logger.info("Capturing screen...")
        image_path = self.manager.capture_screen()
        
        if not image_path:
            return "Failed to capture the screen."

        try:
            self.logger.info("Analyzing screen content...")
            
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Start-Of-The-Week/Ava",
                "X-Title": "Ava"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=60)

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                return f"[Screen Reader]: {content}"
            else:
                self.logger.error(f"Screen Reader API Error ({response.status_code}): {response.text}")
                return "My vision is blurry. I couldn't process the screen."

        except Exception as e:
            self.logger.error(f"Screen Reader Exception: {e}")
            return "I encountered an error while trying to read the screen."
        finally:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    self.logger.info(f"Deleted screenshot: {image_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete screenshot: {e}")
