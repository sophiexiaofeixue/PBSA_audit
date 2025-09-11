import streamlit as st
import os
from datetime import datetime
import pandas as pd
from excel_processor import *


# Set up directories
UPLOAD_DIR = "uploads"
PREPARED_DOCS_DIR = os.path.join(UPLOAD_DIR, "prepared_docs")
COMPLIANCE_GUIDELINES_DIR = os.path.join(UPLOAD_DIR, "compliance_guidelines")

for directory in [UPLOAD_DIR, PREPARED_DOCS_DIR, COMPLIANCE_GUIDELINES_DIR]:
    os.makedirs(directory, exist_ok=True)

def save_uploaded_file(uploaded_file, directory):
    """Save uploaded file to specified directory and return the file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(directory, filename)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Initialize session state
if "guideline_path" not in st.session_state:
    st.session_state["guideline_path"] = None # path to the compliance guideline file

if "processed_guideline" not in st.session_state:
    st.session_state["processed_guideline"] = [] # list of processed guideline files

# Title
st.title("AI-Powered PBSA Audit Preparation & Continuous Compliance Maintenance for CRAs")

# Layout single column to upload guideline
# Create a big custom label
st.markdown("<h3 style='font-size:24px; font-weight:bold;'>Upload Your Compliance Guideline Files</h3>", unsafe_allow_html=True)

guideline = st.file_uploader("",
                             type = ["xls", "xlsx", "csv"],
                             accept_multiple_files=False)

if guideline:
    # save file once uploaded
    file_path = save_uploaded_file(guideline, COMPLIANCE_GUIDELINES_DIR)
    st.session_state["guideline_path"] = file_path
    st.write(f"uploaded and saved: {guideline.name}")

# process guideline button
if st.session_state.get("guideline_path"):
    if st.button("Process Compliance Guideline File"):
        # process and get the section numbers
        df = read_excel_or_csv(st.session_state["guideline_path"]) # the input is a string path
        section_numbers = get_section_numbers(df)
        st.session_state["processed_guideline"] = section_numbers
        st.success(f"Found {len(section_numbers)} sections in the guideline.")

# dropdown menu after guideline is processed
if st.session_state.get("processed_guideline"):
    selected_section = st.selectbox(
        "Select A Section to process prepared PDFs",
        st.session_state["processed_guideline"]
    )
    st.write(f"You selected section: {selected_section}")
