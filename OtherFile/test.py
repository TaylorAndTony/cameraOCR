from pynput.keyboard import Key, Listener


def process_keyboard(e):
    try:
        btn = e.char
    except AttributeError:
        btn = None
    print(btn)


with Listener(on_press=process_keyboard) as listener:
        listener.join()
