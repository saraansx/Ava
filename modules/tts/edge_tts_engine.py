import os
import time
import logging
import subprocess
from playsound import playsound

class EdgeTTS:
    def __init__(self, temp_folder="temp"):
        self.logger = logging.getLogger("EdgeTTS")
        self.temp_folder = temp_folder
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        self.current_file = None

    def speak(self, text: str, voice: str = 'en-IE-EmilyNeural') -> None:
        if not text:
            return

        try:
            timestamp = int(time.time())
            audio_file = os.path.join(self.temp_folder, f"tts_{timestamp}.mp3")
            
            audio_file = os.path.abspath(audio_file)
            
            self.logger.info(f"Generating TTS: {text[:50]}...")
            
            import edge_tts
            import asyncio
            
            async def _gen():
                comm = edge_tts.Communicate(text, voice)
                await comm.save(audio_file)
            
            asyncio.run(_gen())

            if os.path.exists(audio_file):
                self.logger.info("Playing audio...")
                self.current_file = audio_file
                try:
                    playsound(audio_file)
                except Exception as e:
                    self.logger.error(f"Playback Error: {e}")
                finally:
                    self.stop() 
            else:
                self.logger.error("Audio file was not generated.")

        except Exception as e:
            self.logger.error(f"TTS Error: {e}")
            self.stop()

    def stop(self):
        """Stops playback (if possible) and cleans up temporary files."""
        
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.remove(self.current_file)
                self.logger.info(f"Deleted temp file: {self.current_file}")
            except Exception as e:
                self.logger.warning(f"Failed to delete audio file: {e}")
            self.current_file = None

    def wait(self):
        """
        playsound is synchronized (blocking) by default on Windows,
        so explicit waiting is not strictly necessary unless threaded.
        Keeping method for compatibility.
        """
        pass

if __name__ == "__main__":
    tts = EdgeTTS(temp_folder="../../temp")
    tts.speak("Hello, I have been updated to use the simpler playsound method.")

