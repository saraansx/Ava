import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class CohereLLM:
    def __init__(self, model="command-a-03-2025"):
        self.logger = logging.getLogger("CohereLLM")
        self.api_keys = [key for key in [os.getenv("COHERA_API_KEY"), os.getenv("COHERA_API_KEY_2")] if key]
        self.current_key_index = 0
        self.model = model
        self.base_url = "https://api.cohere.com/v1/chat"

        if not self.api_keys:
            self.logger.error("No Cohere API Keys found in .env (expected COHERA_API_KEY or COHERA_API_KEY_2)")

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
        if not self.api_keys:
            return "My brain is missing its connection key (COHERA_API_KEY).", None, None

        latest_message = "Hello"
        chat_history = []
        
        if messages_history:

             last_msg = messages_history[-1]
             content = last_msg['content']
             if isinstance(content, list):
                 text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
                 latest_message = " ".join(text_parts)
             else:
                 latest_message = content
                 
             raw_history = messages_history[:-1]
             for msg in raw_history:
                 role = "USER" if msg["role"] == "user" else "CHATBOT"
                 content = msg["content"]
                 if isinstance(content, list):
                     text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
                     content = " ".join(text_parts)
                 chat_history.append({"role": role, "message": str(content)})
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

        errors = []
        for i in range(len(self.api_keys)):
            
            key_idx = (self.current_key_index + i) % len(self.api_keys)
            api_key = self.api_keys[key_idx]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            try:
                self.logger.info(f"Sending request to Cohere ({self.model}) with Key #{key_idx + 1}...")
                response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=30)
                
                if response.status_code == 200:
                    self.current_key_index = key_idx
                    
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
                    self.logger.warning(f"Cohere Key #{key_idx + 1} Failed ({response.status_code}): {response.text}")
                    errors.append(f"Key {key_idx+1}: {response.status_code}")
            
            except Exception as e:
                self.logger.error(f"Cohere Request Exception with Key #{key_idx + 1}: {e}")
                errors.append(f"Key {key_idx+1}: {str(e)}")

        error_msg = f"All Cohere keys failed. Errors: {', '.join(errors)}"
        self.logger.error(error_msg)
        return "I lost my connection to the Cohere cloud (All keys failed).", None, None

    def get_model_context_limit(self, model_name):
        return 128000
