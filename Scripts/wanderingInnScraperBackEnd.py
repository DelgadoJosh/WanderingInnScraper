import os
import csv
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString

# GLOBALS
curPageNum = 1
word_count = 0
debug = False
if debug:
  meta_file = open("00000 META.txt", "wb")
print_option = ''
headers = {
  # This header is used to mark the webscraper so the server knows
  # who's currently scraping it.
  'User-Agent': 'An interested fan',
  'From': 'fak3unknown1@gmail.com'
}

# Function that creates a stat page.
# At the moment, it only has the total word count
def printStats(directory, word_count): 
  fileTitle = "000 STATS.txt"
  fileTitleDirectory = directory + "/" + fileTitle
  file = open(fileTitleDirectory, "wb")

  stringToWrite = "Wandering Inn Stats\r\n"
  file.write(stringToWrite.encode('utf8'))

  stringToWrite = f"Word Count: {word_count}"
  file.write(stringToWrite.encode('utf8'))

# Function that handles writing to a file.
def writeToFile(file, title, contentsToWrite, format_choice, gui_queue):
  global meta_file
  global print_option
  #print(f"writetofile args: {file} {title} {contentsToWrite.te} {format_choice} {gui_queue}")
  if(format_choice == "txt"):
    file.write(title.encode('utf8'))
    file.write("\n\r\n\r".encode("utf8"))
    if(print_option == "Both"):
      meta_file.write(title.encode('utf8'))
      meta_file.write("\n\r\n\r".encode("utf8"))
  else:
    if (print_option != "One Large File"):
      file.write(f"""<!DOCTYPE html><html><head><link rel="stylesheet" type="text/css" href="style.css"/><title>{title}</title></head><body><h1>{title}</h1>""".encode("utf8"))
    if(print_option != "Individual Chapters"):
      meta_file.write(f"<h2 id='id{curPageNum}'>{title}</h2>".encode("utf8"))

  if(format_choice == "txt"):
    contentsToWrite = contentsToWrite.text
  file.write(str(contentsToWrite).encode("utf8"))
  if(print_option == "Both"):
    meta_file.write(str(contentsToWrite).encode("utf8"))  

  if(format_choice != "txt"):
    if(print_option != "One Large File"):
      file.write("</body></html>".encode("utf8"))
  else:
    file.write(("-"*60).encode("utf8"))
    if(print_option == "Both"):
      meta_file.write(("-"*60).encode("utf8"))


# Function to initialize scraping the page.
def scrapePageInit(start_page_url, stop_page_url, local_print_option, directory, format_choice, gui_queue):
  global print_option 
  global meta_file 
  print_option = local_print_option
  meta_file = open(directory + f"/The Wandering Inn.{format_choice}", "wb")
  if(print_option != "Individual Chapters" and format_choice == "html"):
    meta_file.write("""<!DOCTYPE html><html><head><link rel="stylesheet" type="text/css" href="style.css"/><title>The Wandering Inn</title></head><body><h1>The Wandering Inn</h1><hr/>""".encode("utf8"))
  scrapePage(start_page_url, stop_page_url, directory, format_choice, gui_queue)
  if(print_option != "Individual Chapters" and format_choice == "html"):
      meta_file.write("""</body></html>""".encode("utf8"))
# Recursive function to scrape the page using Python BeautifulSoup
def scrapePage(url, stop_page_url, directory, format_choice, gui_queue):
  global curPageNum
  global word_count
  global print_option

  # Removes the .wordpress found on the site
  url = url.replace(".wordpress","")  
  if debug:
    gui_queue.put(f"\nCurrently at {url}.")

  # Appends a '/' at the end if it's not seen in the url
  # This is to allow the inputted "stop" address to stop if it 
  # encounters an address that does not end in a '/'
  if(url[len(url)-1] != '/'):
    url += '/'
  
  if debug:
    gui_queue.put(f"\nUrl = {url} and stop_page_url = {stop_page_url}")

  # Accesses the page
  page = requests.get(url, headers)

  # Create a BeautifulSoup Object (aka parse Tree), and parse with built-in html.parser
  soup = BeautifulSoup(page.text, 'html.parser')

  # Grabs the title from the "entry-title" h1
  chapter_title_list = soup.find_all('h1', class_='entry-title')
  title = chapter_title_list[0].contents[0]
  if debug:
    gui_queue.put(title)
  gui_queue.put(f"\nCurrently Scraping {url} - {title}")

  # Creates a file for this specific chapter, only if needed
  fileTitle = F"{curPageNum:03d} {title}.{format_choice}"

  # fileTitleDirectory = f"{os.getcwd()}\\Chapters\\{curPageNum:03d} {title}.txt"
  fileTitleDirectory = directory + "/" + fileTitle
  file = meta_file
  if print_option != 'One Large File':
    file = open(fileTitleDirectory, "wb")


  # Pull all text from the "entry-content" div
  chapter_paragraph_list = soup.find(class_='entry-content')
  
  # Pull text from all instances of <p> tag within BodyText div
  chapter_paragraph_list_items = chapter_paragraph_list.find_all('p')

  # Grabs the final paragraph tag (which contains the next chapter)
  last_paragraph_item = chapter_paragraph_list_items[-1]
  if debug:
    gui_queue.put(f'Last item: {last_paragraph_item.contents[0]}')
  link_list = last_paragraph_item.find_all('a') # Grabs the <a> tags
  
  # Grabs the final paragraph that has an a tag
  for paragraph_item in reversed(chapter_paragraph_list_items):
    cur_link_list = paragraph_item.find_all('a')
    if(len(cur_link_list) > 0):
      link_list = cur_link_list
      break
  if(len(link_list) == 0):
    gui_queue.put("Stopped due to no next_chapter_link found")
    return
  next_chapter_link = link_list[-1]  # Grabs the final link to the next one
  next_chapter_url = next_chapter_link.get('href')

  writeToFile(file, title, chapter_paragraph_list, format_choice, gui_queue)
  for chapter_paragraph in chapter_paragraph_list_items[:-1]:
      
      # Goes through every tag within the paragraph.
      for chapter_paragraph_part in chapter_paragraph.contents[:-1]:
        text = chapter_paragraph_part
        if(not(isinstance(chapter_paragraph_part, NavigableString))):  
          text = chapter_paragraph_part.get_text()
        word_count += len(text.split())

      chapter_paragraph_last_part = chapter_paragraph.contents[-1]
      text = chapter_paragraph_last_part
      if(not(isinstance(chapter_paragraph_last_part, NavigableString))):  
        text = chapter_paragraph_last_part.get_text()
      word_count += len(text.split())
  gui_queue.put(f"Word Count: {word_count}")
  curPageNum = curPageNum + 1
  # Break out if done.
  if(url == stop_page_url):
    printStats(directory, word_count)
    gui_queue.put(" ")
    gui_queue.put("Reached the stopping page url, stopping.")

    gui_queue.put(" ")
    gui_queue.put("="*60)
    gui_queue.put(" ")
    gui_queue.put("Congratulations! Your file(s) should be in the folder you specified")
    return

  # Otherwise go to the next link and continue.
  scrapePage(next_chapter_url, stop_page_url, directory, format_choice, gui_queue)


