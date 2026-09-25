import sqlite3
import os

DB_PATH = "data/documents.db"

def get_connection():
    """Creates and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Initializes the SQLite database and creates the documents table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            category TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_hash TEXT UNIQUE NOT NULL,
            text_preview TEXT,
            status TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_document(filename, file_path, category, file_size, file_hash, text_preview, status):
    """Inserts a new document record into the SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO documents (filename, file_path, category, file_size, file_hash, text_preview, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename, file_path, category, file_size, file_hash, text_preview, status))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def get_all_documents():
    """Retrieves all documents stored in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY upload_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_document_by_hash(file_hash):
    """Finds a document by its SHA-256 hash to check for duplicates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_document(doc_id, file_path):
    """Deletes a document record from the database and removes the file from disk."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()

    if os.path.exists(file_path):
        os.remove(file_path)