def print_key(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)
    print(f"Key pressed: {key_char}")


# def play_sound(sound_file):
