import tkinter as tk
import threading
import queue
from pynput import keyboard
import pyautogui
from dotenv import load_dotenv

from selection_box import SelectionBox
from ai_handler import API_KEY, send_to_ai_stream
from result_window import display_stream_result

load_dotenv()

HOTKEY = keyboard.HotKey(keyboard.HotKey.parse("<ctrl>+<shift>+c"))


def capture_and_process():
    global selection_box
    if selection_box:
        selection_box.hide()

        bbox = selection_box.get_bbox()
        print(f"Capturing region: {bbox}...")

        try:
            screenshot = pyautogui.screenshot(region=bbox)
            q = queue.Queue()
            display_stream_result(q)
            threading.Thread(target=send_to_ai_stream, args=(screenshot, q), daemon=True).start()
        except Exception as e:
            error_message = f"Error during capture: {e}"
            print(error_message)
            q = queue.Queue()
            q.put(error_message)
            q.put(None)
            display_stream_result(q)
        finally:
            selection_box.show()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300+100+100")
    selection_box = SelectionBox(root)

    def start_hotkey_listener():
        with keyboard.Listener(on_press=lambda key: HOTKEY.press(key), on_release=lambda key: HOTKEY.release(key)) as listener:
            HOTKEY.activate = capture_and_process
            listener.join()

    listener_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
    listener_thread.start()

    if not API_KEY:
        print("Warning: GOOGLE_API_KEY not found in .env file. Running in offline/mock mode.")

    print("Quick-Capture is running. Press <ctrl>+<shift>+c to capture the selected area.")
    print("Drag corners to resize, drag the center to move.")

    root.mainloop()
