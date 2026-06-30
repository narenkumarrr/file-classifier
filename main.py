import os
from dotenv import load_dotenv
from src.watcher import start_watcher
from src.database import init_db

def main():
    load_dotenv()
    watch_folder = os.getenv("WATCH_FOLDER_PATH", "./WatchFolder")
    db_path = os.getenv("DATABASE_PATH", "./data/file_manager.db")
    
    # Ensure folders exist
    os.makedirs(watch_folder, exist_ok=True)
    
    # Initialize the database
    init_db(db_path)
    
    print(f"Starting Smart File Organizer...")
    start_watcher(watch_folder)

if __name__ == "__main__":
    main()
