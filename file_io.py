## =======================================================
## Program: Site Checker (file_io) - WCMS
## Author: Le Zhang (20916452)
## Email: l652zhan@uwaterloo.ca
## Update Time: Nov. 15 2023
## Company: University of Waterloo
## Faculty: MECHANICAL AND MECHATRONICS ENGINEERING
## =======================================================

from bitarray import bitarray
import datetime
import json
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk


now = datetime.datetime.now()
time_str = now.strftime('%Y%m%d')
user_desktop = Path.home() / 'Desktop'


class JsonEditor(tk.Toplevel):
    """
    A Toplevel widget to create a JSON file editor interface.

    This GUI component allows users to view, add, and remove URLs
    from a JSON file through a simple graphical interface.

    Attributes:
    -----------
    json_file : Path
        Path object pointing to the JSON file that contains URLs.
    urls : list
        List containing the URLs retrieved from the JSON file.

    Methods:
    --------
    populate_listbox()
        Populate the Listbox widget with URLs.
    add_url()
        Add a new URL to the Listbox and JSON file.
    remove_url()
        Remove the selected URL from the Listbox and JSON file.
    save_json()
        Save the current URLs to the JSON file.
    """

    def __init__(self, master=None, json_file=None):
        """
        Initialize JsonEditor.

        Parameters:
        -----------
        master : Tk or Toplevel widget, optional
            The parent widget. Default is None.
        json_file : str, optional
            Path to the JSON file relative to the script or executable.
            Default is None.
        """
        base_path = Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys._MEIPASS)
        json_file = base_path / json_file
        super().__init__(master)
        self.json_file = json_file
        with open(self.json_file, "r") as file:
            self.urls = json.load(file)
        self.title("JSON Editor")
        self.geometry("400x300")
        self.wm_iconbitmap(base_path / 'logo.ico')
        self.url_listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.url_listbox.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        self.entry = ttk.Entry(self)
        self.entry.pack(fill=tk.X, padx=5, pady=5)
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)
        self.add_button = ttk.Button(frame, text="Add", command=self.add_url)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.remove_button = ttk.Button(frame, text="Remove", command=self.remove_url)
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)
        self.populate_listbox()

    def populate_listbox(self):
        """
        Populate the Listbox widget with URLs.

        Clears the Listbox and inserts URLs retrieved from the json file.
        """
        self.url_listbox.delete(0, tk.END)
        for url in self.urls:
            self.url_listbox.insert(tk.END, url)

    def add_url(self):
        """
        Add a new URL to the Listbox and JSON file.

        Retrieves the URL from the Entry widget, verifies that it is
        non-empty and unique, then adds it to the 'urls' list and updates
        the Listbox and JSON file.
        """
        new_url = self.entry.get()
        if new_url and new_url not in self.urls:
            self.urls.append(new_url)
            self.urls.sort()
            self.populate_listbox()
            self.save_json()
            self.entry.delete(0, tk.END)
            self.status_label.config(text="Added successfully!")
        else:
            self.entry.delete(0, tk.END)
            self.status_label.config(text="URL exists!")

    def remove_url(self):
        """
        Remove the selected URL from the Listbox and JSON file.

        Deletes the selected URL from the 'urls' list and updates the
        Listbox and JSON file.
        """
        selected_index = self.url_listbox.curselection()
        if selected_index:
            self.urls.pop(selected_index[0])
            self.populate_listbox()
            self.save_json()
            self.status_label.config(text="Removed successfully!")
        else:
            self.status_label.config(text="No URL selected!")

    def save_json(self):
        """
        Save the current URLs to the JSON file.

        Dumps the 'urls' list to the specified JSON file.
        """
        with open(self.json_file, "w") as file:
            json.dump(self.urls, file)


def edit_config(app_instance):
    """
    Instantiate and open the JsonEditor widget.

    Specifically targeted to edit "social_media_domains.json" file.
    """
    JsonEditor(master=app_instance.root, json_file="social_media_domains.json")


