## =======================================================
## Program: Site Checker (gui) - WCMS
## Author: Le Zhang (20916452)
## Email: l652zhan@uwaterloo.ca
## Update Time: Nov. 14 2023
## Company: University of Waterloo
## Faculty: MECHANICAL AND MECHATRONICS ENGINEERING
## =======================================================

import io
import threading
from tkinter import scrolledtext
from tkinter import messagebox
from operations import *

class TextRedirector(io.TextIOBase):
    """
    TextRedirector is a custom IO stream class for redirecting the
    output (e.g., from print statements) to a specified Tkinter text widget.

    Inherits from: io.TextIOBase

    Instance Attributes:
        - widget (tk.Text): The Tkinter text widget to redirect output to.

    TextRedirector: tk.Text -> TextRedirector

    Example:
        -> import sys
        -> text_widget = tk.Text(some_frame)
        -> sys.stdout = TextRedirector(text_widget)
        -> print("This text will be appended to the text widget.")
    """

    def __init__(self, widget):
        """
        __init__(widget) initializes a new TextRedirector instance, redirecting output to
        the given Tkinter text widget.

        __init__: tk.Text -> None

        Params:
            widget (tk.Text): A Tkinter Text widget where the text/output is to be redirected.

        Effects:
            - Initializes the TextRedirector object with a specified Tkinter Text widget.
        """
        self.widget = widget

    def write(self, string):
        """
        write(string) inserts the provided string at the end of the Text widget and
            auto-scrolls to the end to display the latest output.

        write: str -> None

        Params:
            string (str): The string of text to be written/appended to the text widget.

        Effects:
            - Appends the string to the text widget.
            - Scrolls the text widget to display the newly added text.
        """
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)


