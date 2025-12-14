import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    def __init__(self, model="gemini-1.5-flash"):
        self.logger = logging.getLogger("GeminiLLM")
        self.api_key = os.getenv("GEMINI_API")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

        if not self.api_key:
            self.logger.error("Gemini API Key not found in .env (expected GEMINI_API)")

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
            return "My brain is missing its connection key (GEMINI_API).", None, None

        # Convert messages to Gemini format
        gemini_contents = []
        for msg in messages_history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        # Construct payload
        payload = {
            "contents": gemini_contents,
            "systemInstruction": {
                "parts": [{"text": "CRITICAL PROTOCOL: YOU ARE AN ENGLISH-ONLY AI. NEVER SPEAK HINDI. " + system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        try:
            self.logger.info(f"Sending request to Gemini ({self.model})...")
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract content
                try:
                    candidates = data.get("candidates", [])
                    if candidates and candidates[0].get("content"):
                        content = candidates[0]["content"]["parts"][0]["text"]
                    else:
                        self.logger.warning(f"Gemini response missing content: {data}")
                        return "I couldn't think of a response.", None, None
                except (KeyError, IndexError) as e:
                    self.logger.error(f"Error parsing Gemini response: {e} | Data: {data}")
                    return "Error parsing my thoughts.", None, None

                # Extract usage (Gemini returns 'usageMetadata')
                usage_meta = data.get("usageMetadata", {})
                usage = {
                    "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                    "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                    "total_tokens": usage_meta.get("totalTokenCount", 0)
                }

                return content, usage, self.model
            else:
                self.logger.error(f"Gemini Error ({response.status_code}): {response.text}")
                return f"I encountered an error connecting to Gemini: {response.status_code}", None, None

        except Exception as e:
            self.logger.error(f"Gemini Request Exception: {e}")
            return "I lost my connection to the Gemini cloud.", None, None

    def get_model_context_limit(self, model_name):
        # Gemini 1.5 Flash has a large context window (1M tokens)
        return 1000000
