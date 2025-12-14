import requests
import json
import logging

class OllamaLLM:
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger("OllamaLLM")
        self.base_url = "http://localhost:11434/api/chat"
        self.model = model 

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
        
        full_messages = [{"role": "system", "content": "CRITICAL PROTOCOL: YOU ARE AN ENGLISH-ONLY AI. NEVER SPEAK HINDI. " + system_prompt}] + messages_history

        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": False
        }

        try:
            self.logger.info(f"Sending request to Ollama ({self.model})...")
            response = requests.post(self.base_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "")
                
                prompt_tokens = data.get("prompt_eval_count", 0)
                completion_tokens = data.get("eval_count", 0)
                total_tokens = prompt_tokens + completion_tokens
                
                usage = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
                
                return content, usage, self.model
            else:
                self.logger.error(f"Ollama Error: {response.text}")
                return "I'm having trouble thinking locally right now.", None, None

        except requests.exceptions.ConnectionError:
            return "I cannot connect to the local Ollama server. Is it running?", None, None
        except Exception as e:
            self.logger.error(f"Ollama Exception: {e}")
            return "An internal error occurred with my local brain.", None, None

    def get_model_context_limit(self, model_name):
        return 8192
