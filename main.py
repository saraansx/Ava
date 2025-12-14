
import os
import warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

warnings.filterwarnings("ignore", category=UserWarning, module='pygame')
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

from core.app import JarvisApp

def main():
    app = JarvisApp()
    app.run()

if __name__ == "__main__":
    main()