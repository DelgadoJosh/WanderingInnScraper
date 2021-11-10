import os
import csv
import requests
import re
import json
from bs4 import BeautifulSoup
from bs4 import NavigableString

# GLOBALS
curPageNum = 1
word_count = 0
debug = False
if debug:
  meta_file = open("00000 META.txt", "wb")
next_links = None
print_option = ''
headers = {
  # This header is used to mark the webscraper so the server knows
  # who's currently scraping it.
  'User-Agent': 'An interested fan',
  'From': 'fak3unknown1@gmail.com'
}
csv_file_headers = [
  "title",
  "link",
  "chapter_word_count",
  "total_word_count",
]
word_frequency_headers = [
  "word",
  "frequency",
  "first-appearance",
  "last-appearance",
]

# Functiion that will read in a json file containing
# manually inputted links if that file exists
# This is for any unusual chapters where the "Next Chapter" link does not work
def readLinkFile(gui_queue):
  global next_links

  filename = "links.json"
  filepath = os.getcwd() + "\\" + filename
  try: 
    file = open(filepath)
    json_text = file.read()
    next_links = json.loads(json_text)
  except Exception as e:
    gui_queue.put(f"WARNING: No links.json detected, so no manual links were loaded")
    gui_queue.put(f"The program could not locate it at {filepath}")
    gui_queue.put(f" ")
    gui_queue.put(f"[DEBUG] Here's the details on the specific Exception: {e}")
    gui_queue.put(f" ")
    gui_queue.put(f"It's fine to run regardless, just be weary of any looping at the end of Volume 7!")
    return


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
  file.close()


