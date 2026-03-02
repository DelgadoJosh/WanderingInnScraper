import queue
import threading
import sys
import wanderingInnScraperBackEnd as backend

gui_queue = queue.Queue()

def queue_reader():
    while True:
        try:
            msg = gui_queue.get()
            if msg == "QUIT": break
            print(msg)
            sys.stdout.flush()
        except:
            pass

t = threading.Thread(target=queue_reader)
t.daemon = True
t.start()

start_url = "ignored"
stop_url = "https://wanderinginn.com/2017/03/03/rw1-01/"

print("=== DEPLOYING TEST ===")
sys.stdout.flush()
backend.scrapePageInit(start_url, stop_url, "One Large File", "Test_Dir", "epub", gui_queue, None)

gui_queue.put("QUIT")
t.join()
