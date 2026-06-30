import streamlit as st
import os
import sys
import subprocess
import json

# Ensure we can import from src when running from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.database import get_all_files, search_files

# --- Config & Aesthetics ---
st.set_page_config(page_title="Smart File Organizer", layout="wide", initial_sidebar_state="expanded")

# Minimalist Custom CSS
st.markdown("""
<style>
    /* Clean Minimalist Typography and Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Card Design */
    .file-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .file-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    }
    .file-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 8px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .badge-category { background-color: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
    .badge-tag { background-color: #e0f2fe; color: #0369a1; }
    
    .summary-text {
        color: #4b5563;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-top: 12px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.abspath(os.getenv("DATABASE_PATH", "./data/file_manager.db"))

st.title("📂 Smart File Organizer")
st.markdown("A minimalist dashboard to search and locate your automatically organized files.")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Search & Filter")
search_query = st.sidebar.text_input("Search files, summaries, or tags...")

categories = ["All", "College", "Work", "Bills", "Receipts", "Certificates", "Personal", "Images", "Others", "Unsorted"]
selected_category = st.sidebar.selectbox("Filter by Category", categories)

# --- Data Loading ---
try:
    if search_query:
        files = search_files(DB_PATH, search_query)
    else:
        files = get_all_files(DB_PATH)
except Exception as e:
    st.error(f"Could not load database. Ensure the backend is running. ({e})")
    files = []

if selected_category != "All":
    files = [f for f in files if f['category'] == selected_category]

# --- UI Rendering ---
if not files:
    st.info("No files found matching your criteria.")
else:
    st.markdown(f"**Found {len(files)} files:**")
    
    for f in files:
        # Deserialize tags
        try:
            tags = json.loads(f['tags'])
        except:
            tags = []
            
        tags_html = "".join([f"<span class='badge badge-tag'>#{tag}</span>" for tag in tags])
        
        # We use a container to hold the card HTML and Streamlit button side-by-side
        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                card_html = f"""
                <div class="file-card">
                    <div class="file-title">{f['filename']}</div>
                    <span class="badge badge-category">{f['category']}</span>
                    {tags_html}
                    <div class="summary-text">{f['summary']}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">{f['processed_at'][:16].replace('T', ' ')}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
            with col2:
                st.write("")
                st.write("") 
                # Button to open file location
                if st.button("📁 Open Location", key=f"btn_{f['id']}"):
                    abs_path = os.path.abspath(f['new_path'])
                    if os.path.exists(abs_path):
                        # Windows specific command to open explorer and highlight file
                        subprocess.Popen(rf'explorer /select,"{abs_path}"')
                    else:
                        st.error("File moved/deleted.")
            st.markdown("---")
