
import os
import warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

warnings.filterwarnings("ignore", category=UserWarning, module='pygame')
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

try:
    from core.app import JarvisApp
    from GUI.interface import AvaGUI

    def main():
        app = JarvisApp()
        
        # Initialize GUI and start
        gui = AvaGUI(app)
        gui.start()

    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Failed to load GUI: {e}")
    # Fallback to console if GUI fails? 
    # But user specifically asked for GUI.
    from core.app import JarvisApp
    app = JarvisApp()
    app.run()