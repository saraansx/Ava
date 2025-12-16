import os
import base64
import logging
import requests
from managers.screenshot_manager import ScreenshotManager
from config import Config

class ScreenReader:
    def __init__(self):
        self.logger = logging.getLogger("ScreenReader")
        self.name = "screen_reader"
        self.screenshot_manager = ScreenshotManager()
        self.api_key = Config.SCREEN_READER_API_KEY
        self.model = "google/gemini-2.0-flash-exp:free" 
        self.api_url = "https://openrouter.ai/api/v1/chat/completions" # Defaulting to OpenRouter for flexibility

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def execute(self, user_query="Describe what is on the screen"):
        self.logger.info("Executing Screen Reader...")
        
        # 1. Capture Screenshot
        screenshot_path = self.screenshot_manager.capture_screen()
        if not screenshot_path:
            return "Failed to capture screen."

        try:
            # 2. Prepare API Request
            base64_image = self._encode_image(screenshot_path)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            if not self.api_key:
                self.logger.error("SCREEN_READER_API_KEY not found in config.")
                return "Error: SCREEN_READER_API_KEY is missing."

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this screenshot and answer the user's request: {user_query}. Be concise and direct."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }

            # 3. Call API
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 4. Extract content
            content = result['choices'][0]['message']['content']
            
            self.logger.info("Screen analysis complete.")
            return content

        except Exception as e:
            self.logger.error(f"Error reading screen: {e}")
            return f"I encountered an error trying to read the screen: {str(e)}"
        
        finally:
            self.screenshot_manager.delete_screenshot(screenshot_path)

if __name__ == "__main__":
    reader = ScreenReader()
    if reader.api_key:
        print(reader.execute("What do you see?"))
    else:
        print("Set SCREEN_READER_API_KEY to test.")
