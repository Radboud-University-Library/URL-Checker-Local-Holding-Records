"""
main.py: A GUI application for checking the HTTP response of URLs from a CSV file.

The application allows users to:
- Select an input CSV file containing URLs.
- Select an output location for the processed CSV file.
- Process the input file by checking the URLs' HTTP response codes and descriptions,
  and then save the results to the output file.
"""

import tkinter as tk
from tkinter import ttk, Text
from link_functions import LinkProcessor
import threading


class LinkCheckerApp:
    def __init__(self, root):
        self.main_window = root
        self.main_window.title("URL Checker Local Holding Records")
        self.processor = LinkProcessor()

        # Initialize instance attributes
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.status_text = None
        self.progress_bar = None

        # Add the BooleanVar for the allow_redirects checkbox
        self.allow_redirects = tk.BooleanVar(value=True)

        # Set up the GUI components
        self.init_gui()

    def select_input(self):
        path = LinkProcessor.select_input_file()
        self.input_file_path.set(path)

    def select_output(self):
        path = LinkProcessor.select_output_location()
        self.output_file_path.set(path)

    def start_processing(self):
        threading.Thread(target=self.process_links_threaded, args=(self.allow_redirects.get(),)).start()

    def process_links_threaded(self, allow_redirects):
        self.processor.process_links(self.input_file_path.get(), self.output_file_path.get(), self.status_text,
                                     self.progress_bar, self.main_window, allow_redirects)
        self.status_text.insert('end', "Processing completed!\n")

    def init_gui(self):
        """Initialize the GUI components."""
        tk.Button(self.main_window, text="Select Input CSV", command=self.select_input).pack(pady=20)
        tk.Button(self.main_window, text="Select Output Location", command=self.select_output).pack(pady=20)
        tk.Button(self.main_window, text="Start Processing", command=self.start_processing).pack(pady=20)
        tk.Checkbutton(self.main_window, text="Allow Redirects", variable=self.allow_redirects).pack(pady=10)

        self.status_text = Text(self.main_window, height=5, width=50)
        self.status_text.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self.main_window, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = LinkCheckerApp(root)
    root.mainloop()
