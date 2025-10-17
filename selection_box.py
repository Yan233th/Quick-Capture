import tkinter as tk

CORNER_SIZE = 15
CORNER_COLOR = "red"
DRAG_THRESHOLD = 5
MIN_WINDOW_SIZE = CORNER_SIZE * 2 + 20
TRANSPARENT_COLOR = "grey15"


class SelectionBox:
    def __init__(self, root, trigger_callback):
        self.root = root
        self.trigger_callback = trigger_callback

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.99)
        self.root.config(bg=TRANSPARENT_COLOR)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        self.canvas = tk.Canvas(root, bg=TRANSPARENT_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._create_corners()
        self._bind_events()

        self._press_x = 0
        self._press_y = 0
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging = False
        self._resize_corner = None

    def _create_corners(self):
        s = CORNER_SIZE
        self.corners = {
            "top_left": self.canvas.create_rectangle(0, 0, s, s, fill=CORNER_COLOR),
            "top_right": self.canvas.create_rectangle(0, 0, s, s, fill=CORNER_COLOR),
            "bottom_left": self.canvas.create_rectangle(0, 0, s, s, fill=CORNER_COLOR),
            "bottom_right": self.canvas.create_rectangle(0, 0, s, s, fill=CORNER_COLOR),
        }
        self.root.bind("<Configure>", self._update_corners_position)

    def _update_corners_position(self, event=None):
        s = CORNER_SIZE
        w, h = self.root.winfo_width(), self.root.winfo_height()
        self.canvas.coords(self.corners["top_left"], 0, 0, s, s)
        self.canvas.coords(self.corners["top_right"], w - s, 0, w, s)
        self.canvas.coords(self.corners["bottom_left"], 0, h - s, s, h)
        self.canvas.coords(self.corners["bottom_right"], w - s, h - s, w, h)

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    def _get_corner_at(self, x, y):
        s = CORNER_SIZE
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if x < s and y < s:
            return "top_left"
        if x > w - s and y < s:
            return "top_right"
        if x < s and y > h - s:
            return "bottom_left"
        if x > w - s and y > h - s:
            return "bottom_right"
        return "move"

    def _on_press(self, event):
        self._resize_corner = self._get_corner_at(event.x, event.y)
        self._press_x = self._drag_start_x = event.x_root
        self._press_y = self._drag_start_y = event.y_root
        self._is_dragging = False

    def _on_motion(self, event):
        if not self._is_dragging:
            dx = abs(event.x_root - self._press_x)
            dy = abs(event.y_root - self._press_y)
            if dx > DRAG_THRESHOLD or dy > DRAG_THRESHOLD:
                self._is_dragging = True

        if not self._is_dragging:
            return

        delta_x = event.x_root - self._drag_start_x
        delta_y = event.y_root - self._drag_start_y
        x, y, w, h = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width(), self.root.winfo_height()

        if self._resize_corner == "move":
            self.root.geometry(f"{w}x{h}+{x + delta_x}+{y + delta_y}")
        else:
            if "right" in self._resize_corner:
                w += delta_x
            if "bottom" in self._resize_corner:
                h += delta_y
            if "left" in self._resize_corner:
                x += delta_x
                w -= delta_x
            if "top" in self._resize_corner:
                y += delta_y
                h -= delta_y
            w = max(w, MIN_WINDOW_SIZE)
            h = max(h, MIN_WINDOW_SIZE)
            self.root.geometry(f"{w}x{h}+{x}+{y}")

        self._drag_start_x, self._drag_start_y = event.x_root, event.y_root

    def _on_release(self, event):
        if not self._is_dragging and self._resize_corner != "move":
            self.trigger_callback()
        self._resize_corner = None

    def get_bbox(self):
        return (self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width(), self.root.winfo_height())

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.deiconify()
