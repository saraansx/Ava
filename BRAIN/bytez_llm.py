import os
import logging
from dotenv import load_dotenv
from bytez import Bytez

load_dotenv()

class BytezLLM:
    def __init__(self, model_id="google/gemini-3-pro-preview"):
        self.logger = logging.getLogger("BytezLLM")
        self.api_key = os.getenv("BYTEZ_API") or os.getenv("BYTEZ_API_KEY")
        self.model_id = model_id
        
        if not self.api_key:
            self.logger.error("Bytez API Key not found in .env (expected BYTEZ_API or BYTEZ_API_KEY)")
            self.client = None
        else:
            self.client = Bytez(self.api_key)
            self.model = self.client.model(self.model_id)

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
        if not self.client:
            return "My brain is missing its connection key (BYTEZ_API).", None, None

        # Bytez seems to take a list of messages.
        # We need to prepend the system prompt if possible, or include it in the messages.
        # The user example shows standard role/content dicts.
        
        full_messages = [{"role": "system", "content": "CRITICAL PROTOCOL: YOU ARE AN ENGLISH-ONLY AI. NEVER SPEAK HINDI. " + system_prompt}] + messages_history

        try:
            self.logger.info(f"Sending request to Bytez ({self.model_id})...")
            
            # The Example: output, error = model.run(messages)
            output, error = self.model.run(full_messages)
            
            if error:
                self.logger.error(f"Bytez Error: {error}")
                return f"I encountered an error with my thoughts: {error}", None, None
            
            if output:
                # Bytez run returns output and error. Assuming output is the string content.
                content = output
                
                # Usage stats are not explicitly provided in the simple run return based on the example.
                # We will return None for usage for now on.
                usage = None 
                
                return content, usage, self.model_id
            else:
                self.logger.warning("Bytez returned empty output.")
                return "I couldn't think of a response.", None, None

        except Exception as e:
            self.logger.error(f"Bytez Request Exception: {e}")
            return "I lost my connection to the Bytez cloud.", None, None

    def get_model_context_limit(self, model_name):
        # google/gemini-3-pro-preview likely has a large context
        return 1000000
