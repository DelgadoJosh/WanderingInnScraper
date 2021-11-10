# The Wandering Inn Scraper
A Webscraper for the Web Novel **The Wandering Inn**, packaged in a GUI.

Created by Josh Delgado and BurningEmbyr

## Description

This program allows one to download as much or as little of the web novel **The Wandering Inn** as you'd like, as either a .txt or .html file. It uses Python's Beautiful Soup for the webscraping, PySimpleGUI for the GUI, and PyInstaller for the executable file.

It has a GUI that takes in five options to specify how to download everything:

1. **How to print** (one master file, or separated by chapter)
1. What **format** to print (plain text, or HTML)
1. The **first chapter** to print's address
1. The **last chapter** to print's address (inclusive)
1. The **destination folder**


It also features a console log to see the current progress of the webscraper. As of testing (March 8, 2021), it should take roughly ten minutes to scrape all seven million words of the wandering inn.

If you print each chapter individually, it will automatically number them in order to ensure they are ordered in the right order. This is to offset the fact that some chapters (e.g. 1.01 R, 1.00 D, and any Interlude) would appear out of order otherwise.

### Expected Output

* The Wandering Inn.html / The Wandering Inn.txt
  * A meta-file that contains all the chapters in a single file
  * Will only spawn if you want a master file, or both a master file and single chapters
* NNN Title.txt / NNN Title.html
  * An individual chapter, where NNN is the order of the chapters.
  * The NNN is added as some chapter names may be out of order otherwise (e.g. 1.01 R, 1.00 D, and any Interlude)
* 000 STATS.csv
  * A comma separated file (basically an excel file) giving the word counts for each chapter
* 000 STATS.txt
  * A text file containing the total word count.
* 000 Word Frequency.csv
  * A text file containing all the words in The Wandering Inn and their frequency, and the first and last chapters they appear in.
  * Note: To open this file in excel, don't open the file itself, you have to import the data (by default, it'll read it as a western file, but you want to read unicode instead). To do so, follow this [guide](https://stackoverflow.com/questions/6002256/is-it-possible-to-force-excel-recognize-utf-8-csv-files-automatically). The tl;dr is to import it by opening a blank workbook and then use Data > Import External Data > Import Data. Then change the file origin to "65001 UTF-8" with commas as the delimiter.



## Screenshots
![GUI Screenshot](/images/GUI_Screenshot.png)
Picture of the GUI <br></br>

![GUI In Use](/images/demo.gif) 
Example of the Script being run <br></br>



## How to use

### With an executable
In order to run this,

1. Download `WanderingInnScraper.exe` found in the **Executable** folder (or use the [Releases](https://github.com/DelgadoJosh/WanderingInnScraper/releases) page and download it by clicking **Assets** on the most recent version then clicking `WanderingInnScraper.exe`).
    1. Technically optional, but highly recommended: Download `links.json`, which is also found in the **Executable** folder (or use the [Releases](https://github.com/DelgadoJosh/WanderingInnScraper/releases) page).
        1. This is used to manually add links for irregular hyperlinks on the site. It's recommended to not look too much into the links themselves if you're worried about spoilers.
        1. Once you have `links.json`, make sure you put it in the same folder as `WanderingInnScraper.exe`.
1. Double click the `WanderingInnScraper.exe` once downloaded.
1. Fill in the information required.
    1. Select what **type of output** file you want.
    1. Select what **format of output** file you want
    1. Type/Paste in the web address of the **first** chapter to scrape.
    1. Type/Paste in the web address of the **last** chapter.
    1. Select **"Browse"** and select the destination folder, or type/paste in the folder address.
1. Press the **Submit** Button.
1. Sit back, and relax!
    1. If you selected **HTML** output, you can download the `style.css` file from the **Example Output** directory into the directory with your html files, to make the files more readable.  

### With the python scripts themselves
1. Follow the instructions in the `dependencies.md` file found in the **Scripts** folder of this repository.
1. Download both `wanderingInnFrontEnd.py` and `WanderingInnBackEnd.py` from the **Scripts** folder and have them in the same folder.
    1. Technically optional, but highly recommended: Download `links.json`, which is also found in the **Scripts** folder.
        1. This is used to manually add links for irregular hyperlinks on the site. It's recommended to not look too much into the links themselves if you're worried about spoilers.
        1. Once you have `links.json`, make sure you put it in the same folder as `WanderingInnScraper.exe`.
1. Execute the `wanderingInnFrontEnd.py` script with `python "locationOfTheScript\wanderingInnFrontEnd.py"`.
  For example: `python "C:\MyUserName\Downloads\wanderingInnFrontEnd.py"`
1. Fill in the information required.
    1. Select what **type of output** file you want
    1. Select what **format of output** file you want
    1. Type/Paste in the web address of the **first** chapter to scrape.
    1. Type/Paste in the web address of the **last** chapter.
    1. Select **"Browse"** and select the destination folder, or type/paste in the folder address.
1. Press the **Submit** Button.
1. Sit back, and relax!
    1. If you selected **HTML** output, you can download the **style.css** file from the **Example Output** directory into the directory with your html files, to make the files more readable.   


