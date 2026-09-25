import streamlit as st
import os
import sqlite3
import hashlib
import pandas as pd
import io

# Safely import pypdf
try:
    import pypdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Database configuration
DB_PATH = "data/documents.db"

def get_connection():
    """Creates and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the SQLite database table and resets schema to prevent column mismatch errors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("""
        CREATE TABLE documents (
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
    """Inserts a new document record into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO documents (filename, file_path, category, file_size, file_hash, text_preview, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename, file_path, category, file_size, file_hash, text_preview, status))
        conn.commit()
    except Exception as e:
        st.error(f"Database Insert Error: {e}")
    finally:
        conn.close()

def get_all_documents():
    """Retrieves all documents."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY upload_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_document_by_hash(file_hash):
    """Finds a document by its SHA-256 hash."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_document(doc_id, file_path):
    """Deletes a document record and file."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    if os.path.exists(file_path):
        os.remove(file_path)

def calculate_sha256(file_bytes):
    """Calculates SHA-256 hash."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()

def process_and_save_document(uploaded_file):
    """Extracts text, determines category, saves to disk, and prepares database values."""
    filename = uploaded_file.name
    lower_name = filename.lower()
    
    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()
    file_hash = calculate_sha256(file_bytes)
    file_size = len(file_bytes)
    
    text_content = ""
    try:
        if lower_name.endswith(".pdf") and PDF_SUPPORT:
            uploaded_file.seek(0)
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n"
        elif lower_name.endswith(".txt"):
            text_content = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        text_content = f"Parsing error encountered: {str(e)}"

    if len(text_content.strip()) < 10:
        text_content = "Scanned or non-textual document layout."
        status = "Needs Review"
    else:
        status = "Indexed"

    combined_text = (filename + " " + text_content).lower()
    if "invoice" in combined_text or "bill" in combined_text or "receipt" in combined_text:
        category = "invoices"
    elif "resume" in combined_text or "cv" in combined_text or "experience" in combined_text or "education" in combined_text:
        category = "resumes"
    else:
        category = "others"

    save_dir = os.path.join("data", category)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    return file_path, category, file_size, file_hash, text_content[:500], status

# Initialize Database with automatic schema reset
init_db()

st.set_page_config(page_title="Document Management System", page_icon="📁", layout="wide")
st.title("📁 AI-Powered Document Management System")

menu = ["Dashboard / Upload", "View Documents", "Search & Filter"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Dashboard / Upload":
    st.header("📤 Upload New Document")
    uploaded_file = st.file_uploader("Choose a file (PDF, PNG, JPG, TXT)", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if uploaded_file is not None:
        # Add an explicit button to trigger processing reliably
        if st.button("🚀 Process & Index Document"):
            uploaded_file.seek(0)
            temp_bytes = uploaded_file.read()
            file_hash = calculate_sha256(temp_bytes)
            
            existing_doc = get_document_by_hash(file_hash)
            
            if existing_doc:
                st.warning(f"⚠️ Duplicate file detected! This document already exists under category: **{existing_doc[3]}**.")
            else:
                with st.spinner("Processing document text and indexing metadata..."):
                    file_path, category, file_size, file_hash, text_preview, status = process_and_save_document(uploaded_file)
                    add_document(uploaded_file.name, file_path, category, file_size, file_hash, text_preview, status)
                st.success(f"✅ Successfully processed and saved to `{category}/` folder!")
                st.balloons()

    st.markdown("---")
    st.subheader("📊 System Overview")
    docs = get_all_documents()
    if docs:
        df_metrics = pd.DataFrame(docs)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Documents", len(df_metrics))
        col2.metric("Categories", df_metrics.iloc[:, 3].nunique() if len(df_metrics.columns) > 3 else 1)
        col3.metric("Pending Review", len(df_metrics[df_metrics.iloc[:, 7] == "Needs Review"]) if len(df_metrics.columns) > 7 else 0)
    else:
        st.info("No documents uploaded yet.")

elif choice == "View Documents":
    st.header("🗂️ Document Repository")
    docs = get_all_documents()
    if not docs:
        st.info("No documents found in the database.")
    else:
        for row in docs:
            doc_id, filename, file_path, category, size, file_hash, preview, status, upload_date = row[:9]
            with st.expander(f"📄 {filename} ({category}) - Status: {status}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**Size:** {size} bytes | **Upload Date:** {upload_date}")
                    st.text_area("Extracted Text Preview", preview, height=100, key=f"preview_{doc_id}")
                with col_b:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as dl:
                            st.download_button("📥 Download", data=dl, file_name=filename, key=f"dl_{doc_id}")
                    if st.button("🗑️ Delete", key=f"del_{doc_id}"):
                        delete_document(doc_id, file_path)
                        st.success("Deleted successfully!")
                        st.rerun()

elif choice == "Search & Filter":
    st.header("🔍 Search Documents")
    docs = get_all_documents()
    if not docs:
        st.info("No documents available.")
    else:
        df = pd.DataFrame(docs)
        if len(df.columns) >= 9:
            df.columns = ["ID", "Filename", "Path", "Category", "Size", "Hash", "Preview", "Status", "Date"] + [f"Extra_{i}" for i in range(len(df.columns) - 9)]
        
        query = st.text_input("Search filename or preview text:")
        if query and "Filename" in df.columns:
            df = df[df["Filename"].str.contains(query, case=False, na=False) | df["Preview"].str.contains(query, case=False, na=False)]
            
        st.dataframe(df.iloc[:, :9] if len(df.columns) >= 9 else df)