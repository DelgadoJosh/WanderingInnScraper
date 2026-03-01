# This code creates a simple GUI to run the Wandering Inn Scraper using tkinter
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import queue
import threading 
import wanderingInnScraperBackEnd as backend

class WanderingInnScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wandering Inn Scraper")
        self.root.geometry("1000x600")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam') # Using clam as it's cleaner than default on many systems
        
        # Variables
        self.print_option = tk.StringVar(value='One Large File')
        self.format_choice = tk.StringVar(value='txt')
        self.beginning_link = tk.StringVar(value="https://wanderinginn.com/2017/03/03/rw1-00/")
        self.ending_link = tk.StringVar(value="")
        self.folder_location = tk.StringVar(value="")
        
        self.gui_queue = queue.Queue()
        
        self.setup_menu()
        self.setup_layout()
        
        # Start queue polling
        self.root.after(100, self.poll_queue)

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # Help Menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.root.config(menu=menubar)

    def setup_layout(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Side - Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Output type
        ttk.Label(options_frame, text="Please select what type of output file:").pack(anchor=tk.W, pady=(0, 5))
        options = ['One Large File', 'Individual Chapters', 'Both']
        option_menu = ttk.OptionMenu(options_frame, self.print_option, options[0], *options)
        option_menu.pack(fill=tk.X, pady=(0, 10))
        
        # Format choice
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(format_frame, text='Plain text', variable=self.format_choice, value='txt').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text='HTML', variable=self.format_choice, value='html').pack(side=tk.LEFT)
        
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Links
        ttk.Label(options_frame, text="First page to scrape from").pack(anchor=tk.W)
        ttk.Entry(options_frame, textvariable=self.beginning_link, width=50).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="Final page to scrape from (inclusive)").pack(anchor=tk.W)
        ttk.Entry(options_frame, textvariable=self.ending_link, width=50).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Folder Choice
        ttk.Label(options_frame, text="Please choose a destination folder").pack(anchor=tk.W)
        folder_frame = ttk.Frame(options_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Entry(folder_frame, textvariable=self.folder_location).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT)
        
        # Submit Button
        ttk.Button(options_frame, text="Submit", command=self.on_submit).pack(pady=10)
        
        # Right Side - Console Log
        console_frame = ttk.LabelFrame(main_frame, text="Console Log", padding="10")
        console_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.console = scrolledtext.ScrolledText(console_frame, state='disabled', wrap=tk.WORD, font=('TkFixedFont', 10))
        self.console.pack(fill=tk.BOTH, expand=True)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_location.set(folder)

    def show_about(self):
        messagebox.showinfo("About", "Wandering Inn Scraper\nby Josh Delgado")

    def get_debug_text(self):
        text_type = "Plain text" if self.format_choice.get() == "txt" else "HTML"
        text = f"Type of output file: {self.print_option.get()}, {text_type}\n"
        text += f"Beginning Link: {self.beginning_link.get()}\n"
        text += f"Ending Link: {self.ending_link.get()}\n"
        text += f"Folder Address: {self.folder_location.get()}\n"
        return text

    def on_submit(self):
        start_url = self.beginning_link.get().strip()
        end_url = self.ending_link.get().strip()
        print_option = self.print_option.get()
        directory = self.folder_location.get().strip()
        format_choice = self.format_choice.get()

        if not end_url:
            messagebox.showwarning("Incomplete Information", "Make sure to add an ending url!")
            return

        if not directory:
            messagebox.showwarning("Incomplete Information", "Make sure to choose a folder!")
            return

        confirm_msg = f"Here's the info you input:\n\n{self.get_debug_text()}\nAre you sure you want to submit?"
        if messagebox.askyesno("Confirm", confirm_msg):
            self.log("Beginning Program\n")
            threading.Thread(target=backend.scrapePageInit,
                            args=(start_url, end_url, print_option, directory, format_choice, self.gui_queue), 
                            daemon=True).start()

    def log(self, text):
        self.console.config(state='normal')
        self.console.insert(tk.END, text + "\n")
        self.console.config(state='disabled')
        self.console.see(tk.END)

    def poll_queue(self):
        try:
            while True:
                message = self.gui_queue.get_nowait()
                if message:
                    self.log(message)
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.poll_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = WanderingInnScraperGUI(root)
    root.mainloop()

