import time
import os
import threading
from typing import Callable, Optional
from pynput import keyboard
from .logger import get_logger
from .player import TinyPlayer

class BackgroundKeyboardListener:
    """System-wide keyboard listener that runs in the background."""

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the keyboard listener.

        Args:
            log_file: Optional path to save keyboard logs. If None, logging is disabled.
        """
        self.running = False
        self.listener = None
        self.thread = None
        self.callbacks = []

        # Setup logging if requested
        if log_file:
            self.logger = get_logger('background_keyboard', log_file)
        else:
            self.logger = None

    def add_callback(self, callback) -> None:
        """
        Add a callback function to be called on key events.

        Args:
            callback: Function that takes (key, event_type) parameters.
                     event_type is either 'press' or 'release'
        """
        self.callbacks.append(callback)

    def _on_press(self, key) -> None:
        """Internal callback for key press events."""
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)

        if self.logger:
            self.logger.info(f"Key pressed: {key_char}")
        # print(f"Key pressed: {key_char}")

        for callback in self.callbacks:
            callback(key, 'press')

    def _on_release(self, key) -> None:
        """Internal callback for key release events."""
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)

        if self.logger:
            self.logger.info(f"Key released: {key_char}")

        for callback in self.callbacks:
            callback(key, 'release')

    def start(self) -> None:
        """Start the keyboard listener in the background."""
        if self.running:
            return

        self.running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            # on_release=self._on_release
        )
        with self.listener as listener:
            listener.join()

        self.thread = threading.Thread(target=self.listener.start, daemon=True)
        self.thread.start()

        if self.logger:
            self.logger.info("Keyboard listener started")

    def stop(self) -> None:
        """Stop the keyboard listener."""
        if not self.running:
            return

        self.running = False
        if self.listener:
            self.listener.stop()

        if self.logger:
            self.logger.info("Keyboard listener stopped")

    def is_running(self) -> bool:
        """Check if the listener is currently running."""
        return self.running

# Example usage
if __name__ == "__main__":
    player = TinyPlayer(cache_size=100)
    sound_path = os.path.join(os.path.dirname(__file__), '..', 'sounds', 'mixkit-hard-typewriter-click-1119.wav')

    if player.load_sound(sound_path):
        print("Sound loaded successfully")

        # Create and start the listener
        listener = BackgroundKeyboardListener(log_file="keyboard_log.txt")
        listener.add_callback(player.play_for_key(sound_path))
        listener.start()
    else:
        print("Failed to load sound")
        exit()


    try:
        print("Keyboard listener is running. Press Ctrl+C to stop.")
        # Keep the main thread alive
        while True:
            time.sleep(2)  # Give time to switch to the target window
    except KeyboardInterrupt:
        listener.stop()
        print("Keyboard listener stopped.")
