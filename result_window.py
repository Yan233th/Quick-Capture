import tkinter as tk
from tkinter import scrolledtext
import queue


def display_stream_result(q: queue.Queue):
    result_window = tk.Toplevel()
    result_window.title("AI Analysis Result")
    result_window.attributes("-topmost", True)

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=60, height=15, relief="flat", borderwidth=0)
    text_area.pack(padx=10, pady=10, expand=True, fill="both")
    text_area.configure(state="disabled")

    def update_text():
        try:
            while True:
                chunk = q.get_nowait()
                if chunk is None:
                    return
                text_area.configure(state="normal")
                text_area.insert(tk.END, chunk)
                text_area.configure(state="disabled")
                text_area.see(tk.END)
        except queue.Empty:
            result_window.after(100, update_text)

    result_window.after(100, update_text)

    result_window.update_idletasks()
    x = (result_window.winfo_screenwidth() - result_window.winfo_width()) // 2
    y = (result_window.winfo_screenheight() - result_window.winfo_height()) // 2
    result_window.geometry(f"+{x}+{y}")
