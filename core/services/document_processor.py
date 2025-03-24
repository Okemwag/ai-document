import os
import logging
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

import spacy
from docx import Document as DocxDocument
from PyPDF2 import PdfReader
from textblob import TextBlob
from transformers import pipeline

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Max

from ..models import (
    Document, DocumentContent, DocumentVersion, Suggestion,
    DocumentStatus, Template
)

logger = logging.getLogger(__name__)

# Load NLP models
nlp = spacy.load("en_core_web_sm")  # spaCy for grammar and style analysis
text_generation_pipeline = pipeline("text-generation", model="gpt-2")  # Hugging Face for rewriting

class DocumentProcessor:
    """
    Service class to handle document processing and improvement.
    """

    @staticmethod
    def extract_text_from_file(document: Document) -> str:
        """
        Extract text from the uploaded document based on its file type.
        """
        file_path = document.original_file.path
        file_type = document.file_type

        try:
            if file_type == 'txt':
                with open(file_path, 'r') as file:
                    return file.read()
            elif file_type == 'docx':
                doc = DocxDocument(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            elif file_type == 'pdf':
                reader = PdfReader(file_path)
                return "\n".join([page.extract_text() for page in reader.pages])
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from document {document.id}: {e}")
            raise

    @staticmethod
    def analyze_grammar_and_style(text: str) -> List[Dict[str, Any]]:
        """
        Analyze the text for grammar and style issues using spaCy.
        """
        doc = nlp(text)
        suggestions = []

        for sent in doc.sents:
            # Example: Check for passive voice
            if any(token.dep_ == "nsubjpass" for token in sent):
                suggestions.append({
                    "original_text": sent.text,
                    "suggested_text": None,  # Placeholder for improved text
                    "improvement_type": "passive_voice",
                    "start_position": sent.start_char,
                    "end_position": sent.end_char,
                })

            # Example: Check for long sentences
            if len(sent) > 50:
                suggestions.append({
                    "original_text": sent.text,
                    "suggested_text": None,  # Placeholder for improved text
                    "improvement_type": "long_sentence",
                    "start_position": sent.start_char,
                    "end_position": sent.end_char,
                })

        return suggestions

    @staticmethod
    def rewrite_text(text: str) -> str:
        """
        Rewrite the text using a pre-trained language model (e.g., GPT-2).
        """
        try:
            rewritten_text = text_generation_pipeline(text, max_length=512, num_return_sequences=1)[0]['generated_text']
            return rewritten_text
        except Exception as e:
            logger.error(f"Error rewriting text: {e}")
            return text  # Fallback to original text

    @staticmethod
    def save_suggestions(document: Document, suggestions: List[Dict[str, Any]]) -> None:
        """
        Save improvement suggestions to the database.
        """
        for suggestion in suggestions:
            Suggestion.objects.create(
                document=document,
                original_text=suggestion["original_text"],
                suggested_text=suggestion["suggested_text"],
                improvement_type=suggestion["improvement_type"],
                start_position=suggestion["start_position"],
                end_position=suggestion["end_position"],
                is_accepted=None,  # Pending by default
            )

    @staticmethod
    def create_document_version(document: Document, content: str) -> DocumentVersion:
        """
        Create a new version of the document with improved content.
        """
        # Get the next version number
        latest_version = DocumentVersion.objects.filter(document=document).aggregate(Max('version_number'))
        version_number = latest_version['version_number__max'] + 1 if latest_version['version_number__max'] else 1

        return DocumentVersion.objects.create(
            document=document,
            content=content,
            version_number=version_number,
        )

    @transaction.atomic
    def process_document(self, document_id: UUID) -> None:
        """
        Process a document: extract text, analyze, rewrite, and save results.
        """
        document = Document.objects.get(id=document_id)

        try:
            # Step 1: Extract text
            document.status = DocumentStatus.PROCESSING
            document.save()

            text = self.extract_text_from_file(document)

            # Step 2: Save original content
            DocumentContent.objects.create(document=document, original_content=text)

            # Step 3: Analyze grammar and style
            suggestions = self.analyze_grammar_and_style(text)
            self.save_suggestions(document, suggestions)

            # Step 4: Rewrite text
            rewritten_text = self.rewrite_text(text)

            # Step 5: Save improved version
            self.create_document_version(document, rewritten_text)

            # Step 6: Update document status
            document.status = DocumentStatus.COMPLETED
            document.save()

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            document.status = DocumentStatus.FAILED
            document.save()
            raise