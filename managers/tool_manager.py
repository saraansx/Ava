import logging
from config import Config
from tools.weather import WeatherTool
from tools.news import NewsTool
from tools.system_info import SystemInfoTool
from Functions.screen.screen_reader import ScreenReaderTool


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
        self.register_tool(ScreenReaderTool())

        
    def register_tool(self, tool):
        self.tools[tool.name] = tool
        self.logger.info(f"Tool registered: {tool.name}")

    def find_tool_for_intent(self, text):
        text = text.lower()
        if "weather" in text or "vedar" in text or "vader" in text:
            return self.tools.get("weather")
        if "news" in text:
            return self.tools.get("news")
        
        screen_keywords = [
            "on my screen", "read my screen", "see my screen", "look at my screen", "describe my screen",
            "kya dikh raha hai", "screen par kya hai", "screen dekho", "reading screen",
            "what do you see", "what is visible", "check my screen", "analyze screen",
            "screen mein kya", "mere screen"
        ]
        
        if any(keyword in text for keyword in screen_keywords):
             self.logger.info("Manual Keyword detected screen reading intent.")
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
            result = None
            
            if tool.name == "weather":
                city = "Kolkata"
                if self.llm:
                    city = self.llm.extract_city(user_text)
                    if not city or city == "None":
                        city = "Kolkata"
                
                result = tool.execute(city)
            
            elif tool.name == "news":
                query = None
                if self.llm:
                    extracted = self.llm.extract_news_topic(user_text)
                    if extracted and extracted != "None":
                        query = extracted
                
                result = tool.execute(query=query)
            
            elif tool.name == "system_info":
                result = tool.execute(query_type=user_text)

            elif tool.name == "screen_reader":
                result = tool.execute(prompt=user_text)
            
            self.logger.info(f"Tool Output: {str(result)[:100]}...") 
            return result
            
        
        return None
