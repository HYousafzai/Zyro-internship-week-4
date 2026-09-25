#  AI-Powered Document Management System

An intelligent document processing and management web application built with **Python**, **Streamlit**, and **SQLite**. The system automatically extracts text from uploaded files (PDFs, TXT), performs smart content categorization, computes file hashes to prevent duplicates, and organizes files into structured directories.

---

##  Key Features

* **Smart Document Categorization:** Automatically classifies uploaded documents into categories such as `resumes`, `invoices`, or `others` based on filenames and text contents.
* **Text Extraction & Preview:** Extracts readable text streams from PDF and text documents for quick review.
* **Duplicate Protection:** Computes SHA-256 hashes for every uploaded file to prevent duplicate entries in the database.
* **Database & File Management:** Backed by SQLite for relational metadata storage and organized local directory paths for physical storage.
* **Interactive Dashboard:** View real-time system metrics, explore stored repositories with built-in text preview cards, download files, or delete records.
* **Search & Filter:** Instantly filter and search through uploaded document filenames and extracted preview contents.

---

##  Tech Stack

* **Frontend/UI:** [Streamlit](https://streamlit.io/)
* **Database:** SQLite
* **Data Processing & Parsing:** Pandas, `pypdf`
* **Utilities:** Hashlib, OS, IO

---

##  Installation & Setup

1. **Clone the repository or open your project folder:**
   ```bash
   cd your-project-folder


Create and activate a virtual environment (Recommended):Bashpython -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install the required dependencies:Bashpip install streamlit pandas pypdf
Run the Streamlit application:Bashstreamlit run app.py
 Project Directory StructurePlaintext├── data/
│   ├── resumes/          # Auto-sorted resume/CV documents
│   ├── invoices/         # Auto-sorted invoice/bill documents
│   ├── others/           # Unclassified or general documents
│   └── documents.db      # SQLite relational database
├── app.py                # Main Streamlit application script
└── README.md             # Project documentation
 How to Use:
 Launch the app using streamlit run app.py.   Navigate to the Dashboard / Upload tab from the sidebar.Choose a document (.pdf, .txt, .png, .jpg) using the file uploader widget.   Click the " Process & Index Document" button to extract text, categorize, and commit the file to storage.Switch to View Documents to inspect extracted text previews, download files, or manage deletions.Use Search & Filter to quickly query specific document keywords.