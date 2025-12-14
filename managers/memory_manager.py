
import json
import os
import logging

class MemoryManager:
    def __init__(self, memory_file="memory/memory.json"):
        self.logger = logging.getLogger("MemoryManager")
        self.memory_file = memory_file
        self.memory = []
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
                self.logger.info("Memory loaded.")

            except Exception as e:
                self.logger.error(f"Failed to load memory: {e}")
                self.memory = []
        else:
            self.memory = []
            self.logger.info("No existing memory found. Starting fresh.")

    def save_memory(self):
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")

    def add_message(self, role, content):
        self.memory.append({"role": role, "content": content})
        self.save_memory()

    def get_messages(self):
        return self.memory

    def clear_memory(self):
        self.memory = []
        self.save_memory()
