# backend/utils/file_handler.py

import os
from docx import Document

def process_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def process_docx_file(path):
    doc = Document(path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return '\n'.join(text)
