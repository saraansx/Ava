from managers.vlm_manager import VLMManager

class ScreenReaderTool:
    def __init__(self):
        self.name = "screen_reader"
        self.manager = VLMManager(model="minicpm-v")

    def execute(self, prompt="Describe strictly what you see on the screen."):
        return self.manager.analyze_screen(prompt)
