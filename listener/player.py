import os
import wave
import time
import threading
import numpy as np
import pyaudio

class TinyPlayer:
    """Ultra-lightweight sound player with minimal memory footprint."""

    def __init__(self, cache_size=1):
        self.pa = pyaudio.PyAudio()
        self._cache = {}  # filename -> audio data
        self._cache_keys = []  # For LRU tracking
        self._cache_size = cache_size
        self._lock = threading.Lock()

    def load_sound(self, filepath):
        """Load a sound file, with minimal caching."""
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        # Return cached data if available
        if filepath in self._cache:
            # Move to end of LRU list
            self._cache_keys.remove(filepath)
            self._cache_keys.append(filepath)
            return True

        try:
            with wave.open(filepath, 'rb') as wf:
                # Get basic audio info
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                framerate = wf.getframerate()

                # Read all frames at once
                audio_data = wf.readframes(wf.getnframes())

            # Store in cache with LRU management
            with self._lock:
                # Remove oldest item if cache is full
                if len(self._cache_keys) >= self._cache_size and self._cache_keys:
                    oldest = self._cache_keys.pop(0)
                    del self._cache[oldest]

                # Add new item
                self._cache[filepath] = (audio_data, channels, sample_width, framerate)
                self._cache_keys.append(filepath)

            return True
        except Exception as e:
            print(f"Error loading sound: {e}")
            return False

    def play(self, filepath):
        """
        Play sound directly using blocking mode - simplest possible implementation.
        Called from a thread to avoid blocking the main program.
        """
        if not filepath in self._cache and not self.load_sound(filepath):
            return

        data, channels, width, rate = self._cache[filepath]

        # This is the simplest approach - create a fresh stream for each playback
        try:
            stream = self.pa.open(
                format=self.pa.get_format_from_width(width),
                channels=channels,
                rate=rate,
                output=True
            )

            # Write data directly - no callbacks involved
            stream.write(data)

            # Clean up immediately
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def play_async(self, filepath):
        """Play sound in a separate thread to avoid blocking."""
        threading.Thread(target=self.play, args=(filepath,), daemon=True).start()

    def play_for_key(self, filepath):
        """Return a callback function for keyboard events."""
        def callback(key, event_type):
            if event_type == 'release' or event_type == 'press':
                self.play_async(filepath)
        return callback

    def cleanup(self):
        """Release all resources."""
        self._cache.clear()
        self._cache_keys.clear()
        try:
            self.pa.terminate()
        except:
            pass
# Example usage
if __name__ == "__main__":
    player = TinyPlayer(cache_size=2)  # Keep only 2 sounds in memory at once

    # Load and play a sound
    if player.load_sound("beep.wav"):
        player.play("beep.wav")
        time.sleep(1)  # Let the sound play

    player.cleanup()
