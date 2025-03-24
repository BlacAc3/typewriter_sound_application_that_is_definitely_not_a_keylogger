
# PyTypeSound:  A Minimalist Python Typewriter Sound Emulator

PyTypeSound is a simple, lightweight Python library designed to add typewriter-like sound effects to your typing. It aims for minimal resource usage and a straightforward API.  It utilizes `pynput` for cross-platform keyboard listening, `pyaudio` for audio playback, and implements a basic LRU cache for sound files to minimize memory consumption.

## Features

*   **Background Keyboard Listening:**  Listens for keypresses system-wide without interfering with normal keyboard input.
*   **Sound Playback:** Plays WAV sound files on keypresses.
*   **Minimal Memory Usage:** Uses a small LRU (Least Recently Used) cache to store sound data, preventing excessive memory consumption.  Only the audio data of the cached WAV files is loaded into memory, minimizing the footprint.
*   **Asynchronous Playback:**  Sounds play in separate threads to avoid blocking the main application.
*   **Logging:** Optionally logs keypresses to a file.
*   **Simple API:** Easy to integrate into other projects.
*   **Cross-Platform:** Leverages `pynput` for compatibility across Windows, macOS, and Linux.

## Installation

1.  **Install Required Libraries:**

    ```bash
    pip install -r requirements.txt
    ```

    For PyAudio installation, you might need system-specific dependencies. Consult the PyAudio documentation if you encounter issues.  For example, on Debian/Ubuntu, you might need:

    ```bash
    sudo apt-get install portaudio19-dev python3-pyaudio
    ```

    On macOS (using Homebrew):

    ```bash
    brew install portaudio
    ```

2.  **Clone the Repository (Optional):**

    If you want to run the example or contribute to the project, clone the repository:

    ```bash
    git clone https://github.com/<your-username>/pytypesound.git  # Replace with your fork if contributing
    cd pytypesound
    ```

## Usage

The main components are `BackgroundKeyboardListener` and `TinyPlayer`. Here's a breakdown of the example provided in `pytypesound/listener/main.py`, with explanations:

```python
import time
import os
from pytypesound.listener.main import BackgroundKeyboardListener
from pytypesound.listener.player import TinyPlayer

# --- TinyPlayer Setup ---

# 1. Instantiate TinyPlayer:
player = TinyPlayer(cache_size=100)  # Cache up to 100 sounds. Adjust as needed.

# 2. Specify the sound file:
sound_path = os.path.join(
    os.path.dirname(__file__), "..", "sounds", "mixkit-hard-typewriter-click-1119.wav"
)  # Relative path to the sound file.

# 3. Load the sound (attempts to load into cache):
if player.load_sound(sound_path):
    print("Sound loaded successfully")

    # --- BackgroundKeyboardListener Setup ---

    # 4. Instantiate the listener, optionally enabling logging:
    listener = BackgroundKeyboardListener(log_file="keyboard_log.txt")  # Log to 'keyboard_log.txt'.  Omit for no logging.

    # 5. Add a callback: Connect the keypress event to sound playback.
    listener.add_callback(player.play_for_key(sound_path))

    # 6. Start the listener (runs in a background thread):
    listener.start()

    # --- Main Loop (Keep the program running) ---

    try:
        print("Keyboard listener is running. Press Ctrl+C to stop.")
        while True:  # Keep the main thread alive;  background listener is on a daemon thread.
            time.sleep(2)
    except KeyboardInterrupt:
        listener.stop()  # Stop the listener when Ctrl+C is pressed.
        print("Keyboard listener stopped.")
else:
    print("Failed to load sound")
```

**Key improvements and explanations in this example:**

