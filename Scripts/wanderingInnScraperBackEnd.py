import os
import csv
import requests
import re
import json
import zipfile
import time
import random
import glob
import cloudscraper
from bs4 import BeautifulSoup
from bs4 import NavigableString

# GLOBALS
curPageNum = 1
word_count = 0
debug = False
next_links = None
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'From': 'fak3unknown1@gmail.com'
}
scraper = None

# Function to check if the current url matches the stop url.
# Also handles the 2017 vs 2023 Volume 1 discrepancy. (Vol 1 rewrite)
def is_url_match(current_url, stop_url):
  if current_url == stop_url:
    return True
  if "/rw1-" in current_url and "/rw1-" in stop_url:
    current_clean = current_url.replace("/2017/", "/2023/")
    stop_clean = stop_url.replace("/2017/", "/2023/")
    if current_clean == stop_clean:
      return True
  return False

# Function that will read in a json file containing
# manually inputted links if that file exists.
# This is for any unusual chapters where the "Next Chapter" link does not work.
def readLinkFile(gui_queue):
  global next_links
  filename = "links.json"
  filepath = os.path.join(os.getcwd(), filename)
  try: 
    with open(filepath, 'r') as file:
      json_text = file.read()
      next_links = json.loads(json_text)
  except Exception as e:
    gui_queue.put(f"WARNING: No links.json detected.")
    return

# Function that creates a stat page.
# At the moment, it only has the total word count.
def printStats(directory, word_count): 
  fileTitle = "000 STATS.txt"
  fileTitleDirectory = os.path.join(directory, fileTitle)
  with open(fileTitleDirectory, "wb") as file:
    stringToWrite = "Wandering Inn Stats\r\n"
    file.write(stringToWrite.encode('utf8'))
    stringToWrite = f"Word Count: {word_count}"
    file.write(stringToWrite.encode('utf8'))

