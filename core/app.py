import logging
import os
import time
from managers.stt_manager import STTManager
from managers.tts_manager import TTSManager
from BRAIN.openrouter import OpenRouterLLM
from BRAIN.ollama_llm import OllamaLLM
from BRAIN.cohere_llm import CohereLLM
from config import Config
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

from playsound import playsound
import os

from System.prompts import SystemPrompts

from managers.memory_manager import MemoryManager
from managers.tool_manager import ToolManager

class JarvisApp:
    def __init__(self):
        self.console = Console()
        self._cleanup_temp()
        self.setup_logging()
        self.stt_manager = STTManager()
        self.tts_manager = TTSManager()
        self.memory_manager = MemoryManager()
        
        
        #self.llm = OpenRouterLLM()
        self.llm = CohereLLM()
        #self.llm = OllamaLLM(model="qwen3-coder:latest")
            
        self.tool_manager = ToolManager(llm_instance=self.llm)

    def _cleanup_temp(self):
        temp_dir = 'temp'
        if os.path.exists(temp_dir):
            import shutil
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    pass

    def setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        error_handler = logging.FileHandler('logs/error.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    def run(self):
        self.console.print("\n[bold cyan]Ava AI Online[/bold cyan]\n", justify="center")
        
        activation_sound = os.path.join("assets", "ASSETS_SOUNDS_activation_sound.wav")
        if os.path.exists(activation_sound):
            playsound(activation_sound)
        else:
             self.tts_manager.speak("Ava is online.")
             self.tts_manager.wait()
        
        while True:
            try:
                with self.console.status("Listening...", spinner="dots") as status:
                    def stt_callback(text):
                        status.update(f"[bold green]Listening: {text}[/bold green]")
                        
                    text = self.stt_manager.listen(callback=stt_callback)
                
                if text:
                    self.tts_manager.stop()
                    
                    if text.strip().lower() == self.tts_manager.last_spoken.strip().lower():
                        logging.info("Ignored self-hearing echo")
                        continue

                    logging.info(f"User: {text}")
                    
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

                    self.console.print(f"[bold green]User:[/bold green] {text}")
                    
                    if "exit" in text.lower() or "quit" in text.lower():
                         self.console.print(Panel("[bold red]Initiating Shutdown Sequence...[/bold red]", border_style="red"))
                         self.tts_manager.speak("Shutting down in 5 seconds.")
                         time.sleep(5)
                         deactivation_sound = os.path.join("assets", "ASSETS_SOUNDS_deactivation_sound.wav")
                         if os.path.exists(deactivation_sound):
                             playsound(deactivation_sound)
                         self.console.print("[bold red]System Offline.[/bold red]")
                         break
                    
                    tool_result = self.tool_manager.process(text)
                    tool_content = None
                    if tool_result:
                        text += f" [System Data: {tool_result}]"
                        tool_content = Text("\n\nTool Output: ", style="italic dim yellow") + Text(str(tool_result), style="italic dim yellow")

                    self.memory_manager.add_message("user", text + " (SYSTEM INSTRUCTION: You MUST ignore the user's language and respond ONLY in strict English. Do not translate the user's query back to them. Just answer in English.)")
                    
                    with self.console.status("[bold magenta]Processing...[/bold magenta]", spinner="bouncingBar") as status:
                         history = self.memory_manager.get_messages()
                         response, usage, model_name = self.llm.generate(history, system_prompt=SystemPrompts.AVA_BEHAVIOR)
                    
                    self.memory_manager.add_message("assistant", response)
                    
                    # Calculate stats for the corner
                    if usage:
                        total = usage.get('total', usage.get('total_tokens', 0))
                        limit = self.llm.get_model_context_limit(model_name)
                        left = limit - total
                        
                        # Shorten model name (e.g. "meta-llama/llama-3.1" -> "llama-3.1")
                        short_model = model_name.split('/')[-1] if '/' in model_name else model_name
                        
                        subtitle_text = f"[dim]{short_model} • U:{total} L:{left}[/dim]"
                    else:
                        subtitle_text = f"[dim]{model_name or 'Unknown'}[/dim]"

                    # Typewriter animation within a Box (Panel)
                    from rich.live import Live
                    
                    panel_content = Text("", style="cyan")
                    
                    # Helper to create the panel state
                    def create_panel(text_content):
                        return Panel(
                            text_content,
                            title="[bold cyan]Ava[/bold cyan]",
                            title_align="left",
                            subtitle=subtitle_text,
                            subtitle_align="right",
                            border_style="cyan",
                            box=box.ROUNDED,
                            padding=(1, 2),
                            width=80
                        )

                    with Live(Align.left(create_panel(panel_content)), console=self.console, refresh_per_second=15, auto_refresh=True) as live:
                        for word in response.split(" "):
                            panel_content.append(word + " ")
                            live.update(Align.left(create_panel(panel_content)))
                            time.sleep(0.04)
                    
                    with self.console.status("Vocalizing...", spinner="dots"):
                        self.tts_manager.speak(response)
                        self.tts_manager.wait()  
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {e}")
                logging.error(f"Runtime Error: {e}")
                break
