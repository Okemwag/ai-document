import logging
import os
from typing import Optional, Union

import mammoth
import PyPDF2
import textract

logger = logging.getLogger(__name__)


def read_document_content(file_path: Union[str, os.PathLike]) -> Optional[str]:
    """
    Read the content of a document file with robust error handling.

    Supports:
    - .docx (Microsoft Word)
    - .pdf (Adobe PDF)
    - .txt (Plain Text)
    - .rtf (Rich Text Format)
    - .doc (Older Microsoft Word)

    Args:
        file_path (str or PathLike): Path to the document file

    Returns:
        Optional[str]: Extracted text content or None if extraction fails
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    try:
        # Determine file extension
        file_extension = os.path.splitext(file_path)[1].lower()

        # Read different file types
        if file_extension == ".docx":
            return _read_docx(file_path)
        elif file_extension == ".pdf":
            return _read_pdf(file_path)
        elif file_extension == ".txt":
            return _read_txt(file_path)
        elif file_extension in [".rtf", ".doc"]:
            return _read_legacy_document(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return None

    except Exception as e:
        logger.error(f"Error reading document {file_path}: {str(e)}")
        return None


def _read_docx(file_path: str) -> Optional[str]:
    """
    Read content from .docx files using mammoth library.

    Args:
        file_path (str): Path to the .docx file

    Returns:
        Optional[str]: Extracted text content
    """
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            return result.value.strip()
    except Exception as e:
        logger.error(f"Error reading DOCX file {file_path}: {str(e)}")
        return None


def _read_pdf(file_path: str) -> Optional[str]:
    """
    Read content from PDF files using PyPDF2.

    Args:
        file_path (str): Path to the PDF file

    Returns:
        Optional[str]: Extracted text content
    """
    try:
        with open(file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {str(e)}")
        return None


def _read_txt(file_path: str) -> Optional[str]:
    """
    Read content from plain text files.

    Args:
        file_path (str): Path to the text file

    Returns:
        Optional[str]: File content
    """
    try:
        with open(file_path, "r", encoding="utf-8") as txt_file:
            return txt_file.read().strip()
    except UnicodeDecodeError:
        # Try alternative encodings if UTF-8 fails
        try:
            with open(file_path, "r", encoding="latin-1") as txt_file:
                return txt_file.read().strip()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            return None


def _read_legacy_document(file_path: str) -> Optional[str]:
    """
    Read content from legacy document formats using textract.

    Args:
        file_path (str): Path to the document file

    Returns:
        Optional[str]: Extracted text content
    """
    try:
        # textract handles .rtf, .doc and some other legacy formats
        return textract.process(file_path).decode("utf-8").strip()
    except Exception as e:
        logger.error(f"Error reading legacy document {file_path}: {str(e)}")
        return None


def clean_text(text: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Clean extracted text by removing excessive whitespaces and optionally truncating.

    Args:
        text (Optional[str]): Input text
        max_length (Optional[int]): Maximum length to truncate text

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Remove excessive whitespaces
    cleaned_text = " ".join(text.split())

    # Truncate if max_length is specified
    if max_length and len(cleaned_text) > max_length:
        cleaned_text = cleaned_text[:max_length]

    return cleaned_text
