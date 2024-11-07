import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import threading
from tkinter import Canvas


class CoordinateMarker:
    def __init__(self):
        self.marker_window = None

    def show_marker(self, x, y):
        if self.marker_window:
            self.marker_window.destroy()

        self.marker_window = tk.Toplevel()
        self.marker_window.overrideredirect(True)
        self.marker_window.attributes('-topmost', True)
        self.marker_window.attributes('-transparentcolor', 'black')
        self.marker_window.geometry(f'20x20+{x - 10}+{y - 10}')

        canvas = Canvas(self.marker_window, width=20, height=20, bg='black', highlightthickness=0)
        canvas.pack()

        canvas.create_oval(2, 2, 18, 18, outline='#FF4444', width=2)
        canvas.create_oval(8, 8, 12, 12, fill='#FF4444', outline='#FF4444')
        canvas.create_line(10, 0, 10, 7, fill='#FF4444', width=1)
        canvas.create_line(10, 13, 10, 20, fill='#FF4444', width=1)
        canvas.create_line(0, 10, 7, 10, fill='#FF4444', width=1)
        canvas.create_line(13, 10, 20, 10, fill='#FF4444', width=1)

        self.marker_window.bind('<Escape>', lambda e: self.remove_marker())
        self.marker_window.focus_force()

    def remove_marker(self):
        if self.marker_window:
            self.marker_window.destroy()
            self.marker_window = None


class CoordinateSelector:
    def __init__(self, parent):
        self.parent = parent
        self.coordinates = None
        self.position_window = None

    def show_position_window(self):
        self.position_window = tk.Toplevel()
        self.position_window.attributes('-topmost', True)
        self.position_window.geometry('200x100')
        self.position_window.title('Coordinates')

        self.x_label = tk.Label(self.position_window, text="X: 0")
        self.x_label.pack(pady=5)
        self.y_label = tk.Label(self.position_window, text="Y: 0")
        self.y_label.pack(pady=5)

        self.update_position()

    def update_position(self):
        if self.position_window:
            x, y = pyautogui.position()
            self.x_label.config(text=f"X: {x}")
            self.y_label.config(text=f"Y: {y}")
            self.position_window.after(50, self.update_position)

    def capture_screen(self):
        self.show_position_window()

        overlay = tk.Toplevel()
        overlay.attributes('-alpha', 0.3)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)

        canvas = tk.Canvas(overlay, highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        canvas.configure(cursor='cross')

        def motion(event):
            canvas.delete("crosshair")
            x, y = event.x, event.y
            canvas.create_line(x, 0, x, overlay.winfo_height(), fill='red', tags="crosshair")
            canvas.create_line(0, y, overlay.winfo_width(), y, fill='red', tags="crosshair")

        def on_click(event):
            self.coordinates = (event.x, event.y)
            overlay.destroy()
            if self.position_window:
                self.position_window.destroy()

        canvas.bind('<Motion>', motion)
        canvas.bind('<Button-1>', on_click)
        overlay.wait_window()

        return self.coordinates


class MacroGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mouse Macro")
        self.root.geometry("400x500")

        self.coordinates_list = []
        self.running = False
        self.marker = CoordinateMarker()

        self.create_widgets()

    def create_widgets(self):
        coord_frame = ttk.LabelFrame(self.root, text="Coordinates List")
        coord_frame.pack(padx=10, pady=5, fill='x')

        self.coord_listbox = tk.Listbox(coord_frame, height=8)
        self.coord_listbox.pack(padx=5, pady=5, fill='x')
        self.coord_listbox.bind('<Double-Button-1>', self.show_coordinate_marker)
        self.root.bind('<Escape>', lambda e: self.marker.remove_marker())

        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=5, fill='x')

        add_btn = ttk.Button(buttons_frame, text="Add Coordinate", command=self.add_coordinate)
        add_btn.pack(pady=5, fill='x', padx=10)

        remove_btn = ttk.Button(buttons_frame, text="Remove Selected", command=self.remove_coordinate)
        remove_btn.pack(pady=5, fill='x', padx=10)

        interval_frame = ttk.LabelFrame(self.root, text="Settings")
        interval_frame.pack(padx=10, pady=5, fill='x')

        ttk.Label(interval_frame, text="Click Interval (seconds):").pack()
        self.interval_var = tk.StringVar(value="1.0")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var)
        interval_entry.pack(pady=5)

        ttk.Label(interval_frame, text="Repeat Count:").pack()
        self.repeat_var = tk.StringVar(value="1")
        repeat_entry = ttk.Entry(interval_frame, textvariable=self.repeat_var)
        repeat_entry.pack(pady=5)

        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_btn = ttk.Button(control_frame, text="Start Selected", command=self.start_macro)
        self.start_btn.pack(side='left', padx=5)

        stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_macro)
        stop_btn.pack(side='left', padx=5)

        exit_btn = ttk.Button(control_frame, text="Exit", command=self.root.destroy)
        exit_btn.pack(side='left', padx=5)

    def show_coordinate_marker(self, event):
        selection = self.coord_listbox.curselection()
        if selection:
            coord = self.coordinates_list[selection[0]]
            self.marker.show_marker(coord[0], coord[1])

    def add_coordinate(self):
        self.root.withdraw()
        time.sleep(0.5)

        selector = CoordinateSelector(self.root)
        coords = selector.capture_screen()

        self.root.deiconify()

        if coords:
            self.coordinates_list.append(coords)
            self.coord_listbox.insert(tk.END, f"X: {coords[0]}, Y: {coords[1]}")

    def remove_coordinate(self):
        selection = self.coord_listbox.curselection()
        if selection:
            idx = selection[0]
            self.coord_listbox.delete(idx)
            self.coordinates_list.pop(idx)

    def start_macro(self):
        selection = self.coord_listbox.curselection()
        if not selection:
            return

        self.marker.remove_marker()  # Added this line to remove marker before starting macro
        self.running = True
        self.start_btn.state(['disabled'])

        def macro_thread():
            try:
                repeat_count = int(self.repeat_var.get())
                interval = float(self.interval_var.get())
                selected_coord = self.coordinates_list[selection[0]]

                for _ in range(repeat_count):
                    if not self.running:
                        break
                    pyautogui.click(x=selected_coord[0], y=selected_coord[1])
                    time.sleep(interval)
            finally:
                self.running = False
                self.root.after(0, lambda: self.start_btn.state(['!disabled']))

        threading.Thread(target=macro_thread, daemon=True).start()

    def stop_macro(self):
        self.running = False

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    macro_gui = MacroGUI()
    macro_gui.run()