# Function that creates a word frequency page.
# It ranks every word by how frequently it appears.
def printWordFrequency():
  global word_frequency_filename
  global word_frequency_dict
  word_frequency_headers = ["word", "frequency", "first-appearance", "last-appearance"]
  # Note: Make sure to use Unicode encoding (Specifically for 1.06 R "Dogeza")
  with open(word_frequency_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer_word_freq = csv.DictWriter(csv_file, fieldnames=word_frequency_headers)
    csv_writer_word_freq.writeheader()
    # Write the rows in decreasing order by their frequency
    for word in sorted(word_frequency_dict, key=lambda x: (word_frequency_dict[x]["frequency"]), reverse=True):
      csv_writer_word_freq.writerow(word_frequency_dict[word])

# Function that handles writing the individual chapter to a file.
# It also saves the source URL invisibly so the program can auto-resume later.
def writeChapterToFile(filepath, title, contentsToWrite, source_url):
  contentsToWrite = re.sub(r'[“”]', '&quot;', str(contentsToWrite))
  contentsToWrite = re.sub(r'[’]', '&apos;', str(contentsToWrite))
  contentsToWrite = str(contentsToWrite)
  
  temp_filepath = filepath + ".tmp"
  with open(temp_filepath, "wb") as file:
    file.write(f"<!-- Source URL: {source_url} -->\n".encode("utf8"))
    file.write(f"<h1>{title}</h1>\n".encode("utf8"))
    file.write(contentsToWrite.encode("utf8"))
  
  os.replace(temp_filepath, filepath)

# Function to remove punctuation
# TODO: Determine what is a good idea to remove or not. (:;*?![]{}*... etc.)
def removePunctuation(word):
  word = re.sub(r"[“”,;]", "", word)
  word = word.rstrip('.') 
  word = word.rstrip('?')
  word = word.rstrip('!')
  # Used rstrip to remove the periods at end of sentences. 
  # Not in the regex because it may be part of a word, or elipses...
  # Apostrophe's also may be part of a name (Az'kerash)
  return word

# Removes all illegal characters so a file/folder can be created successfully in Windows
def removeIllegalWindowsCharacters(file_path):
  file_path = re.sub(r'[<>:"\/\\\|\?\*]', "", file_path)
  file_path = file_path.strip()
  return file_path

# Scrapes the word count from the chapter and updates the dictionary
def getChapterWordCountAndUpdateWordFrequencies(paragraph_list, title):
  global word_frequency_dict 
  chapter_word_count = 0
  for chapter_paragraph in paragraph_list:

    # Goes through every tag within the paragraph.
    for chapter_paragraph_part in chapter_paragraph.contents:
      text = chapter_paragraph_part
      if(not(isinstance(chapter_paragraph_part, NavigableString))):  
        text = chapter_paragraph_part.get_text()
      
      split_text = text.split()
      for word in split_text:
        word = removePunctuation(word)

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
  
  return chapter_word_count

# Function to scan the existing files in a directory to find the last valid chapter.
# It will delete any corrupted/blank files and read the hidden Source URL to auto-resume.
def find_resume_state(directory, gui_queue):
  files = glob.glob(os.path.join(directory, "*.html"))
  valid_files = []
  for f in files:
    basename = os.path.basename(f)
    if "The Wandering Inn" in basename:
      continue
    match = re.match(r"^(\d{3})\s+(.+)\.html$", basename)
    if match:
      valid_files.append((int(match.group(1)), f))
          
  if not valid_files:
    return 1, None
      
  valid_files.sort(key=lambda x: x[0])
  
  for pagenum, f in reversed(valid_files):
    try:
      with open(f, 'r', encoding='utf-8') as html_file:
        content = html_file.read()
        soup = BeautifulSoup(content, 'html.parser')
        
        if not soup.find('p'):
          gui_queue.put(f"Deleting invalid/blank file: {os.path.basename(f)}")
          html_file.close()
          os.remove(f)
          continue
        
        match = re.search(r'<!-- Source URL: (.+?) -->', content)
        if match:
          resume_url = match.group(1).strip()
          return pagenum, resume_url
        else:
          gui_queue.put(f"File {os.path.basename(f)} is valid but missing Source URL metadata. Cannot auto-resume.")
          return pagenum, None
    except Exception as e:
      gui_queue.put(f"Error reading {os.path.basename(f)}: {e}")
      continue
          
  return 1, None

# Function to initialize scraping the page.
# Sets up the Cloudscraper session, checks for resume states, and handles the main scraping loop.
def scrapePageInit(start_page_url, stop_page_url, print_option, directory, format_choice, gui_queue, stop_event=None):
  global word_count
  global curPageNum
  global csv_file
  global csv_writer
  global word_frequency_filename
  global word_frequency_dict
  global scraper
  
  word_count = 0
  scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
  readLinkFile(gui_queue)

  last_page_num, resume_url = find_resume_state(directory, gui_queue)
  if resume_url:
    gui_queue.put(f"Found existing valid chapters! Resuming securely from {resume_url}")
    curPageNum = last_page_num + 1
    start_page_url = resume_url
    url = resume_url
    is_resuming = True
  else:
    curPageNum = 1
    url = start_page_url
    is_resuming = False

  mode = 'a' if is_resuming else 'w'
  csv_file = open(os.path.join(directory, '000 STATS.csv'), mode=mode, newline='') 
  csv_file_headers = ["title", "link", "chapter_word_count", "total_word_count"]
  csv_writer = csv.DictWriter(csv_file, fieldnames=csv_file_headers)
  if not is_resuming:
    csv_writer.writeheader()

  # Setup the necessary info to create a file for the word frequency
  word_frequency_filename = os.path.join(directory, '000 Word Frequency.csv')
  word_frequency_dict = {}

  about_to_scrape_last_page = False
  
  while True:
    if stop_event and stop_event.is_set():
      gui_queue.put("Stop signal received. Cleaning up...")
      if not csv_file.closed:
        printWordFrequency()
        printStats(directory, word_count)
        csv_file.close()
      return

    if is_url_match(url, stop_page_url):
      about_to_scrape_last_page = True
    
    url = scrapePage(url, stop_page_url, directory, gui_queue, stop_event, is_resuming_fetch=is_resuming)
    
    if is_resuming:
      is_resuming = False 
      time.sleep(random.uniform(2.0, 4.0))
      continue
    
    if url == "" or not url:
      break
    
    # If we just scraped the final page, stop
    if about_to_scrape_last_page:
      gui_queue.put("\nReached the stopping page url, stopping scrape.")
      gui_queue.put("="*60)
      gui_queue.put("Congratulations! Your individual chapter files have been downloaded.")
      gui_queue.put("You can now click 'Compile' to join them into your EPUB/HTML!")
      
      printWordFrequency()
      printStats(directory, word_count)
      csv_file.close()
      return
    
    sleep_time = random.uniform(5.0, 9.0)
    gui_queue.put(f"Pausing for {sleep_time:.1f} seconds to simulate human reading...\n")
    time.sleep(sleep_time)


# Function to scrape an individual page using BeautifulSoup and Cloudscraper.
# Returns the url for the next chapter.
def scrapePage(url, stop_page_url, directory, gui_queue, stop_event=None, is_resuming_fetch=False):
  global curPageNum
  global word_count
  global next_links
  global csv_file 
  global csv_writer
  global word_frequency_dict
  global scraper

  if not is_resuming_fetch:
    if debug: gui_queue.put(f"\nCurrently at {url}.")

  # Appends a '/' at the end if it's not seen in the url
  # This is to allow the inputted "stop" address to stop if it 
  # encounters an address that does not end in a '/'
  if(url[len(url)-1] != '/'):
    url += '/'
  
  # Accesses the page, with 3 retry attempts for VPN/Cloudflare blocks
  max_retries = 3
  page = None
  soup = None
  chapter_paragraph_list = None
  
  for attempt in range(max_retries):
    try:
      page = scraper.get(url, timeout=15)
      soup = BeautifulSoup(page.text, 'html.parser')
      
      # Pull all text from the new "twi-article" div, fallback to "entry-content"
      chapter_paragraph_list = soup.find(class_='twi-article')
      if not chapter_paragraph_list:
        chapter_paragraph_list = soup.find(class_='entry-content')
        
      if not chapter_paragraph_list:
        raise Exception("Article content container not found (Possible VPN/Cloudflare block).")
      else:
        break # Success! Escape the retry loop
        
    except Exception as e:
      if attempt < max_retries - 1:
        gui_queue.put(f"Blocking Issue Detected (Attempt {attempt+1}/{max_retries}): {e}")
        gui_queue.put("Re-initializing Cloudscraper session to dump tokens, waiting 10 seconds...\n")
        time.sleep(10)
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
      else:
        gui_queue.put(f"Network Error/Block persisting after {max_retries} attempts: Failed to fetch {url}.")
        gui_queue.put("Stopping scrape. You can resume safely later.")
        if stop_event: stop_event.set()
        return url

  title = None
  
  # == Title Handling ==
  # 1. Try meta og:title (most reliable)
  meta_title = soup.find("meta", property="og:title")
  if meta_title and meta_title.get("content"):
    title = meta_title.get("content").strip()

  # 2. Try standard <title> tag
  if not title:
    title_tag = soup.find('title')
    if title_tag and title_tag.text:
      title = title_tag.text.split('-')[0].strip()

  # 3. Try visible headers, but ignore "loading..."
  if not title:
    chapter_title_list = soup.find_all(class_='elementor-heading-title')
    if not chapter_title_list:
      chapter_title_list = soup.find_all('h1', class_='entry-title')
    for t in chapter_title_list:
      t_text = t.text.strip()
      if t_text and "loading" not in t_text.lower():
        title = t_text
        break

  # 4. Fallback: Parse from URL
  if not title:
    raw_url = url.rstrip('/')
    url_part = raw_url.split('/')[-1]
    title = url_part.replace('-', '.').capitalize()

  title = removeIllegalWindowsCharacters(title)
  if not is_resuming_fetch:
    gui_queue.put(f"Scraping: {url} - {title}")
  
  # Pull text from all instances of <p> tag within the container
  chapter_paragraph_list_items = chapter_paragraph_list.find_all('p')

  # Grabs the next chapter link
  # Will use the manual link if it exists
  next_chapter_url = ""
  if ((next_links != None) and ("AfterLinks" in next_links) and (url in next_links["AfterLinks"])):
    next_chapter_url = next_links["AfterLinks"][url]
  else:
    next_links_search = chapter_paragraph_list.find_all("a", string=lambda s: s and ("next chapter" in s.lower() or "next" in s.lower()))
    if len(next_links_search) == 0:
      if not is_resuming_fetch:
        gui_queue.put("Stopped due to no next_chapter_link found")
        if stop_event: stop_event.set()
      return ""
      
    next_chapter_link = next_links_search[-1]
    next_chapter_url = next_chapter_link.get('href')
    # Removes the .wordpress found on the site
    next_chapter_url = next_chapter_url.replace(".wordpress","")  

  if is_resuming_fetch:
    return next_chapter_url

  # Safely strip out the navigation links (Next Chapter / Previous Chapter) from the DOM
  # so they don't appear in the compiled book. Done via BeautifulSoup to prevent HTML mangling.
  for a_tag in chapter_paragraph_list.find_all("a"):
    link_text = a_tag.get_text().lower()
    # Explicitly search for "Next Chapter", "Next chapter", etc. in the article
    if "next" in link_text or "previous" in link_text:
      parent_p = a_tag.find_parent("p")
      if parent_p: parent_p.decompose()
      else: a_tag.decompose()

  # Creates a file for this specific chapter, only if needed
  fileTitle = f"{curPageNum:03d} {title}.html"
  fileTitleDirectory = os.path.join(directory, fileTitle)

  # Write this chapter to file
  writeChapterToFile(fileTitleDirectory, title, chapter_paragraph_list, url)
  
  # Grab the word count, but don't include the final "paragraph" which is just the next chapter links
  chapter_word_count = getChapterWordCountAndUpdateWordFrequencies(chapter_paragraph_list_items[:-1], title)
  word_count += chapter_word_count
  gui_queue.put(f"Word Count: {word_count}, Chapter Word: {chapter_word_count}")
  curPageNum += 1

  # Create a dictionary of information for the chapter
  chapter_info = {}
  chapter_info["title"] = title 
  chapter_info["link"] = url
  chapter_info["chapter_word_count"] = chapter_word_count
  chapter_info["total_word_count"] = word_count

  # Writes the chapter info to the csv file
  csv_writer.writerow(chapter_info)

  return next_chapter_url

# Function to compile all the individual HTML chapters into a single unified book format.
# Supports EPUB, HTML (with Table of Contents), and TXT formats.
def compileBook(directory, format_choice, print_option, gui_queue):
  gui_queue.put(f"\n--- Compiling downloaded files to {format_choice.upper()} ---")
  files = glob.glob(os.path.join(directory, "*.html"))
  valid_files = []
  for f in files:
    basename = os.path.basename(f)
    if "The Wandering Inn" in basename:
      continue
    match = re.match(r"^(\d{3})\s+(.+)\.html$", basename)
    if match:
      valid_files.append((int(match.group(1)), f, match.group(2)))
      
  valid_files.sort(key=lambda x: x[0])
  
  if not valid_files:
    gui_queue.put("No downloaded HTML chapters found to compile!")
    return
    
  toc_links = []
  
  if format_choice == "epub":
    epub_path = os.path.join(directory, "The Wandering Inn.epub")
    gui_queue.put("Creating The Wandering Inn.epub...")
    with zipfile.ZipFile(epub_path, 'w', compression=zipfile.ZIP_DEFLATED) as epub:
      epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
      container_xml = '''<?xml version="1.0" encoding="UTF-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n  <rootfiles>\n    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n  </rootfiles>\n</container>'''
      epub.writestr("META-INF/container.xml", container_xml)
      
      for pagenum, filepath, title in valid_files:
         anchor_id = f"id{pagenum}"
         chapter_filename = f"chapter_{pagenum:03d}.html"
         
         with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            xhtml = f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml">\n<head><title>{title}</title></head>\n<body>\n'
            contents_no_comment = re.sub(r'<!-- Source URL: .+? -->\n', '', content)
            contents_no_comment = contents_no_comment.replace('<h1>', f'<h1 id="{anchor_id}">', 1)
            xhtml += contents_no_comment + '\n</body>\n</html>'
            
            epub.writestr(f"OEBPS/{chapter_filename}", xhtml)
            toc_links.append((anchor_id, title, chapter_filename))
            gui_queue.put(f"Bundled {title} into EPUB...")
            
      opf = '''<?xml version="1.0" encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">\n  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n    <dc:title>The Wandering Inn</dc:title>\n    <dc:language>en</dc:language>\n    <dc:identifier id="BookId">urn:uuid:12345</dc:identifier>\n  </metadata>\n  <manifest>\n    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'''
      for _, _, filename in toc_links: opf += f'\n    <item id="{filename}" href="{filename}" media-type="application/xhtml+xml"/>'
      opf += '\n  </manifest>\n  <spine toc="ncx">'
      for _, _, filename in toc_links: opf += f'\n    <itemref idref="{filename}"/>'
      opf += '\n  </spine>\n</package>'
      epub.writestr("OEBPS/content.opf", opf)

      ncx = '''<?xml version="1.0" encoding="UTF-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n  <head><meta name="dtb:uid" content="urn:uuid:12345"/></head>\n  <docTitle><text>The Wandering Inn</text></docTitle>\n  <navMap>'''
      for idx, (anchor, toc_title, filename) in enumerate(toc_links, 1):
        ncx += f'\n    <navPoint id="navPoint-{idx}" playOrder="{idx}">\n      <navLabel><text>{toc_title}</text></navLabel>\n      <content src="{filename}#{anchor}"/>\n    </navPoint>'
      ncx += '\n  </navMap>\n</ncx>'
      epub.writestr("OEBPS/toc.ncx", ncx)
      
      gui_queue.put("Successfully created The Wandering Inn.epub!")
      
  elif format_choice == "html":
    if print_option == "Individual Chapters":
      gui_queue.put("HTML format selected, but Individual Chapters is also selected. Files are already extracted as Individual Chapters. Compile not required.")
      return
      
    html_path = os.path.join(directory, "The Wandering Inn.html")
    gui_queue.put("Compiling The Wandering Inn.html...")
    with open(html_path, "wb") as mf:
      mf.write("""<!DOCTYPE html><html><head><link rel="stylesheet" type="text/css" href="style.css"/><title>The Wandering Inn</title></head><body><h1>The Wandering Inn</h1>\n<h2>Table of Contents</h2><ul>\n""".encode("utf8"))
      
      body_contents = ""
      for pagenum, filepath, title in valid_files:
        anchor_id = f"id{pagenum}"
        mf.write(f"<li><a href='#{anchor_id}'>{title}</a></li>\n".encode("utf8"))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            contents_no_comment = re.sub(r'<!-- Source URL: .+? -->\n', '', content)
            contents_no_comment = contents_no_comment.replace('<h1>', f'<h2 id="{anchor_id}">', 1)
            contents_no_comment = contents_no_comment.replace('</h1>', '</h2>', 1)
            body_contents += contents_no_comment + "<hr/>\n"
        gui_queue.put(f"Bundled {title} into HTML...")
      
      mf.write("</ul><hr/>\n".encode("utf8"))
      mf.write(body_contents.encode("utf8"))
      mf.write("</body></html>".encode("utf8"))
      gui_queue.put("Successfully created The Wandering Inn.html!")
      
  elif format_choice == "txt":
    if print_option == "Individual Chapters":
      gui_queue.put("Compiling all chapters into individual .txt files...")
      for pagenum, filepath, title in valid_files:
        txt_path = os.path.join(directory, f"{pagenum:03d} {title}.txt")
        with open(filepath, 'r', encoding='utf-8') as f:
          content = f.read()
          soup = BeautifulSoup(content, 'html.parser')
          with open(txt_path, 'wb') as tf:
            tf.write(title.encode('utf8'))
            tf.write(("\n\r\n\r" + soup.text + "\n\r\n\r").encode('utf8'))
            tf.write(("-"*60).encode("utf8"))
      gui_queue.put("Successfully created Individual TXT files!")
    else:
      txt_path = os.path.join(directory, "The Wandering Inn.txt")
      gui_queue.put("Compiling The Wandering Inn.txt...")
      with open(txt_path, "wb") as mf:
        for pagenum, filepath, title in valid_files:
          with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            mf.write(title.encode('utf8'))
            mf.write(("\n\r\n\r" + soup.text + "\n\r\n\r").encode('utf8'))
            mf.write(("-"*60).encode("utf8"))
            mf.write("\n\r\n\r".encode("utf8"))
          gui_queue.put(f"Bundled {title} into TXT...")
      gui_queue.put("Successfully created The Wandering Inn.txt!")
