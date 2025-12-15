import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class VisionCortex:
    def __init__(self, model="meta-llama/llama-3.2-90b-vision-instruct"):
        self.logger = logging.getLogger("VisionCortex")
        self.api_key = os.getenv("VISUAL_CORTEX")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            self.logger.error("Visual Cortex API Key not found in .env (expected VISUAL_CORTEX)")

    def analyze_image(self, image_path, prompt="What do you see in this image?"):
        if not self.api_key:
            return "Visual Cortex is offline (Missing API Key).", None
        
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found at: {image_path}")
            return "I cannot see anything because the image capture failed.", None

        try:
            import base64
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

            self.logger.info(f"Sending visual data to OpenRouter ({self.model})...")
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=60)

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                usage_raw = data.get("usage", {})
                usage_data = {
                    "prompt_tokens": usage_raw.get("prompt_tokens", 0),
                    "completion_tokens": usage_raw.get("completion_tokens", 0),
                    "total_tokens": usage_raw.get("total_tokens", 0),
                    "model": self.model
                }
                
                return content, usage_data
            else:
                self.logger.error(f"Vision API Error ({response.status_code}): {response.text}")
                return "My vision is blurry. I couldn't process the image.", None

        except Exception as e:
            self.logger.error(f"Visual Cortex Exception: {e}")
            return "I encountered a neural error while trying to see.", None
