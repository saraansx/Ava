
"""
Author: Devs Do Code (Sree)
Project: Realtime Speech to Text Listener
Description: A Python script that uses Selenium to interact with a website and listen to user input & print them in real time.
"""

from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os

class SpeechToTextListener:
    """A class for performing speech-to-text using a web-based service."""

    def __init__(
            self, 
            website_path: str = None, 
            language: str = "hi-IN",
            wait_time: int = 10):
        
        """Initializes the STT class with the given website path and language."""
        if website_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            website_path = os.path.join(current_dir, "src", "index.html")
            
        self.website_path = website_path
        self.language = language
        self.chrome_options = Options()
        self.chrome_options.add_argument("--use-fake-ui-for-media-stream")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, wait_time)
        self.is_page_loaded = False

    def stream(self, content: str):
        """Prints the given content to the console in real-time."""
        print(f"\r\033[96mUser Speaking:\033[0m {content}", end='', flush=True)

    def get_text(self) -> str:
        """Retrieves the transcribed text from the website."""
        return self.driver.find_element(By.ID, "convert_text").text

    def select_language(self):
        """Selects the language from the dropdown using JavaScript."""
        self.driver.execute_script(
            f"""
            var select = document.getElementById('language_select');
            select.value = '{self.language}';
            var event = new Event('change');
            select.dispatchEvent(event);
            """
        )

    def verify_language_selection(self):
        """Verifies if the language is correctly selected."""
        language_select = self.driver.find_element(By.ID, "language_select")
        selected_language = language_select.find_element(By.CSS_SELECTOR, "option:checked").get_attribute("value")
        return selected_language == self.language

    def start_listening(self):
        """Initializes the listener directly. Broken out from main() for better control."""
        if self.website_path.startswith("http"):
            self.driver.get(self.website_path)
        else:
            self.driver.get("file:///" + self.website_path.replace("\\", "/"))

        self.wait.until(EC.presence_of_element_located((By.ID, "language_select")))
        
        self.select_language()

        if not self.verify_language_selection():
            return False

        self.driver.find_element(By.ID, "click_to_record").click()

        self.wait.until(
            EC.presence_of_element_located((By.ID, "is_recording"))
        )
        return True

    def listen(self, prints: bool = False) -> Optional[str]:
        """Starts the listening process."""
        # print("\033[94m\rListening...", end='', flush=True)
        
        if not hasattr(self, 'initialized') or not self.initialized:
             if self.start_listening():
                 self.initialized = True
        
        is_recording = self.driver.find_element(By.ID, "is_recording")
        final_text = ""
        
        while is_recording.text.startswith("Recording: True"):
            text = self.get_text()
            if text and text != final_text:
                self.stream(text)
                final_text = text
            is_recording = self.driver.find_element(By.ID, "is_recording")

        return self.get_text()
        
    def listen_once(self):
        """One-shot listen until silence or similar logic if implemented, or just return current buffer."""
        if not hasattr(self, 'is_setup') or not self.is_setup:
             self.driver.get("file:///" + self.website_path.replace("\\", "/"))
             self.wait.until(EC.presence_of_element_located((By.ID, "language_select")))
             self.select_language()
             self.driver.find_element(By.ID, "click_to_record").click()
             self.wait.until(EC.presence_of_element_located((By.ID, "is_recording")))
             self.is_setup = True

        # print("\033[94m\rListening...", end='', flush=True)
        
        is_recording_elem = self.driver.find_element(By.ID, "is_recording")
        
        last_text = ""
        while is_recording_elem.text.startswith("Recording: True"):
             text = self.get_text()
             if text and text != last_text:
                 self.stream(text)
                 last_text = text
             is_recording_elem = self.driver.find_element(By.ID, "is_recording")
        
        return self.get_text()

    def run_cycle(self, callback=None):
         """Replicates the user's `main` method logic exactly."""
         if not self.is_page_loaded:
             if self.website_path.startswith("http"):
                 self.driver.get(self.website_path)
             else:
                 self.driver.get("file:///" + self.website_path.replace("\\", "/"))
             self.is_page_loaded = True

         self.wait.until(EC.presence_of_element_located((By.ID, "language_select")))
         self.select_language()
         if not self.verify_language_selection():
             return None
             
         self.driver.execute_script("document.getElementById('convert_text').innerHTML = '';")
         self.driver.find_element(By.ID, "click_to_record").click()
         
         is_recording = self.wait.until(EC.presence_of_element_located((By.ID, "is_recording")))
         
         streamed = False
         while is_recording.text.startswith("Recording: True"):
            text = self.get_text()
            if text:
                if callback:
                    callback(text)
                else:
                    self.stream(text)
                streamed = True
            is_recording = self.driver.find_element(By.ID, "is_recording")
         
         if streamed:
            pass
            # print()
         
         return self.get_text()

if __name__ == "__main__":
    listener = SpeechToTextListener(language="hi-IN")
    speech = listener.run_cycle()
    print("FINAL EXTRACTION: ", speech)
