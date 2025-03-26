import logging
from typing import Any, Dict, List

from celery import chain, group, shared_task
from celery.result import AsyncResult, GroupResult


from .models import Document, DocumentVersion
from .utils import clean_text, read_document_content
from .services import DocumentProcessingService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def read_document_content_task(self, file_path: str) -> Dict[str, Any]:
    """
    Celery task to read document content
    
    Args:
        file_path (str): Path to the document file

    Returns:
        Dict with document content and metadata
    """
    try:
        content = read_document_content(file_path)
        
        if not content:
            raise ValueError("Could not extract content from the document")
        
        return {
            'content': clean_text(content),
            'file_path': file_path
        }
    except Exception as e:
        self.retry(exc=e, countdown=2 ** self.request.retries)

@shared_task(bind=True)
def paraphrase_document_task(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to paraphrase document content
    
    Args:
        document_data (dict): Dictionary containing document content

    Returns:
        Dict with original and paraphrased content
    """
    try:
        from transformers import pipeline

        paraphraser = pipeline("text2text-generation", model="t5-small")
        
        # Break text into chunks to avoid model length limitations
        chunks = _split_text_into_chunks(document_data['content'])
        
        paraphrased_chunks = [
            _paraphrase_text_chunk(paraphraser, chunk) for chunk in chunks
        ]
        
        paraphrased_text = ' '.join(paraphrased_chunks)
        
        return {
            **document_data,
            'paraphrased_content': paraphrased_text
        }
    except Exception as e:
        logger.error(f"Paraphrasing failed: {str(e)}")
        return document_data

@shared_task(bind=True)
def analyze_document_task(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to analyze document content
    
    Args:
        document_data (dict): Dictionary containing document content

    Returns:
        Dict with analysis results
    """
    try:
        import language_tool_python
        import spacy

        # Load models
        nlp = spacy.load('en_core_web_sm')
        grammar_tool = language_tool_python.LanguageTool('en-US')
        
        # Grammar analysis
        grammar_analysis = _analyze_grammar(grammar_tool, document_data['content'])
        
        # Readability analysis
        readability = _analyze_readability(nlp, document_data['content'])
        
        # Style suggestions
        style_suggestions = _generate_style_suggestions(nlp, document_data['content'])
        
        return {
            **document_data,
            'improvements': {
                'grammar': grammar_analysis,
                'readability': readability,
                'style_suggestions': style_suggestions
            }
        }
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        return document_data

@shared_task
def save_document_version_task(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to save document version
    
    Args:
        document_data (dict): Dictionary containing processed document data

    Returns:
        Dict with saved document version details
    """
    try:
        # Retrieve the original document
        document = Document.objects.get(original_file=document_data['file_path'])
        
        # Create a new document version
        document_version = DocumentVersion.objects.create(
            document=document,
            version_type='improved',
            content=document_data.get('paraphrased_content', ''),
            suggestions=document_data.get('improvements', {})
        )
        
        return {
            'document_version_id': str(document_version.id),
            **document_data
        }
    except Exception as e:
        logger.error(f"Saving document version failed: {str(e)}")
        return document_data

def process_document(document_id: str) -> AsyncResult:
    """
    Orchestrate document processing workflow
    
    Args:
        document_id (str): ID of the document to process

    Returns:
        Celery AsyncResult for the entire processing workflow
    """
    # Retrieve the document
    document = Document.objects.get(id=document_id)
    
    # Create processing workflow using Celery's chain
    processing_workflow = chain(
        read_document_content_task.s(document.original_file.path),
        paraphrase_document_task.s(),
        analyze_document_task.s(),
        save_document_version_task.s()
    )
    
    # Execute the workflow
    return processing_workflow.apply_async()

# Helper functions for text processing
def _split_text_into_chunks(text: str, max_chunk_size: int = 200) -> List[str]:
    """Split text into manageable chunks"""
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        
        if len(current_chunk) >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def _paraphrase_text_chunk(paraphraser, chunk: str) -> str:
    """Paraphrase a text chunk"""
    try:
        response = paraphraser(
            f"paraphrase: {chunk}", 
            max_length=100, 
            do_sample=True
        )
        return response[0]['generated_text']
    except Exception:
        return chunk

def _analyze_grammar(grammar_tool, text: str) -> Dict[str, Any]:
    """Grammar analysis using LanguageTool"""
    matches = grammar_tool.check(text)
    
    grammar_suggestions = []
    for match in matches:
        grammar_suggestions.append({
            'message': match.message,
            'suggestions': match.replacements,
            'context': match.context,
            'offset': match.offset,
            'length': match.errorLength
        })
    
    return {
        'total_errors': len(grammar_suggestions),
        'suggestions': grammar_suggestions
    }

def _analyze_readability(nlp, text: str) -> Dict[str, float]:
    """Readability analysis using SpaCy"""
    doc = nlp(text)
    
    sentences = list(doc.sents)
    words = [token.text for token in doc if not token.is_punct]
    
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    return {
        'sentence_count': len(sentences),
        'word_count': len(words),
        'avg_sentence_length': avg_sentence_length,
        'avg_word_length': avg_word_length
    }

def _generate_style_suggestions(nlp, text: str) -> List[Dict[str, Any]]:
    """Generate style and clarity improvement suggestions"""
    import re
    
    style_suggestions = []
    
    # Passive voice detection
    passive_patterns = [
        r'\b(is|was|were|be|been)\b.*\bby\b',
        r'\b(is|was|were|be|been)\b.*\w+ed\b'
    ]
    
    for pattern in passive_patterns:
        passive_matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if passive_matches:
            style_suggestions.append({
                'type': 'Passive Voice',
                'suggestion': 'Consider rewriting sentences in active voice for clarity',
                'count': len(passive_matches)
            })
    
    # Repeated words detection
    doc = nlp(text)
    word_freq = {}
    for token in doc:
        if not token.is_stop and not token.is_punct:
            word_freq[token.text] = word_freq.get(token.text, 0) + 1
    
    repeated_words = [
        {'word': word, 'count': count} 
        for word, count in word_freq.items() 
        if count > 3
    ]
    
    if repeated_words:
        style_suggestions.append({
            'type': 'Word Repetition',
            'suggestion': 'Consider varying word choice to improve style',
            'repeated_words': repeated_words
        })
    
    return style_suggestions

# Bulk processing function
def process_multiple_documents(document_ids: List[str]) -> GroupResult:
    """
    Process multiple documents in parallel
    
    Args:
        document_ids (List[str]): List of document IDs to process

    Returns:
        Celery GroupResult for the processing tasks
    """
    # Create a group of processing tasks
    processing_tasks = group(
        process_document.s(doc_id) for doc_id in document_ids
    )
    
    # Execute the group of tasks
    return processing_tasks.apply_async()


@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_path):
    """Celery task wrapper for async processing"""
    service = DocumentProcessingService()
    try:
        return service.process_document(document_path, async_mode=False)
    except Exception as e:
        self.retry(exc=e, countdown=60)