def load_progress(app_instance):
    """
    load_progress() returns the last node number from the 'progress.txt' file if it exists,
        otherwise None.

    load_progress: () -> Union[int, None]

    Effects:
        - Reads from 'progress.txt' file in the current working directory if it exists.

    Returns:
        - An integer representing the last node number read from the file if the file exists.
        - None if the file does not exist.

    Note:
        - The function internally sets global variables (site_var, start_var, end_var)
          which should be available in the scope.

    Example:
        node = load_progress()
        if node is not None:
            print(f"Resuming from node {node}.")
    """
    progress_file = Path('progress.txt')
    if progress_file.exists():
        with progress_file.open('r') as file:
            speed, site, start, end, last_node = file.read().strip().split(',')
            app_instance.site_var.set(site)
            app_instance.start_var.set(start)
            app_instance.end_var.set(end)
            if speed:
                app_instance.fast_gui()
            else:
                app_instance.slow_gui()
            return int(last_node)
    return None


def get_last_node(app_instance):
    """
    get_last_node() returns the last node number obtained from the load_progress function.

    get_last_node: () -> Union[int, None]

    Returns:
        - An integer representing the last node number if obtained successfully.
        - None if unable to obtain the last node number.

    Example:
        node = get_last_node()
        if node is not None:
            print(f"Last node is {node}.")
    """
    last_node = load_progress(app_instance)
    return last_node


def set_last_node(app_instance, node_number):
    """
    set_last_node(node_number) writes the current site, start, end, and node_number to
        the 'progress.txt' file.

    set_last_node: int -> None

    Requires:
        - node_number is an integer that represents the node number to be written to the file.

    Effects:
        - Writes to 'progress.txt' file in the current working directory.

    Note:
        - The function internally uses global variables (site_var, start_var, end_var)
          which should be available in the scope.

    Example:
        set_last_node(42)
        # Writes current site, start, end, and "42" to 'progress.txt'.
    """
    with open('progress.txt', 'w') as file:
        file.write(f'{app_instance.speed_var.get()},{app_instance.site_var.get()},{app_instance.start_var.get()},{app_instance.end_var.get()},{node_number}')


def remove_progress():
    """
    Deletes the 'progress.txt' file from the current working directory, if it exists.

    Usage example:
    remove_progress()
    """
    progress_txt = Path('progress.txt')
    progress_bin = Path('progress.bin')
    if progress_txt.exists():
        progress_txt.unlink()

    if progress_bin.exists():
        progress_bin.unlink()


def write_to_file(output_name, base_url, acc_problem, broken_urls, acc_bool, broken_bool):
    """
    write_to_file(output_name, base_url, acc_problem, broken_urls, acc_bool, broken_bool)
    writes the accessibility issues and broken URLs into a text file on the user's desktop.

    write_to_file: Str Str (listof str) (listof str) Bool Bool -> None

    Requires:
        - output_name is a string specifying the prefix of the output file name.
        - base_url is a string representing the base URL that was checked.
        - acc_problem is a list of strings, each representing a URL causing accessibility issues.
        - broken_urls is a list of strings, each representing a broken URL.
        - acc_bool is a boolean that indicates whether to write accessibility issues to the file.
        - broken_bool is a boolean that indicates whether to write broken URLs to the file.

        Note: The function internally uses `user_desktop` and `time_str` which should be available
              in the scope.

    Effects:
        - Writes the base URL, accessibility issues (if acc_bool is True), and broken URLs
          (if broken_bool is True) into a text file located on the user's desktop. The text file
          is named using the provided output_name as a prefix and the current time string
          as a suffix, in the format "{output_name}result_{time_str}.txt".

    Example:
        write_to_file("check_results", "http://example.com", acc_problems, broken_urls, True, True)

        This writes the base URL, accessibility issues, and broken URLs into a text file named
        "check_resultsresult_{time_str}.txt" on the user's desktop.
    """
    output_file_path = user_desktop / f'{output_name}result_{time_str}.txt'
    with open(output_file_path, 'a', encoding='utf-8') as file:
        file.write(f"base_url: {base_url}\n")
        if acc_bool:
            file.write("    acc_problem:\n")
            for index, item in enumerate(acc_problem, start=1):
                file.write(f"        {index}. {item}\n")
        if broken_bool:
            file.write("    broken_urls:\n")
            for index, item in enumerate(broken_urls, start=1):
                file.write(f"        {index}. {item}\n")
        file.write("\n")


