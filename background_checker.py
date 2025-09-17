import threading
import time
from payments import run_payment_checks

CHECK_INTERVAL = int(__import__("os").getenv("CHECK_INTERVAL_SECS", 60))

_stop_event = threading.Event()

def _loop():
    while not _stop_event.is_set():
        try:
            run_payment_checks()
        except Exception as e:
            print("background checker error:", e)
        # sleep with early exit
        for _ in range(int(CHECK_INTERVAL)):
            if _stop_event.is_set():
                break
            time.sleep(1)

def start_background_checker():
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    print("Background payment checker started.")
    return t

def stop_background_checker():
    _stop_event.set()