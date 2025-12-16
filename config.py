import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "Ava"
    STT_MODEL_SIZE = "base"
    STT_DEVICE = "cpu"
    STT_COMPUTE_TYPE = "int8"
    USER_NAME = "Saraans"
    OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API")
    

    # LLM Provider: "OPENROUTER", "COHERE"
    LLM_PROVIDER = "OPENROUTER"
    SCREEN_READER_API_KEY = os.getenv("SCREEN_READER_API_KEY")

