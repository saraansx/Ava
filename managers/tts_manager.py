
import logging
import re
from modules.tts.edge_tts_engine import EdgeTTS
from config import Config

class TTSManager:
    def __init__(self):
        self.logger = logging.getLogger("TTSManager")
        self.engine = EdgeTTS(temp_folder="temp")
        self.default_voice = 'en-IE-EmilyNeural'
        self.last_spoken = ""

    def speak(self, text):
        self.logger.info(f"Speaking: {text}")
        
        clean_text = re.sub(r'\*.*?\*', '', text).strip()
        
        if clean_text:
            self.last_spoken = clean_text
            self.engine.speak(clean_text, voice=self.default_voice)

    def stop(self):
        self.engine.stop()

    def wait(self):
        self.engine.wait()
