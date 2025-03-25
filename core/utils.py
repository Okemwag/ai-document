import os

import PyPDF2
from docx import Document as DocxDocument

# Allowed file types
ALLOWED_EXTENSIONS = ['.txt', '.docx', '.pdf']

def validate_file(file):
    ext = os.path.splitext(file.name)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

def read_file(file):
    ext = os.path.splitext(file.name)[-1].lower()
    content = ""

    if ext == '.txt':
        content = file.read().decode('utf-8')
    elif ext == '.pdf':
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text
    elif ext == '.docx':
        doc = DocxDocument(file)
        content = '\n'.join([para.text for para in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    if not content.strip():
        raise ValueError("Empty content is not allowed")

    return content
