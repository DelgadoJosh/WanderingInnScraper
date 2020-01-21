# WanderingInnScraper
A Webscraper for the Web Novel **The Wandering Inn**, packaged in a GUI.

Created by Josh Delgado

## Description

This program allows one to download as much or as little of the web novel **The Wandering Inn** as a .txt file. It uses Python's Beautiful Soup for the webscraping, and PySimpleGUI for the GUI.

It has a GUI that takes in four options to specify how to download everything:

1. **How to print** (one master file, or separated by chapter)
1. The **first chapter** to print's address
1. The **last chapter** to print's address (inclusive)
1. The **destination folder**


It also features a console log to see the current progress of the webscraper. As of testing (Jan 19, 2020), it should take roughly five minutes to scrape all four million words of the wandering inn.

If you print each chapter individually, it will automatically number them in order to ensure they are ordered in the right order. This is to offset the fact that some chapters (e.g. 1.01 R, 1.00 D, and any Interlude) would appear out of order otherwise.

## How to use

### With an executable
In order to run this,

1. Download **WanderingInnScraper.exe** found in the **Executable** folder.
1. Double click the **WanderingInnScraper.exe** once downloaded.
1. Fill in the information required.
    1. Select what **type of output** file you want.
    1. Type/Paste in the web address of the **first** chapter to scrape.
    1. Type/Paste in the web address of the **last** chapter.
    1. Select **"Browse"** and select the destination folder
1. Press the **Submit** Button
1. Sit back, and relax!

### With the python scripts themselves
1. Download both **wanderingInnFrontEnd.py** and **WanderingInnBackEnd.py** and have them in the same folder.
1. Execute the wanderingInnFrontEnd.py script with **"python 'locationOfTheScript\wanderingInnFrontEnd.py'"**.
  For example: "python "C:\MyUserName\Downloads\wanderingInnFrontEnd.py"
1. Fill in the information required.
    1. Select what **type of output** file you want.
    1. Type/Paste in the web address of the **first** chapter to scrape.
    1. Type/Paste in the web address of the **last** chapter.
    1. Select **"Browse"** and select the destination folder
1. Press the **Submit** Button
1. Sit back, and relax!


## Screenshots
![GUI Screenshot](/images/GUI_Screenshot.png)
Picture of the GUI



![GUI In Use](/images/demo.gif) 
Example of the Script being run

