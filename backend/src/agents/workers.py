import time

def run_worker():
    print("Agent worker loop starting...")
    while True:
        time.sleep(5)
        print("Agent tick...")
