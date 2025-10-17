import tkinter as tk
import threading
import queue
import pyautogui
from dotenv import load_dotenv

from selection_box import SelectionBox
from ai_handler import send_to_ai_stream
from result_window import display_stream_result

load_dotenv()

from ai_handler import API_KEY  # noqa: E402


def capture_and_process():
    if capture_and_process.running:
        return
    capture_and_process.running = True

    print("--- CORNER CLICKED: capture_and_process function called! ---")
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
            capture_and_process.running = False


capture_and_process.running = False

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300+100+100")

    selection_box = SelectionBox(root, trigger_callback=capture_and_process)

    if not API_KEY:
        print("Warning: GOOGLE_API_KEY not found in .env file. Running in offline/mock mode.")

    print("Quick-Capture is running. Click one of the four corners to capture.")
    print("Drag corners to resize, drag the center to move.")

    root.mainloop()
