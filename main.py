
import os
import warnings
from core.app import JarvisApp

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

warnings.filterwarnings("ignore", category=UserWarning, module='pygame')
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

def main():
    app = JarvisApp()
    app.run()

if __name__ == "__main__":
    main()