*   **`TinyPlayer`:**
    *   `cache_size`:  Controls the maximum number of sounds kept in memory. The `TinyPlayer` uses a simple LRU (Least Recently Used) cache. When the cache is full, the least recently used sound is removed to make room for new ones.
    *   `load_sound(filepath)`:  Attempts to load the WAV file at `filepath`.  If the file is already in the cache, it just updates its position in the LRU list.  If not, it reads the audio data and adds it to the cache.  Returns `True` on success, `False` on failure.
    *   `play(filepath)`: Plays the sound *synchronously* (blocking).  This is done within a separate thread by `play_async`.
    *   `play_async(filepath)`:  Plays the sound *asynchronously* (non-blocking) by launching a new thread that calls `play`.  This is crucial to prevent the keyboard listener from freezing.
    *   `play_for_key(filepath)`: This is a *very* important method.  It returns a *callback function*.  This callback function, when called by the keyboard listener, will trigger the asynchronous playback of the sound. This design is efficient and avoids creating new threads for every single keypress.
    *    `cleanup()`: Releases the resources and terminates the `pyaudio` object.

*   **`BackgroundKeyboardListener`:**
    *   `log_file`:  Optional.  Specifies a file to log keypress events.
    *   `add_callback(callback)`:  Adds a function to be called on each keypress.  The callback receives the `key` object and the `event_type` ('press' or 'release') as arguments.
    *   `start()`:  Starts the keyboard listener in a *daemon thread*.  This means the listener thread will automatically exit when the main program exits.
    *   `stop()`:  Stops the listener.
    *   `is_running()`: Returns `True` if the listener is active.
    *   The listener only handles press event, and the release event has been removed.

*   **Main Loop:** The `while True: time.sleep(2)` loop is essential. Since the keyboard listener runs in a daemon thread, the main thread needs to stay alive.  If the main thread exits, the daemon thread will be terminated as well.

* **Error Handling:** Basic error handling is included (file not found, PyAudio errors), making the code more robust.

##  Structure
* **`listener/`**: Contains the core logic.
    *   `callbacks.py`:  (Example)  Provides a simple callback function to print keypresses.  Not directly used in the main example, but demonstrates how to define custom callbacks.
    *   `logger.py`: A utility for setting up basic logging.
    *   `main.py`:  The `BackgroundKeyboardListener` class, which handles keyboard listening and callback management.  Also includes the example usage.
    *   `player.py`: The `TinyPlayer` class for efficient sound playback and caching.
* **`__init__.py`**: Is an empty file that indicates to python that the listener folder is a module.

## Running the Example

1.  **Ensure you have a WAV sound file.**  You can either create your own or find one online.  The example code looks for a file named `mixkit-hard-typewriter-click-1119.wav` in a `sounds` directory one level above the `listener` directory. Create the `sounds` folder and place your wav file inside.

2.  **Run the script:**

    ```bash
    python -m  listener.main.py
    ```

3.  **Switch to another window.** The keyboard listener is system-wide.  Start typing, and you should hear the sound.

4.  **Stop the script:** Press Ctrl+C in the terminal where you ran the script.

## Important Considerations and Improvements

*   **LRU Cache:** The `TinyPlayer` uses an LRU cache to manage sound data.  This limits memory usage by only keeping the most recently used sounds loaded.
*   **Asynchronous Playback:** The `play_async` method ensures that sound playback doesn't block the keyboard listener.
*   **Thread Safety:** The `TinyPlayer` uses a `threading.Lock` to protect the cache from race conditions when multiple threads (from rapid keypresses) try to access it simultaneously.
*   **Resource Management:** The `cleanup` method in `TinyPlayer` releases PyAudio resources.
* **Error Handling:** Includes basic error handling to prevent crashes.
*   **Daemon Thread:** The listener runs in a daemon thread, so it exits automatically when the main program terminates.
* **Cross-Platform:** Uses pynput, which supports Windows, macOS, and Linux

This significantly improved version provides a much more robust, efficient, and user-friendly experience, adhering to best practices for threading, resource management, and memory usage. It's ready to be used as a basic typewriter sound emulator or integrated into larger projects.
