# This code creates a simple GUI to run the Wandering Inn Scraper using tkinter
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import queue
import threading 
import wanderingInnScraperBackEnd as backend

VERSION = "1.7.0"

# Colors matching the screenshot (Dark Brown theme)
BG_COLOR = "#2b2b28"
FG_COLOR = "#ffff00"  # Yellow/Gold
INPUT_BG = "#4d4d4d"
BTN_BG = "#3b5a6b"   # Teal/Blueish
BTN_HOVER = "#4a6d82"
BTN_FG = "#ffffff"

class CustomButton(tk.Label):
  """A custom button using tk.Label to ensure colors are respected on macOS."""
  def __init__(self, parent, text, command, **kwargs):
    super().__init__(parent, text=text, bg=BTN_BG, fg=BTN_FG, padx=10, pady=2, 
                     relief=tk.RAISED, borderwidth=1, cursor="hand2", **kwargs)
    self.command = command
    self.bind("<Button-1>", self._on_click)
    self.bind("<Enter>", self._on_enter)
    self.bind("<Leave>", self._on_leave)

  def _on_click(self, event):
    self.command()

  def _on_enter(self, event):
    self.config(bg=BTN_HOVER)

  def _on_leave(self, event):
    self.config(bg=BTN_BG)

class WanderingInnScraperGUI:
  def __init__(self, root):
    self.root = root
    self.root.title(f"Wandering Inn Scraper v{VERSION}")
    self.root.geometry("1000x500")
    self.root.configure(bg=BG_COLOR)
    
    # Variables
    self.print_option = tk.StringVar(value='One Large File')
    self.format_choice = tk.StringVar(value='txt')
    self.beginning_link = tk.StringVar(value="https://wanderinginn.com/2017/03/03/rw1-00/")
    self.ending_link = tk.StringVar(value="")
    self.folder_location = tk.StringVar(value="")
    
    self.gui_queue = queue.Queue()
    self.stop_event = threading.Event()
    
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
    # Main container
    main_frame = tk.Frame(self.root, bg=BG_COLOR, padx=10, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Left Side - Options
    options_container = tk.LabelFrame(main_frame, text="Options", bg=BG_COLOR, fg=FG_COLOR, padx=10, pady=10)
    options_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
    
    # Internal width for consistency
    opt_width = 45

    # Output type
    tk.Label(options_container, text="Please select what type of output file:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor=tk.W)
    
    options = ['One Large File', 'Individual Chapters', 'Both']
    self.option_menu = tk.OptionMenu(options_container, self.print_option, *options)
    self.option_menu.config(bg=INPUT_BG, fg=FG_COLOR, activebackground=INPUT_BG, activeforeground=FG_COLOR, 
                            width=opt_width, highlightthickness=0, borderwidth=1)
    self.option_menu["menu"].config(bg=INPUT_BG, fg=FG_COLOR)
    self.option_menu.pack(pady=(5, 10))
    
    # Format choice
    format_frame = tk.Frame(options_container, bg=BG_COLOR)
    format_frame.pack(fill=tk.X, pady=(0, 10))
    tk.Radiobutton(format_frame, text='Plain text', variable=self.format_choice, value='txt', 
                   bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, 
                   activeforeground=FG_COLOR, highlightthickness=0).pack(side=tk.LEFT)
    tk.Radiobutton(format_frame, text='HTML', variable=self.format_choice, value='html', 
                   bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, 
                   activeforeground=FG_COLOR, highlightthickness=0).pack(side=tk.LEFT, padx=(20, 0))
    tk.Radiobutton(format_frame, text='EPUB (One Large File)', variable=self.format_choice, value='epub', 
                   bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, 
                   activeforeground=FG_COLOR, highlightthickness=0).pack(side=tk.LEFT, padx=(20, 0))
    
    tk.Frame(options_container, height=1, bd=0, bg=FG_COLOR).pack(fill=tk.X, pady=10)
    
    # Links
    tk.Label(options_container, text="First page to scrape from", bg=BG_COLOR, fg=FG_COLOR).pack(anchor=tk.W)
    tk.Entry(options_container, textvariable=self.beginning_link, width=opt_width+5, 
             bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, borderwidth=1, highlightthickness=0).pack(pady=(0, 10))
    
    tk.Label(options_container, text="Final page to scrape from (inclusive)", bg=BG_COLOR, fg=FG_COLOR).pack(anchor=tk.W)
    tk.Entry(options_container, textvariable=self.ending_link, width=opt_width+5, 
             bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, borderwidth=1, highlightthickness=0).pack(pady=(0, 10))
    
    tk.Frame(options_container, height=1, bd=0, bg=FG_COLOR).pack(fill=tk.X, pady=10)
    
    # Folder Choice
    tk.Label(options_container, text="Please choose a destination folder", bg=BG_COLOR, fg=FG_COLOR).pack(anchor=tk.W)
    folder_inner = tk.Frame(options_container, bg=BG_COLOR)
    folder_inner.pack(fill=tk.X, pady=(5, 20))
    tk.Label(folder_inner, text="Your Folder", bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    tk.Entry(folder_inner, textvariable=self.folder_location, bg=INPUT_BG, fg=FG_COLOR, 
             insertbackground=FG_COLOR, width=30, borderwidth=1, highlightthickness=0).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    CustomButton(folder_inner, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
    
    # Submit & Stop Buttons
    btn_frame = tk.Frame(options_container, bg=BG_COLOR)
    btn_frame.pack(anchor=tk.W)
    CustomButton(btn_frame, text="Submit", command=self.on_submit).pack(side=tk.LEFT, padx=(0, 10))
    CustomButton(btn_frame, text="Stop Program", command=self.on_stop).pack(side=tk.LEFT)
    
    # Right Side - Console Log
    console_container = tk.LabelFrame(main_frame, text="Console Log", bg=BG_COLOR, fg=FG_COLOR, padx=10, pady=10)
    console_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    self.console = scrolledtext.ScrolledText(console_container, state='disabled', wrap=tk.WORD, 
                                            font=('TkFixedFont', 10), bg=BG_COLOR, fg=FG_COLOR, 
                                            insertbackground=FG_COLOR, highlightthickness=0, borderwidth=0)
    self.console.pack(fill=tk.BOTH, expand=True)

  def browse_folder(self):
    folder = filedialog.askdirectory()
    if folder:
      self.folder_location.set(folder)

  def show_about(self):
    messagebox.showinfo("About", f"Wandering Inn Scraper v{VERSION}\nby Josh Delgado")

  def get_debug_text(self):
    text_type = "Plain text" if self.format_choice.get() == "txt" else ("HTML" if self.format_choice.get() == "html" else "EPUB")
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
      
    if format_choice == "epub" and print_option != "One Large File":
      messagebox.showwarning("Invalid Selection", "EPUB format must be 'One Large File'. The EPUB will automatically isolate chapters internally.")
      return

    confirm_msg = f"Here's the info you input:\n\n{self.get_debug_text()}\nAre you sure you want to submit?"
    if messagebox.askyesno("Confirm", confirm_msg):
      self.log("Beginning Program\n")
      self.stop_event.clear()
      threading.Thread(target=backend.scrapePageInit,
              args=(start_url, end_url, print_option, directory, format_choice, self.gui_queue, self.stop_event), 
              daemon=True).start()

  def on_stop(self):
    if not self.stop_event.is_set():
      self.stop_event.set()
      self.log("\nStop signal sent. Finishing current chapter and stopping...")

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

