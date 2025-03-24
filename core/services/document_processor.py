from django.core.exceptions import ObjectDoesNotExist
from ..models import Document
from ..utils import read_file, validate_file

def create_document(user, file):
    """
    Create and save a new document.
    """
    validate_file(file)
    content = read_file(file)

    document = Document.objects.create(
        user=user,
        title=file.name,
        original_content=content
    )
    return document

def get_document(user, document_id):
    """
    Retrieve document details.
    """
    try:
        return Document.objects.get(id=document_id, user=user)
    except ObjectDoesNotExist:
        return None

def update_document_status(document, status, improved_content=None):
    """
    Update document status and optionally improved content.
    """
    document.status = status
    if improved_content:
        document.improved_content = improved_content
    document.save()
