import sys
import os
import threading
import time
import requests
from werkzeug.wrappers import Response

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.camera import ThreadPoolWSGIServer

def simple_app(environ, start_response):
    # Simulate work
    time.sleep(0.5)
    response = Response('Hello World', mimetype='text/plain')
    return response(environ, start_response)

def test_threading():
    port = 9999
    max_workers = 5
    print(f"Starting server with max_workers={max_workers}")
    server = ThreadPoolWSGIServer('127.0.0.1', port, simple_app, max_workers=max_workers)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1) # Wait for server to start

    active_requests = 0
    lock = threading.Lock()

    def make_request():
        nonlocal active_requests
        try:
            with lock:
                active_requests += 1
            requests.get(f'http://127.0.0.1:{port}/')
        except Exception as e:
            print(f"Request failed: {e}")
        finally:
            with lock:
                active_requests -= 1

    client_threads = []
    # Launch 20 concurrent requests
    print("Launching 20 concurrent requests...")
    for _ in range(20):
        t = threading.Thread(target=make_request)
        client_threads.append(t)
        t.start()

    # Check active thread count in the pool
    # ThreadPoolExecutor creates threads on demand up to max_workers.
    # Since we have 20 requests and each takes 0.5s, the pool should fill up to 5 workers.

    time.sleep(0.2) # Wait for requests to hit server

    # Count threads
    # Python 3.x ThreadPoolExecutor threads are typically named "ThreadPoolExecutor-x_y"
    threads = threading.enumerate()
    pool_threads = [t for t in threads if "ThreadPoolExecutor" in t.name]

    print(f"Total active threads: {len(threads)}")
    print(f"Pool threads detected: {len(pool_threads)}")

    for t in threads:
         if "ThreadPoolExecutor" in t.name:
             print(f"  Pool Thread: {t.name}")

    if len(pool_threads) > max_workers:
        print(f"FAIL: Pool threads {len(pool_threads)} > max_workers {max_workers}")
        sys.exit(1)
    elif len(pool_threads) == 0:
        print("WARNING: No pool threads detected (naming might vary)")
    else:
        print(f"PASS: Pool threads {len(pool_threads)} <= max_workers {max_workers}")

    # Wait for completion
    for t in client_threads:
        t.join()

    server.shutdown()
    server.server_close()

if __name__ == "__main__":
    test_threading()
