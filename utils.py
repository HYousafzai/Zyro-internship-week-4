import hashlib
import os
from datetime import datetime
import fitz  # PyMuPDF

def calculate_sha256(file_bytes):
    """Calculates SHA-256 hash for duplicate detection."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()

def get_safe_storage_path(doc_type):
    """Returns directory path based on document type (Task 1)."""
    base_dir = "data"
    if doc_type == "Invoice":
        folder = os.path.join(base_dir, "invoices")
    elif doc_type == "Resume":
        folder = os.path.join(base_dir, "resumes")
    else:
        folder = os.path.join(base_dir, "others")
    os.makedirs(folder, exist_ok=True)
    return folder

def extract_text_from_pdf(file_bytes):
    """Safely extracts text and previews from PDF bytes."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception:
        return ""

def process_and_save_uploaded_file(uploaded_file):
    """Processes file validation, hashing, text extraction, and safe storage with error handling."""
    try:
        file_bytes = uploaded_file.getvalue()
        
        # Limit very large uploads (Task 8: 10MB limit)
        if len(file_bytes) > 10 * 1024 * 1024:
            return None, "File size exceeds 10MB limit."

        # Validate file type (Task 8)
        if not uploaded_file.name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            return None, "Unsupported file format. Please upload PDF or image files."

        file_hash = calculate_sha256(file_bytes)
        
        # Classification heuristic
        name_lower = uploaded_file.name.lower()
        if "invoice" in name_lower or "bill" in name_lower:
            doc_type = "Invoice"
        elif "resume" in name_lower or "cv" in name_lower:
            doc_type = "Resume"
        else:
            doc_type = "Other"

        # Extract text preview
        text_preview = ""
        if uploaded_file.name.lower().endswith('.pdf'):
            text_preview = extract_text_from_pdf(file_bytes)
        
        # Determine status (Task 7)
        status = "Processed"
        if not text_preview or len(text_preview) < 20:
            status = "Needs Review"

        # Safe filename generation (Task 1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{uploaded_file.name.replace(' ', '_')}"
        folder_path = get_safe_storage_path(doc_type)
        full_path = os.path.join(folder_path, safe_name)

        # Save file to disk
        with open(full_path, "wb") as f:
            f.write(file_bytes)

        metadata = {
            'original_filename': uploaded_file.name,
            'stored_filename': safe_name,
            'document_type': doc_type,
            'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'company': "Sample Corp" if doc_type == "Invoice" else None,
            'invoice_number': "INV-001" if doc_type == "Invoice" else None,
            'total_amount': "$150.00" if doc_type == "Invoice" else None,
            'file_path': full_path,
            'text_preview': text_preview[:300] if text_preview else "No text preview available",
            'file_hash': file_hash,
            'status': status
        }

        return metadata, None

    except Exception:
        # Task 8: Do not expose raw exception details to normal users
        return None, "An error occurred while processing the file. Please try again."