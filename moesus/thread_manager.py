import time
import queue
import threading
import traceback

import tqdm

pool = queue.Queue()
lock = threading.Lock()
progress = tqdm.tqdm(total=0, dynamic_ncols=True, smoothing=0.2)


def thread(function):
    t = 1.0

    while True:
        try:
            account = pool.get()
            account = function(account)

        except Exception:
            traceback.print_exc()
            t *= 1.5
            time.sleep(t)

        else:
            t = 1.0

        with lock:
            progress.update()
            pool.task_done()


def start_thread(thread, function, n_threads):
    for _ in range(n_threads):
        time.sleep(0.1)
        threading.Thread(target=thread, args=(function, ), daemon=True).start()
