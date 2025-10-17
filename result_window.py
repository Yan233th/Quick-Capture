import tkinter as tk
from tkinter import scrolledtext
import queue


class ResultWindow(tk.Toplevel):
    def __init__(self, q: queue.Queue):
        super().__init__()
        self.q = q

        self.title("AI Analysis Result")
        self.attributes("-topmost", True)

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=60, height=15, relief="flat", borderwidth=0)
        self.text_area.pack(padx=10, pady=10, expand=True, fill="both")
        self.text_area.configure(state="disabled")

        self._center_window()
        self.after(100, self._update_text)

    def _update_text(self):
        try:
            while True:
                chunk = self.q.get_nowait()
                if chunk is None:
                    return
                self.text_area.configure(state="normal")
                self.text_area.insert(tk.END, chunk)
                self.text_area.configure(state="disabled")
                self.text_area.see(tk.END)
        except queue.Empty:
            self.after(100, self._update_text)

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


def display_stream_result(q: queue.Queue):
    ResultWindow(q)
