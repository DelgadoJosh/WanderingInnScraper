# WanderingInnScraper
A Webscraper for the Wandering Inn Web Novel, packaged in a GUI


This program allows one to download as much or as little of the web novel **The Wandering Inn** as a .txt file.

It has a nice little front end that takes in 4 options to specify how to download everything:

1. How to print (one master file, or separated by chapter)
1. The first chapter to print's address
1. The last chapter to print's address (inclusive)
1. The destination folder

It also features a console log to see the current progress of the webscraper. As of testing (Jan 19, 2020), it should take roughly 5 minutes to scrape all four million words of the wandering inn.

If you print a 

### How to run
In order to run this,

1. Download both wanderingInnFrontEnd.py and WanderingInnBackEnd.py and have them in the same folder.
1. Execute the wanderingInnFrontEnd.py script with "python 'locationOfTheScript\wanderingInnFrontEnd.py'".
  For example: python "C:\MyUserName\Downloads\wanderingInnFrontEnd.py"
1. Fill in the information required.
  1. Select what type of output file you want.
  1. Type/Paste in the web address of the first chapter to scrape.
  1. Type/Paste in the web address of the last.
  1. Select "Browse" and select the destination folder
1. Press the Submit Button
1. Sit back, and relax!

### Screenshots
![GUI Screenshot](/images/guiScreenshot.png)
Picture of the GUI


![GUI In Use](/images/demo.gif) 
Example of the Script being run
