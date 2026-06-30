import os
from dotenv import load_dotenv
from src.watcher import start_watcher

def main():
    load_dotenv()
    watch_folder = os.getenv("WATCH_FOLDER_PATH", "./WatchFolder")
    
    # Ensure watch folder exists
    os.makedirs(watch_folder, exist_ok=True)
    
    print(f"Starting Smart File Organizer...")
    start_watcher(watch_folder)

if __name__ == "__main__":
    main()
