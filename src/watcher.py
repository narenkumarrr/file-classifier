import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def get_size(path: str) -> int:
    """Gets the size of a file or total size of a directory."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp) and os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    return 0

def wait_for_transfer_to_finish(path: str, check_interval: int = 1, stable_checks_required: int = 2):
    """Waits until the file or directory size stops changing."""
    stable_checks = 0
    last_size = -1

    while True:
        try:
            current_size = get_size(path)
        except OSError:
            # File might be temporarily locked or deleted
            current_size = -1

        if current_size == last_size and current_size != -1:
            stable_checks += 1
        else:
            stable_checks = 0
            last_size = current_size

        if stable_checks >= stable_checks_required:
            break

        time.sleep(check_interval)

class NewFileHandler(FileSystemEventHandler):
    def process_path(self, path: str, is_directory: bool):
        # Ignore hidden files/folders or temporary files
        basename = os.path.basename(path)
        if basename.startswith('.') or basename.startswith('~'):
            return

        print(f"Detected new {'directory' if is_directory else 'file'}: {path}")
        print("Waiting for transfer to complete...")
        wait_for_transfer_to_finish(path)
        print(f"Transfer complete for: {path}")
        
        # Placeholder for triggering the pipeline
        if is_directory:
            print(f"-> [PIPELINE] Sending directory '{basename}' to LLM for classification.")
        else:
            print(f"-> [PIPELINE] Extracting text from file '{basename}' and sending to LLM.")

    def on_created(self, event):
        self.process_path(event.src_path, event.is_directory)
        
    def on_moved(self, event):
        # Triggered when a file is moved/pasted into the directory
        self.process_path(event.dest_path, event.is_directory)

def start_watcher(watch_dir: str):
    observer = Observer()
    event_handler = NewFileHandler()
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.start()
    print(f"Started watching: {watch_dir} for new files/folders...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