def load_config(file_path):
    """
    load_config(file_path) returns a dictionary obtained by reading a JSON file
      located at the file_path.

    load_config: Str -> Dict

    Requires: file_path is a string representing a valid relative or absolute file path.
              The file at file_path should be readable and contain valid JSON data.

    Example:
        config_data = load_config('config.json')

        Where 'config.json' is a JSON file located in the same directory as the script.

    """
    base_path = Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys._MEIPASS)
    file_path = base_path / file_path
    with open(file_path, 'r') as file:
        return json.load(file)


def load_icon(file_path):
    """
    load_icon(file_path) returns the path of an icon file located at file_path.

    load_icon: Str -> Path

    Requires: file_path is a string that represents a valid relative or absolute file path.
              The file at file_path should exist.

    Example:
        icon_path = load_icon('icon.png')

        Where 'icon.png' is an image file located in the same directory as the script.

    """
    base_path = Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys._MEIPASS)
    file_path = base_path / file_path
    return file_path


def parse_and_sort(output_name):
    """
    parse_and_sort(output_name) reads the content from a text file named as per the output_name, 
    sorts the content blocks based on a specific key, and then writes the sorted content back to the same file.

    parse_and_sort: Str -> None

    Requires: output_name is a string that represents the base name for the output text file.
              The text file named '{output_name}result_{time_str}.txt' must exist on the user's desktop.

    Effect: Reads from a text file located on the user's desktop, sorts the content, and overwrites the file with sorted content.

    Example:
        parse_and_sort('analysis_')

        This will read 'analysis_result_{time_str}.txt', sort its content, and overwrite the file with sorted data.
    """
    output_file_path = user_desktop / f'{output_name}result_{time_str}.txt'
    if output_file_path.exists():
        with open(output_file_path, 'r') as file:
            content = file.read()

        blocks = content.strip().split('\n\n')
        sorted_blocks = sorted(blocks, key=lambda block: int(block.split('/node/')[1].split('/')[0]))
        sorted_content = '\n\n'.join(sorted_blocks)

        with open(output_file_path, 'w') as file:
            file.write(sorted_content)
    else:
        print("DONE")


def save_bin(bit_array):
    """
    save_bin(bit_array) writes the provided bit array to a binary file named 'progress.bin'.

    save_bin: BitArray -> None

    Requires: bit_array is an instance of the BitArray type or similar, supporting the tofile method.

    Effect: Writes the content of bit_array to a binary file 'progress.bin' in the current working directory.

    Example:
        save_bin(my_bit_array)

        Where 'my_bit_array' is a bit array that needs to be saved to 'progress.bin'.
    """
    with open('progress.bin', 'wb') as file:
        bit_array.tofile(file)


def load_bin(size):
    """
    load_bin(size) reads a bit array from the 'progress.bin' file if it exists, 
    or creates a new bit array of a specified size with all bits set to 0 if the file doesn't exist.

    load_bin: Int -> BitArray

    Requires: size is a positive integer that specifies the size of the bit array to be created if 'progress.bin' doesn't exist.

    Effect: Reads from or creates a file named 'progress.bin' in the current working directory.

    Returns: A bit array that is either loaded from 'progress.bin' or newly created with all bits set to 0.

    Example:
        bit_array = load_bin(1024)

        This will load a bit array from 'progress.bin' or create a new one with 1024 bits, all set to 0.
    """
    progress_file = Path('progress.bin')
    if progress_file.exists():
        with progress_file.open('rb') as file:
            bit_array = bitarray()
            bit_array.fromfile(file)
            return bit_array
    else:
        bit_array = bitarray(size)
        bit_array.setall(0)
        return bit_array
