#!/usr/bin/env python3
import getpass
import json
import tempfile
import tkinter as tk
import tkinter.ttk as ttk
import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from typing import Optional

import PIL
import requests
from PIL import Image
from PIL import ImageTk
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
from ttkthemes import ThemedTk

from digi_leap.pylib.server import common


@dataclass
class Label:
    class_: str
    left: int
    top: int
    right: int
    bottom: int
    conf: float
    text: str = ""


@dataclass
class Sheet:
    path: Path = None
    scale: float = 1.0
    scaled_image: ImageTk.PhotoImage = None
    raw_image: Image.Image = None
    labels: list[Label] = field(default_factory=list)


class App:
    find_url = "http://localhost:8000/find-labels"
    ocr_url = "http://localhost:8000/ocr-labels"

    def __init__(self):
        self.win = ThemedTk(theme="radiance")

        self.key = common.api_key()
        self.curr_dir = Path(".") / "data" / "junk" / "sheets"

        self.win.title("Digi-Leap Client")
        self.win.geometry("1200x800")
        self.win.protocol("WM_DELETE_WINDOW", self.quit)

        self.sheet: Optional[Sheet] = None

        self.build_menu()

        main_frame = ttk.Frame(self.win)
        main_frame.pack(expand=True, fill="both")

        self.control_frame = ttk.Frame(main_frame)
        self.control_frame.pack(expand=False, fill="x", pady=(16, 16))

        self.sheet_controls()
        self.find_button, self.find_progress = self.find_controls()
        self.ocr_button, self.ocr_progress = self.ocr_controls()

        self.control_frame = ttk.Frame(main_frame)
        self.control_frame.pack(expand=True, fill="both")

        self.canvas = tk.Canvas(self.control_frame, bg="white")
        self.canvas.pack(expand=True, fill="both")

    def sheet_controls(self):
        sheet_frame = ttk.Frame(self.control_frame)
        sheet_frame.pack(side=tk.LEFT, padx=(8, 8))
        button = ttk.Button(
            sheet_frame, text="Get herbarium sheet...", command=self.get_sheet
        )
        button.pack()

    def find_controls(self):
        frame = ttk.Frame(self.control_frame)
        frame.pack(side=tk.LEFT, padx=(8, 8))
        button = ttk.Button(
            frame, text="Find labels", command=self.find_start, state=tk.DISABLED
        )
        button.pack(side=tk.TOP, pady=(8, 8))
        progress = ttk.Progressbar(frame, mode="indeterminate")
        progress.pack(side=tk.TOP, pady=(8, 8))
        return button, progress

    def ocr_controls(self):
        frame = ttk.Frame(self.control_frame)
        frame.pack(side=tk.LEFT, padx=(8, 8))
        button = ttk.Button(
            frame, text="OCR labels", command=self.ocr_start, state=tk.DISABLED
        )
        button.pack(side=tk.TOP, pady=(8, 8))
        progress = ttk.Progressbar(frame, mode="indeterminate")
        progress.pack(side=tk.TOP, pady=(8, 8))
        return button, progress

    def build_menu(self):
        menu = tk.Menu(self.win)
        sub_menu = tk.Menu(menu, tearoff=False)
        sub_menu.add_command(label="Quit", underline=0, command=self.quit)
        menu.add_cascade(label="File", underline=0, menu=sub_menu)
        self.win.config(menu=menu)

    def quit(self):
        self.win.quit()

    def get_sheet(self):
        self.canvas.delete("all")
        file_types = (("All files", "*.*"),)
        path = filedialog.askopenfilename(
            initialdir=self.curr_dir, title="Open herbarium sheet", filetypes=file_types
        )
        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            try:
                raw_image = Image.open(str(path)).convert("RGB")
            except PIL.UnidentifiedImageError:
                messagebox.showerror("Error", f"Could not open image '{path}'")
                return

        w, h = raw_image.size
        scale1 = w / self.canvas.winfo_width()
        scale2 = h / self.canvas.winfo_height()
        scale = max(1.0, scale1, scale2)
        scaled_image = raw_image.resize((int(w / scale), int(h / scale)))

        scaled_image = ImageTk.PhotoImage(scaled_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=scaled_image)
        self.canvas.update()

        self.find_button["state"] = tk.NORMAL
        self.sheet = Sheet(
            path=path, scale=scale, scaled_image=scaled_image, raw_image=raw_image
        )

    def find_start(self):
        self.find_progress.start()
        status, response = self.find_request()
        if status == "Error":
            messagebox.showerror("Error", response)
        else:
            self.draw_labels(response)
        self.find_progress.stop()

    def draw_labels(self, response):
        response = json.loads(response)
        for labels in response.values():
            for lb in labels:
                self.sheet.labels.append(
                    Label(
                        left=lb["left"],
                        top=lb["top"],
                        right=lb["right"],
                        bottom=lb["bottom"],
                        class_=lb["class"],
                        conf=lb["conf"],
                    )
                )
                x1 = int(lb["left"] / self.sheet.scale)
                y1 = int(lb["top"] / self.sheet.scale)
                x2 = int(lb["right"] / self.sheet.scale)
                y2 = int(lb["bottom"] / self.sheet.scale)
                color = "#d95f02" if lb["class"] == "Typewritten" else "#7570b3"
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=4)

    def find_request(self):
        try:
            response = requests.post(
                url=self.find_url,
                files=[
                    ("files", open(self.sheet.path, "rb")),
                ],
                auth=HTTPBasicAuth(getpass.getuser(), self.key),
            )
        except ConnectionError:
            return "Error", "Could not connect to Digi-Leap server"
        if response.status_code < 199 or response.status_code > 299:
            return "Error", "Could not find labels"

        self.ocr_button["state"] = tk.NORMAL
        return "Success", response.json()

    def ocr_start(self):
        self.find_progress.start()
        status, response = self.ocr_request()
        if status == "Error":
            messagebox.showerror("Error", response)
        else:
            self.show_text(response)
        self.find_progress.stop()

    def show_text(self, response):
        response = json.loads(response)
        response = list(response.values())
        print(response[0])
        messagebox.showinfo("debug", response[0])

    def ocr_request(self):
        with tempfile.TemporaryDirectory(prefix="ocr_") as ocr_dir:
            ocr_dir = Path(ocr_dir)
            files = []
            for i, lb in enumerate(self.sheet.labels):
                if lb.class_ != "Typewritten":
                    continue
                image = self.sheet.raw_image.crop(
                    (lb.left, lb.top, lb.right, lb.bottom)
                )
                path = ocr_dir / f"{i}{self.sheet.path.suffix}"
                print("=" * 80)
                print(path)
                image.save(path)
                files.append(("files", open(path, "rb")))
            if not files:
                return "Error", "No labels on this sheet"
            try:
                response = requests.post(
                    url="http://localhost:8000/ocr-labels",
                    files=files,
                    auth=HTTPBasicAuth(getpass.getuser(), self.key),
                )
            except ConnectionError:
                return "Error", "Could not connect to Digi-Leap server"
            if response.status_code < 199 or response.status_code > 299:
                return "Error", "Could not OCR labels"
            return "Success", response.json()


def main():
    app = App()
    app.win.mainloop()


if __name__ == "__main__":
    main()
