import sqlite3
import json
import os
from datetime import datetime

def get_connection(db_path: str):
    return sqlite3.connect(db_path)

def init_db(db_path: str):
    """Initializes the SQLite database and tables."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_path TEXT NOT NULL,
            new_path TEXT NOT NULL,
            category TEXT NOT NULL,
            summary TEXT,
            tags TEXT,
            processed_at DATETIME NOT NULL,
            file_size INTEGER,
            file_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_file_metadata(db_path: str, metadata: dict) -> int:
    """Inserts processed file metadata into the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # tags will be a list in python, so we serialize it to JSON string
    tags_json = json.dumps(metadata.get('tags', []))
    
    cursor.execute('''
        INSERT INTO files (
            filename, original_path, new_path, category, 
            summary, tags, processed_at, file_size, file_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metadata.get('filename'),
        metadata.get('original_path'),
        metadata.get('new_path'),
        metadata.get('category'),
        metadata.get('summary'),
        tags_json,
        datetime.now().isoformat(),
        metadata.get('file_size'),
        metadata.get('file_hash')
    ))
    
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def get_all_files(db_path: str) -> list:
    """Retrieves all files from the database."""
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files ORDER BY processed_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_files(db_path: str, query: str) -> list:
    """Searches files by filename, category, or summary."""
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM files 
        WHERE filename LIKE ? OR category LIKE ? OR summary LIKE ? OR tags LIKE ?
        ORDER BY processed_at DESC
    ''', (search_term, search_term, search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
