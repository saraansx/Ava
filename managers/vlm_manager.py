import base64
import logging
from io import BytesIO
import requests
from PIL import ImageGrab

class VLMManager:
    def __init__(self, model="minicpm-v"):
        self.logger = logging.getLogger("VLMManager")
        self.model = model
        # Assuming Ollama is running on default port
        self.api_url = "http://localhost:11434/api/generate" 

    def capture_screen(self):
        try:
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            self.logger.error(f"Failed to capture screen: {e}")
            return None

    def analyze_screen(self, user_query=None):
        base_prompt = "Briefly list the main applications and content visible on the screen."
        
        if user_query:

            final_prompt = f"User Question: '{user_query}'. Answer this question based on the screen content. Be extremely concise. OUTPUT IN ENGLISH ONLY."
        else:
             final_prompt = f"{base_prompt} OUTPUT IN ENGLISH ONLY."
        screenshot = self.capture_screen()
        if not screenshot:
            return "Failed to capture screen."

        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "images": [img_str],
            "stream": False
        }

        try:
            self.logger.info(f"Sending screen to {self.model} for analysis...")
            response = requests.post(self.api_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from VLM.")
            else:
                self.logger.error(f"VLM Error {response.status_code}: {response.text}")
                return f"Error from VLM: {response.text}"
                
        except Exception as e:
            self.logger.error(f"VLM Analysis Failed: {e}")
            return f"Error analyzing screen: {e}"
