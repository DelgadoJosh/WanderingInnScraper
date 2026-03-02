import queue
import sys
import wanderingInnScraperBackEnd as backend
from collections import deque

gui_queue = queue.Queue()

start_url = "ignored"
stop_url = "https://wanderinginn.com/2017/03/04/rw1-02/"

print("=== STARTING CLEAN RESUME SCRAPE ===")
try:
    backend.scrapePageInit(start_url, stop_url, "One Large File", "Test_Dir", "epub", gui_queue, None)
except Exception as e:
    print(f"FAILED: {e}")

while not gui_queue.empty():
    print(gui_queue.get())
