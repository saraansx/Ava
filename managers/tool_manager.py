import logging
from config import Config
from tools.weather import WeatherTool
from tools.news import NewsTool
from tools.system_info import SystemInfoTool
from BRAIN.screen_reader.tools.screen_reader import ScreenReaderTool
from BRAIN.screen_reader.tools.screen_reader_local import ScreenReaderLocalTool

class ToolManager:
    def __init__(self, llm_instance=None):
        self.logger = logging.getLogger("ToolManager")
        self.tools = {}
        self.llm = llm_instance
        self._register_tools()

    def _register_tools(self):
        self.register_tool(WeatherTool())
        self.register_tool(NewsTool())
        self.register_tool(SystemInfoTool())

        try:
            if Config.VISION_MODE == "LOCAL":
                self.logger.info("Vision Mode: LOCAL (Ollama)")
                self.register_tool(ScreenReaderLocalTool())
            else:
                self.logger.info("Vision Mode: API (OpenRouter)")
                self.register_tool(ScreenReaderTool())
        except Exception as e:
            self.logger.error(f"Failed to register Screen Reader Tool ({Config.VISION_MODE}): {e}")
        
    def register_tool(self, tool):
        self.tools[tool.name] = tool
        self.logger.info(f"Tool registered: {tool.name}")

    def find_tool_for_intent(self, text):
        text = text.lower()
        if "weather" in text or "vedar" in text or "vader" in text:
            return self.tools.get("weather")
        if "news" in text:
            return self.tools.get("news")
        
        if self.llm:
            if hasattr(self.llm, "extract_screen_reader_intent"):
                screen_intent = self.llm.extract_screen_reader_intent(text)
                if screen_intent and "YES" in screen_intent:
                    self.logger.info(f"LLM decided this is a SCREEN READER request.")
                    return self.tools.get("screen_reader")
        
        system_keywords = [
            "system", "spec", "specs", "processor", "cpu", 
            "memory", "ram", "disk", "storage", "space", "os", "platform",
            "gpu", "graphics", "card"
        ]
        if any(keyword in text for keyword in system_keywords):
            if "space" in text and not ("free" in text or "left" in text or "disk" in text or "storage" in text):
                 pass
            else:
                 return self.tools.get("system_info")
        
        return None

    def process(self, user_text):
        tool = self.find_tool_for_intent(user_text)
        if tool:
            self.logger.info(f"Triggering tool: {tool.name}")
            
            if tool.name == "weather":
                city = "Kolkata"
                if self.llm:
                    city = self.llm.extract_city(user_text)
                    if not city or city == "None":
                        city = "Kolkata"
                
                return tool.execute(city)
            
            elif tool.name == "news":
                query = None
                if self.llm:
                    extracted = self.llm.extract_news_topic(user_text)
                    if extracted and extracted != "None":
                        query = extracted
                
                return tool.execute(query=query)
            
            elif tool.name == "system_info":
                return tool.execute(query_type=user_text)


            elif tool.name == "screen_reader":
                return tool.execute(prompt=user_text)
        
        return None