class SiteCheckerApp:
    def __init__(self, root):
        self.root = root
        self.initialize_gui()

    def execute(self):
        self.progress_var.set(0)
        self.update_progress_label()
        self.output_text.delete('1.0', tk.END)
        base_link = self.site_entry.get()

        def thread_target():
            valid_site, site, output_name = site_process(base_link)
            start = self.start_var.get()
            end = self.end_var.get()
            mode = self.mode_var.get()
            speed = self.speed_var.get()
            mode_dict = {'Default': 0, 'Accessibility Only': 1, 'Broken Links Only': 2, 'Acc and Broken Links': 3}
            try:
                if valid_site and start and end:
                    start, end = int(start), int(end)
                    range_check(self, site, start, end + 1, mode_dict[mode], output_name, speed)
                elif valid_site and (start or end):
                    node = int(start) if start else int(end)
                    node_check(self, site, node, mode_dict[mode], output_name)
            except ValueError:
                self.output_text.insert(tk.END, "Please enter valid numbers for start and end nodes.\n")
            except KeyError:
                self.output_text.insert(tk.END, "Please select a valid mode.\n")

        execute_thread = threading.Thread(target=thread_target)
        execute_thread.daemon = True
        execute_thread.start()

    def reset(self):
        if messagebox.askokcancel("Reset", "Do you want to reset? All data will be reset."):
            self.site_var.set('')
            self.start_var.set('')
            self.end_var.set('')
            self.speed_var.set(0)
            self.progress_var.set(0)
            self.output_text.delete('1.0', tk.END)
            self.update_progress_label()
            remove_progress()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? All ongoing operations will be terminated."):
            self.root.destroy()

    def res_quit(self):
        self.reset()
        self.on_closing()

    def initialize_gui(self):
        self.root.title("Site Checker")
        icon_path = load_icon('logo.ico')
        self.root.wm_iconbitmap(icon_path)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.style = ttk.Style()
        self.style.configure("Warning.TLabel", foreground="red")

        self.site_var = tk.StringVar()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.speed_var = tk.IntVar()

        self.create_widgets()

        load_progress(self)

        self.layout_widgets()

    def fast_gui(self):
        self.speed_button.config(text='Use default mode')
        self.speed_var.set(1)
        self.root.title("Site Checker - Fast mode")
        self.speed_label.config(text="WARNING! FAST MODE!", style="Warning.TLabel")

    def slow_gui(self):
        self.speed_button.config(text='Use fast mode')
        self.speed_var.set(0)
        self.root.title("Site Checker")
        self.speed_label.config(text="")

    def speed(self):
        if self.speed_button.config('text')[-1] == 'Use fast mode':
            if messagebox.askokcancel("Mode", "Do you want to use high speed mode? The process cannot be paused."):
                self.fast_gui()
        else:
            if messagebox.askokcancel("Mode", "Do you want to use default? The check will be more safe."):
                self.slow_gui()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10")

        self.site_label = ttk.Label(self.frame, text="Site url:")
        self.site_entry = ttk.Entry(self.frame, width=70, textvariable=self.site_var)

        self.start_label = ttk.Label(self.frame, text="Start Node:")
        self.start_entry = ttk.Entry(self.frame, width=15, textvariable=self.start_var)

        self.end_label = ttk.Label(self.frame, text="End Node:")
        self.end_entry = ttk.Entry(self.frame, width=15, textvariable=self.end_var)

        self.mode_label = ttk.Label(self.frame, text="Mode:")
        self.mode_var = tk.StringVar(value='Default')
        self.mode_menu = ttk.OptionMenu(self.frame, self.mode_var, 'Default',
                                        'Default', 'Accessibility Only',
                                        'Broken Links Only', 'Acc and Broken Links')
        self.mode_menu.config(width=26)

        self.execute_button = ttk.Button(self.frame, width=15, text="Execute", command=self.execute)
        self.res_button = ttk.Button(self.frame, width=15, text="Reset", command=self.reset)
        self.speed_button = ttk.Button(self.frame, width=15, text="Use fast mode", command=self.speed)
        self.speed_label = ttk.Label(self.frame)

        self.quit_button = ttk.Button(self.frame, width=15, text="Quit", command=self.on_closing)
        self.quit_res_button = ttk.Button(self.frame, width=15, text="Quit With Reset", command=self.res_quit)

        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=20)

        self.progress_var = tk.IntVar()
        self.progressbar = ttk.Progressbar(self.frame, variable=self.progress_var)

        self.progress_label = ttk.Label(self.frame, text=f"{self.progress_var.get()}/{self.end_var.get()}")

        self.config_button = ttk.Button(self.frame, width=15, text="Configuration", command=lambda: edit_config(self))

    def layout_widgets(self):
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.site_label.grid(column=0, row=0, sticky=tk.W)
        self.site_entry.grid(columnspan=5, column=1, row=0, sticky=tk.W)

        self.start_label.grid(column=0, row=1, sticky=tk.W)
        self.start_entry.grid(columnspan=2, column=1, row=1, sticky=tk.W)

        self.end_label.grid(column=0, row=2, sticky=tk.W)
        self.end_entry.grid(columnspan=2, column=1, row=2, sticky=tk.W)

        self.mode_label.grid(column=0, row=3, sticky=tk.W)
        self.mode_menu.grid(column=1, row=3, columnspan=3, sticky=tk.W)

        self.execute_button.grid(columnspan=1, column=3, row=1, pady=10)
        self.res_button.grid(columnspan=1, column=4, row=1, pady=10, sticky=tk.W)
        self.speed_button.grid(columnspan=2, column=5, row=1, pady=20, sticky=tk.W)
        self.speed_label.grid(columnspan=2, column=4, row=3, pady=20, sticky=tk.W)

        self.quit_button.grid(columnspan=1, column=3, row=2, pady=10)
        self.quit_res_button.grid(columnspan=1, column=4, row=2, pady=10, sticky=tk.W)

        self.output_text.grid(column=0, row=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.progressbar.grid(columnspan=5, column=0, row=4, pady=10, sticky=(tk.W, tk.E))

        self.progress_label.grid(column=5, row=4, pady=10)

        self.config_button.grid(columnspan=1, column=5, row=2, pady=10, sticky=tk.W)

        sys.stdout = TextRedirector(self.output_text)

    def update_progress_label(self, n=0):
        if n == 1:
            self.progress_label.config(text=f"DONE")
        else:
            self.progress_label.config(text=f"{self.progress_var.get()}/{self.end_var.get()}")
