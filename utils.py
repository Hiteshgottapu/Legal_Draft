# utils.py
import streamlit as st
from functools import wraps

# Error handling decorator for Streamlit UI functions
def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"[Error] {str(e)}")
            return None
    return wrapper

# Export document in various formats (TXT, PDF, DOCX)
def export_document(content, export_format):
    if not content:
        st.warning("No document to export.")
        return
    if export_format == "TXT":
        st.download_button(
            label="Download as TXT",
            data=content,
            file_name="legal_document.txt",
            mime="text/plain"
        )
    elif export_format == "PDF":
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in content.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            st.download_button(
                label="Download as PDF",
                data=pdf_bytes,
                file_name="legal_document.pdf",
                mime="application/pdf"
            )
        except ImportError:
            st.error("PDF export requires the 'fpdf' package. Please install it via 'pip install fpdf'.")
    elif export_format == "DOCX":
        try:
            from docx import Document
            from io import BytesIO
            doc = Document()
            for line in content.split('\n'):
                doc.add_paragraph(line)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download as DOCX",
                data=buffer,
                file_name="legal_document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except ImportError:
            st.error("DOCX export requires the 'python-docx' package. Please install it via 'pip install python-docx'.")
    else:
        st.warning("Unsupported export format.")
