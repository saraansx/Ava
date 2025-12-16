import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class OpenRouterLLM:
    def __init__(self, model="qwen/qwen3-coder:free"):
        self.logger = logging.getLogger("OpenRouterLLM")
        self.api_key = os.getenv("OPENROUTER_AI")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            self.logger.error("No OpenRouter API Key found in .env (expected OPENROUTER_AI)")

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
        if not self.api_key:
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Start-Of-The-Week/Ava",
            "X-Title": "Ava"
        }

        try:
            self.logger.info(f"Sending request to OpenRouter ({self.model})...")
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=30)
            
            if response.status_code == 200:
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
                self.logger.warning(f"OpenRouter Failed ({response.status_code}): {response.text}")
                return f"Error: {response.status_code}", None, None

        except Exception as e:
            self.logger.error(f"OpenRouter Request Exception: {e}")
            return f"Error: {str(e)}", None, None
