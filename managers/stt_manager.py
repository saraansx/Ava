
from modules.stt.listener import SpeechToTextListener
import logging

class STTManager:
    def __init__(self):
        self.logger = logging.getLogger("STTManager")
        self.listener = SpeechToTextListener(language="en-IN")
    
    def listen(self, callback=None):
        text = self.listener.run_cycle(callback=callback)
        return text
