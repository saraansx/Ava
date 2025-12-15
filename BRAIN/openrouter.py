import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class OpenRouterLLM:
    def __init__(self, model="meta-llama/llama-3.3-70b-instruct"):
        self.logger = logging.getLogger("OpenRouterLLM")
        self.api_keys = [key for key in [os.getenv("OPENROUTER_AI"), os.getenv("OPENROUTER_API_KEY_2")] if key]
        self.current_key_index = 0
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_keys:
            self.logger.error("No OpenRouter API Keys found in .env (expected OPENROUTER_AI or OPENROUTER_API_KEY_2)")

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

    def get_model_context_limit(self, model_name):
        return 128000

    def generate(self, messages_history, system_prompt):
        if not self.api_keys:
            return "My brain is missing its connection key (OPENROUTER_AI).", None, None

        messages = [{"role": "system", "content": system_prompt}]
        
        if messages_history:
            for msg in messages_history:
                content = msg["content"]
                if isinstance(content, list):
                    text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
                    content = " ".join(text_parts)
                
                messages.append({"role": msg["role"], "content": str(content)})

        payload = {
            "model": self.model,
            "messages": messages
        }

        errors = []
        for i in range(len(self.api_keys)):
            key_idx = (self.current_key_index + i) % len(self.api_keys)
            api_key = self.api_keys[key_idx]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Start-Of-The-Week/Ava",
                "X-Title": "Ava"
            }

            try:
                self.logger.info(f"Sending request to OpenRouter ({self.model}) with Key #{key_idx + 1}...")
                response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=30)
                
                if response.status_code == 200:
                    self.current_key_index = key_idx
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    
                    usage_data = data.get("usage", {})
                    usage = {
                        "prompt_tokens": usage_data.get("prompt_tokens", 0),
                        "completion_tokens": usage_data.get("completion_tokens", 0),
                        "total_tokens": usage_data.get("total_tokens", 0)
                    }
                    
                    return content, usage, self.model
                else:
                    self.logger.warning(f"OpenRouter Key #{key_idx + 1} Failed ({response.status_code}): {response.text}")
                    errors.append(f"Key {key_idx+1}: {response.status_code}")

            except Exception as e:
                self.logger.error(f"OpenRouter Request Exception with Key #{key_idx + 1}: {e}")
                errors.append(f"Key {key_idx+1}: {str(e)}")

        error_msg = f"All OpenRouter keys failed. Errors: {', '.join(errors)}"
        self.logger.error(error_msg)
        return "I lost my connection to the OpenRouter cloud (All keys failed).", None, None
