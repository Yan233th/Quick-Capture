import tkinter as tk
import threading
import queue
import pyautogui
import signal

from selection_box import SelectionBox
from ai_handler import API_KEY, send_to_ai_stream
from result_window import display_stream_result


def capture_and_process():
    if capture_and_process.running:
        return
    capture_and_process.running = True

    print("--- CORNER CLICKED: capture_and_process function called! ---")
    global selection_box
    if not selection_box:
        capture_and_process.running = False
        return

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

    def handle_ctrl_c(signum, frame):
        print("\nCtrl+C detected. Shutting down application.")
        root.destroy()

    signal.signal(signal.SIGINT, handle_ctrl_c)

    if not API_KEY:
        print("Warning: GOOGLE_API_KEY not found in .env file. Running in offline/mock mode.")

    print("Quick-Capture is running. Click one of the four corners to capture.")
    print("Drag corners to resize, drag the center to move.")

    root.mainloop()
