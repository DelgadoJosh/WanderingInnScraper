import queue
import wanderingInnScraperBackEnd as backend
import os

gui_queue = queue.Queue()

start_url = "this_url_should_be_ignored"
stop_url = "https://wanderinginn.com/2017/03/04/rw1-02/"

print("=== STARTING RESUME SCRAPE ===")
try:
    backend.scrapePageInit(start_url, stop_url, "One Large File", "Test_Dir", "epub", gui_queue, None)
except Exception as e:
    import traceback
    traceback.print_exc()

import sys
sys.stdout.flush()

while not gui_queue.empty():
    print(gui_queue.get())
