import os
import time
import pygame
import logging
import subprocess

class EdgeTTS:
    def __init__(self, temp_folder="temp"):
        self.logger = logging.getLogger("EdgeTTS")
        self.temp_folder = temp_folder
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        pygame.mixer.init()
        self.current_file = None
        self.current_subtitle = None

    def speak(self, text: str, voice: str = 'en-IE-EmilyNeural') -> None:
        if not text:
            return

        try:
            timestamp = int(time.time())
            audio_file = os.path.join(self.temp_folder, f"tts_{timestamp}.mp3")
            subtitle_file = os.path.join(self.temp_folder, f"tts_{timestamp}.srt")

            safe_text = text
            
            args = [
                "edge-tts",
                "--voice", voice,
                "--text", safe_text,
                "--write-media", audio_file,
                "--write-subtitles", subtitle_file
            ]
            
            self.logger.info(f"Generating TTS: {text[:50]}...")
            subprocess.run(args, check=True)

            if os.path.exists(audio_file):
                self.logger.info("Playing audio...")
                self.stop()
                
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                self.current_file = audio_file
                self.current_subtitle = subtitle_file
            else:
                self.logger.error("Audio file was not generated.")

        except Exception as e:
            self.logger.error(f"TTS Error: {e}")

    def stop(self):
        """Stops playback and cleans up temporary files."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                self.logger.info("Audio stopped.")
            
            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass

            if self.current_file and os.path.exists(self.current_file):
                try:
                    os.remove(self.current_file)
                    self.logger.info(f"Deleted temp file: {self.current_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete audio file: {e}")
                self.current_file = None
            
            if self.current_subtitle and os.path.exists(self.current_subtitle):
                try:
                    os.remove(self.current_subtitle)
                except Exception as e:
                    self.logger.warning(f"Failed to delete subtitle file: {e}")
                self.current_subtitle = None

        except Exception as e:
            self.logger.error(f"Error while stopping/cleaning up: {e}")

    def wait(self):
        """Waits for the current audio playback to finish."""
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

if __name__ == "__main__":
    tts = EdgeTTS(temp_folder="../../temp")
    tts.speak("Hello, this is a test of the Edge TTS system.")
    time.sleep(2)
    tts.stop()
