# This code creates a very simple GUI to run the Wandering Inn Scraper

import PySimpleGUI as sg
import queue
import threading 
import wanderingInnScraperBackEnd as backend

sg.theme('Dark Brown')


# --- Helper Functions ---
def getDebug(values):
  text = ""
  text = text + "Type of output file: " + values['print_option'] + "\n"
  text = text + "Beginning Link: " + values['beginning_link'] + "\n"
  text = text + "Ending Link: " + values['ending_link'] + "\n"
  text = text + "Folder Address: " + values['folder_location'] + "\n"
  return text

def getAboutText():
  text = ""
  text = text + "Wandering Inn Scraper\n"
  text = text + "by Josh Delgdao\n"
  return text

# Debug Setting
debug = False


# --- Layout ---
# Defines the Menu Header
menu_def = [['File', ['Exit']],
            ['Help', 'About...'],]

print_options = ('One Large File', 'Individual Chapters', 'Both')

default_beginning_link = "https://wanderinginn.com/2016/07/27/1-00/"
default_ending_link = ""

default_folder = "Please pick a folder!"

# Options
left_side_width = 50
left_side_layout = [
  # Menu
  [sg.Menu(menu_def, tearoff=True)],

  # Output Option
  [sg.Text("Please select what type of output file:", size=(left_side_width, 1))],
  [sg.InputOptionMenu(print_options, key='print_option', size=((int)(left_side_width*0.8), 1))],
  [sg.Text('_'*(int)(left_side_width))],

  # Web Addresses
  [sg.Text("First page to scrape from")],
  [sg.InputText(default_beginning_link, key='beginning_link', size=(left_side_width, 1))],
  [sg.Text("Final page to scrape from (inclusive)")],
  [sg.InputText(default_ending_link, key='ending_link', size=(left_side_width, 1))],
  [sg.Text('_'*(int)(left_side_width))],

  # Folder Chooser
  [sg.Text("Please choose a destination folder")],
  [sg.Text('Your Folder', size=(9, 1), auto_size_text=False, justification='left'),
    sg.InputText(default_folder, size=(left_side_width-20, 1), key='folder_location'), sg.FolderBrowse()],

  # Submit & Cancel Buttons
  [sg.Submit(tooltip='Click to begin scraping'), sg.Button('Stop Program')],
]


# Console + Fun facts
console_width = 80
console_lines = 20
right_side_layout = [
  [sg.Output(size=(console_width, console_lines))],

]


layout = [
  [sg.Frame(layout=left_side_layout, title='Options', relief=sg.RELIEF_SUNKEN),
    sg.Frame(layout=right_side_layout, title='Console Log', relief=sg.RELIEF_SUNKEN)]
]

window_title = 'Wandering Inn Scraper'
window = sg.Window(window_title, layout, default_element_size=(40, 1), grab_anywhere=False)

confirm_title = "Confirm"


# Queue used for communication between threads
# Multi-threading used in order to prevent GUI-Freeze
gui_queue = queue.Queue()


# Event loop
while(True):
  event, values = window.read(timeout=100)   # Timeout used to ensure it's periodically checking the other thread

  if event in (None, 'Exit'):
    break


  if debug: 
    # print("Button:", event, " Values", values)
    print("Button:", event)
    print(getDebug(values))

  if event == 'Submit':
    # Check the data to make sure it's good, if not, throw error and continue loop


    # Open up the confirm window
    # confirm_window = sg.Window(confirm_title, confirm_layout, grab_anywhere=True)
    confirmed = sg.PopupYesNo("Here's the info you input: ", getDebug(values),"Are you sure you want to submit?", title="Confirm", )
    if confirmed == 'Yes':
      print("Beginning Program")
      start_url = values['beginning_link']
      end_url = values['ending_link']
      print_option = values['print_option']
      directory = values['folder_location']
      threading.Thread(target=backend.scrapePageInit,
                        args=(start_url, end_url, print_option, directory, gui_queue), daemon=True).start()
      # backend.scrapePageInit(start_url, end_url, print_option, directory)

      # print()
      # print('='*60)
      # print()
      # print("Congratulations! Your file(s) should be in the folder you specified")

  # If the scraper attempted to print information, print that information
  try: 
    message = gui_queue.get_nowait() 
  except queue.Empty:
    message = None 

  if message: 
    print(message)


  if event == 'About...':
    sg.popup(getAboutText(), title="About")

