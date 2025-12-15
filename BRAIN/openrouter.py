import os
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

class OpenRouterLLM:
    def __init__(self):
        self.logger = logging.getLogger("OpenRouterLLM")
        self.api_key = os.getenv("OPENROUTER_AI") or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            self.logger.error("OpenRouter API Key not found in .env (expected OPENROUTER_AI)")
        

        self.model = "meta-llama/llama-3.3-70b-instruct"

    def extract_city(self, text):
        prompt = f"Extract the city name from this user query: '{text}'. Return ONLY the city name. If no city is specified, return 'None'. Do not add any punctuation or extra words."
        try:
            content, _, _ = self.generate([], system_prompt=prompt)
            return content.strip()
        except:
            return "None"

    def extract_news_topic(self, text):
        prompt = f"Extract the news topic or category from this user query: '{text}'. Return ONLY the topic keywords (e.g., 'Artificial Intelligence', 'Bitcoin', 'Politics'). If the user asks for general news or doesn't specify a topic, return 'None'. Do not add any punctuation or extra words."
        try:
            content, _, _ = self.generate([], system_prompt=prompt)
            return content.strip()
        except:
            return "None"

    def generate(self, messages_history, system_prompt, image_data=None):
        if not self.api_key:
            return "My brain is missing its connection key (OPENROUTER_AI).", None, None

        full_messages = [{"role": "system", "content": "CRITICAL PROTOCOL: YOU ARE AN ENGLISH-ONLY AI. NEVER SPEAK HINDI. "+system_prompt}] + messages_history

        # Inject Image Data if Present
        if image_data:
            for msg in reversed(full_messages):
                if msg['role'] == 'user':
                    original_text = msg['content']
                    msg['content'] = [
                        {
                            "type": "text",
                            "text": original_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                    break

        success, response, usage = self._call_model(self.model, full_messages)
        if success:
            return response, usage, self.model
        else:
            return f"I apologize, but I encountered an error: {response}", None, None

    def _call_model(self, model, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:3000", 
            "X-Title": "Jarvis Assistant",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            self.logger.info(f"Attempting to generate with model: {model}")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=15 
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    usage = data.get('usage', {})
                    return True, content, usage
                else:
                    self.logger.warning(f"OpenRouter response missing choices: {data}")
                    return False, "OpenRouter sent an empty response.", None
            else:
                error_msg = f"OpenRouter Error {response.status_code}: {response.text}"
                self.logger.warning(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            self.logger.error(f"Request Error ({model}): {e}")
            return False, f"Connection Error: {str(e)}", None

    def get_model_context_limit(self, model_name):
        limits = {
            "meta-llama/llama-3.3-70b-instruct": 128000,
        }
        return limits.get(model_name, 4096)
