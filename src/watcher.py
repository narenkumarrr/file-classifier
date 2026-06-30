import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"Detected new file: {event.src_path}")
            # Wait for file to finish writing, then trigger processing

def start_watcher(watch_dir: str):
    observer = Observer()
    event_handler = NewFileHandler()
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.start()
    print(f"Started watching: {watch_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
