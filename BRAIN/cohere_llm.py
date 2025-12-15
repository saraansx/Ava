import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class CohereLLM:
    def __init__(self, model="command-a-03-2025"):
        self.logger = logging.getLogger("CohereLLM")
        self.api_key = os.getenv("COHERA_API_KEY")
        self.model = model
        self.base_url = "https://api.cohere.com/v1/chat"

        if not self.api_key:
            self.logger.error("Cohere API Key not found in .env (expected COHERA_API_KEY)")

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

    def generate(self, messages_history, system_prompt):
        if not self.api_key:
            return "My brain is missing its connection key (COHERA_API_KEY).", None, None

        latest_message = "Hello"
        chat_history = []
        
        if messages_history:
             last_msg = messages_history[-1]
             if last_msg['role'] == 'user':
                 latest_message = last_msg['content']
                 raw_history = messages_history[:-1]
             else:
                 latest_message = last_msg['content']
                 raw_history = messages_history[:-1]
             for msg in raw_history:
                 role = "USER" if msg["role"] == "user" else "CHATBOT"
                 chat_history.append({"role": role, "message": msg["content"]})
        else:
            pass

        full_preamble = "CRITICAL PROTOCOL: YOU ARE AN ENGLISH-ONLY AI. NEVER SPEAK HINDI. " + system_prompt

        payload = {
            "model": self.model,
            "message": latest_message,
            "chat_history": chat_history,
            "preamble": full_preamble,
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            self.logger.info(f"Sending request to Cohere ({self.model})...")
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("text", "")
                
             
                meta = data.get("meta", {}).get("billed_units", {})
                usage = {
                    "prompt_tokens": meta.get("input_tokens", 0),
                    "completion_tokens": meta.get("output_tokens", 0),
                    "total_tokens": meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
                }
                
                return content, usage, self.model
            else:
                self.logger.error(f"Cohere Error ({response.status_code}): {response.text}")
                return f"I encountered an error connecting to Cohere: {response.status_code}", None, None

        except Exception as e:
            self.logger.error(f"Cohere Request Exception: {e}")
            return "I lost my connection to the Cohere cloud.", None, None

    def get_model_context_limit(self, model_name):
        return 128000
