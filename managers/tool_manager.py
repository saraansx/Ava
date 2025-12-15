import logging
from tools.weather import WeatherTool
from tools.news import NewsTool
from tools.system_info import SystemInfoTool

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
            from tools.vision_tool import VisionTool
        
            VisionTool.name = "vision" 
            self.register_tool(VisionTool())
        except Exception as e:
            self.logger.error(f"Failed to register VisionTool: {e}")

    def register_tool(self, tool):
        self.tools[tool.name] = tool
        self.logger.info(f"Tool registered: {tool.name}")

    def find_tool_for_intent(self, text):
        text = text.lower()
        if "weather" in text or "vedar" in text or "vader" in text:
            return self.tools.get("weather")
        if "news" in text:
            return self.tools.get("news")
        
        vision_keywords = ["see", "holding", "look at", "describe", "vision", "dikh", "dekho", "najar"]
        if any(keyword in text for keyword in vision_keywords):
            if "you see" in text or "do you see" in text or "am i holding" in text or "look at this" in text:
                 return self.tools.get("vision")
            if "kya dikh" in text or "dikh rha" in text or "isko dekho" in text or "najar aa rha" in text:
                return self.tools.get("vision")
        
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

            elif tool.name == "vision":
                return tool.execute(prompt=user_text)
        
        return None
