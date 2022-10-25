#!/usr/bin/env python3
import tkinter as tk
import tkinter.ttk as ttk
import warnings
from pathlib import Path

from PIL import Image
from PIL import ImageTk
from ttkthemes import ThemedTk


class App:
    def __init__(self):
        self.win = ThemedTk(theme="radiance")

        self.curr_dir = Path(".") / "data" / "sheets"

        self.win.title("Digi-Leap Client")
        self.win.geometry("1200x800")

        self.image = None
        self.raw_image = None
        self.scale = 1.0

        self.build_menu()

        frame = ttk.Frame(self.win)
        frame.pack(expand=True, fill="both")

        frame1 = ttk.Frame(frame)
        frame1.pack(expand=False, fill="x", pady=(24, 24))

        button = ttk.Button(
            frame1, text="Get herbarium sheet...", command=self.get_sheet
        )
        button.pack(side=tk.LEFT, padx=(8, 8))

        frame1 = ttk.Frame(frame)
        frame1.pack(expand=True, fill="both")

        self.canvas = tk.Canvas(frame1, bg="white")
        self.canvas.pack(expand=True, fill="both")

    def build_menu(self):
        menu = tk.Menu(self.win)
        sub_menu = tk.Menu(menu, tearoff=False)
        sub_menu.add_command(label="Quit", underline=0, command=self.quit)
        menu.add_cascade(label="File", underline=0, menu=sub_menu)
        self.win.config(menu=menu)

    def quit(self):
        self.win.quit()

    def get_sheet(self):
        path = tk.filedialog.askopenfile(
            initialdir=self.curr_dir, title="Open herbarium sheet"
        )
        if not path:
            return

        path = Path(path.name)
        self.curr_dir = path.parent

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            self.raw_image = Image.open(str(path)).convert("RGB")

        w, h = self.raw_image.size
        scale1 = w / self.canvas.winfo_width()
        scale2 = h / self.canvas.winfo_height()
        self.scale = max(1.0, scale1, scale2)
        image = self.raw_image.resize((int(w / self.scale), int(h / self.scale)))

        self.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.update()


def main():
    app = App()
    app.win.mainloop()


if __name__ == "__main__":
    main()