def printWordFrequency():
  global word_frequency_headers
  global word_frequency_filename
  global word_frequency_dict

  # Note: Make sure to use Unicode encoding (Specifically for 1.06 R "Dogeza")
  with open(word_frequency_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer_word_freq = csv.DictWriter(csv_file, fieldnames=word_frequency_headers)
    csv_writer_word_freq.writeheader()

    # Write the rows in decreasing order by their frequency
    for word in sorted(word_frequency_dict, key=lambda x: (word_frequency_dict[x]["frequency"]), reverse=True):
      csv_writer_word_freq.writerow(word_frequency_dict[word])


# Function that handles writing to a file.
def writeToFile(file, title, contentsToWrite, format_choice, gui_queue):
  global meta_file
  global print_option
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
    # Remove all those pesky HTML tags
    contentsToWrite = contentsToWrite.text
  else:
    # Remove all those pesky, unescaped fancy quotes and apostrophes
    contentsToWrite = re.sub(r'[“”]', '&quot;', str(contentsToWrite))
    contentsToWrite = re.sub(r'[’]', '&apos;', str(contentsToWrite))

  # Remove text from links
  contentsToWrite = re.sub(r'(Previous chapter)?.*Next Chapter|', '', str(contentsToWrite), flags=re.I)
  
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
      meta_file.write("\n\r\n\r".encode("utf8"))


# Function to initialize scraping the page.
def scrapePageInit(start_page_url, stop_page_url, local_print_option, directory, format_choice, gui_queue):
  global print_option 
  global meta_file 
  global word_count
  global curPageNum
  global csv_file
  global csv_writer
  global csv_file_headers
  global word_frequency_filename
  global word_frequency_dict
  word_count = 0
  curPageNum = 1
  print_option = local_print_option
  meta_file = open(directory + f"/The Wandering Inn.{format_choice}", "wb")
  if(print_option != "Individual Chapters" and format_choice == "html"):
    meta_file.write("""<!DOCTYPE html><html><head><link rel="stylesheet" type="text/css" href="style.css"/><title>The Wandering Inn</title></head><body><h1>The Wandering Inn</h1><hr/>""".encode("utf8"))
  
  # Grabs manual links if they exist in a links.json
  readLinkFile(gui_queue)

  # Creates a csv file
  csv_file = open(directory + '/000 STATS.csv', mode='w', newline='') 
  csv_writer = csv.DictWriter(csv_file, fieldnames=csv_file_headers)
  csv_writer.writeheader()

  # Setup the necessary info to create a file for the word frequency
  word_frequency_filename = directory + '/000 Word Frequency.csv'
  word_frequency_dict = {}

  # Scrape until you reach the ending url
  about_to_scrape_last_page = False
  url = start_page_url
  while True:
    if url == stop_page_url:
      about_to_scrape_last_page = True
    
    url = scrapePage(url, stop_page_url, directory, format_choice, gui_queue)
    
    # If we just scraped the final page, stop
    if about_to_scrape_last_page:
      return


# Function to scrape the page using Python BeautifulSoup, returns the next url
def scrapePage(url, stop_page_url, directory, format_choice, gui_queue):
  global curPageNum
  global word_count
  global print_option
  global next_links
  global csv_file 
  global csv_writer
  global word_frequency_dict

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
  
  # Grabs the next chapter link
  # Will use the manual link if it exists
  if ((next_links != None) and ("AfterLinks" in next_links) and (url in next_links["AfterLinks"])):
    next_chapter_url = next_links["AfterLinks"][url]
  else:
    # Grabs the final paragraph that has an a tag
    for paragraph_item in reversed(chapter_paragraph_list_items):
      cur_link_list = paragraph_item.find_all('a')
      if(len(cur_link_list) > 0):
        link_list = cur_link_list
        break
    
    # Quits if there is no next chapter link found
    if(len(link_list) == 0):
      gui_queue.put("Stopped due to no next_chapter_link found")
      printStats(directory, word_count)
      file.close()
      return
    next_chapter_link = link_list[-1]  # Grabs the final link to the next one
    next_chapter_url = next_chapter_link.get('href')
    
    # Removes the .wordpress found on the site
    next_chapter_url = next_chapter_url.replace(".wordpress","")  

  # Write this page to file
  writeToFile(file, title, chapter_paragraph_list, format_choice, gui_queue)
  
  # Grab the word count
  chapter_word_count = 0
  for chapter_paragraph in chapter_paragraph_list_items[:-1]:
      
    # Goes through every tag within the paragraph.
    for chapter_paragraph_part in chapter_paragraph.contents:
      text = chapter_paragraph_part
      if(not(isinstance(chapter_paragraph_part, NavigableString))):  
        text = chapter_paragraph_part.get_text()
      
      split_text = text.split()
      for word in split_text:
        # Remove punctuation from the text.
        # TODO: Determine what is a good idea to remove or not. (:;*?![]{}*... etc.)
        word = re.sub(r"[“”,;]", "", word)  # Yes, this is the unicode ".  “” are different.
        word = word.rstrip('.') 
        word = word.rstrip('?')
        word = word.rstrip('!')
        # Used rstrip to remove the periods at end of sentences. 
        # Not in the regex because it may be part of a word, or elipses...
        # Apostrophe's also may be part of a name (Az'kerash)

        # Update the dictionary of word frequencies
        if word not in word_frequency_dict:
          # If it's not in the dictionary, this is the first time it's been seen
          word_frequency_dict[word] = {}
          word_frequency_dict[word]["word"] = word
          word_frequency_dict[word]["frequency"] = 0
          word_frequency_dict[word]["first-appearance"] = title

        word_frequency_dict[word]["frequency"] = word_frequency_dict[word]["frequency"] + 1
        word_frequency_dict[word]["last-appearance"] = title

      chapter_word_count += len(split_text)
  word_count += chapter_word_count
  gui_queue.put(f"Word Count: {word_count}, Chapter Word Count: {chapter_word_count}")
  curPageNum = curPageNum + 1

  # Create a dictionary of information for the chapter
  chapter_info = {}
  chapter_info["title"] = title 
  chapter_info["link"] = url
  chapter_info["chapter_word_count"] = chapter_word_count
  chapter_info["total_word_count"] = word_count

  # Writes the chapter info to the csv file
  csv_writer.writerow(chapter_info)

  # Clean up if you're done
  if(url == stop_page_url):

    if(print_option != "Individual Chapters" and format_choice == "html"):
      meta_file.write("""</body></html>""".encode("utf8"))
    meta_file.close()

    csv_file.close()
    
    printWordFrequency()
    printStats(directory, word_count)

    gui_queue.put(" ")
    gui_queue.put("Reached the stopping page url, stopping.")

    gui_queue.put(" ")
    gui_queue.put("="*60)
    gui_queue.put(" ")
    gui_queue.put("Congratulations! Your file(s) should be in the folder you specified")

  # Clean up the file if we're done with the individual file
  if(print_option == "Individual Chapters"):
    file.close()



  return next_chapter_url


