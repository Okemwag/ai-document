import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Any, Dict, List

from celery import shared_task
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

class DocumentProcessingService:
    """
    Hybrid document processing service that can be used both synchronously
    and asynchronously via Celery tasks.
    """
    
    def __init__(self):
        self._validate_environment()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _validate_environment(self):
        """Check required dependencies and environment variables"""
        try:
            import language_tool_python
            import spacy
            from transformers import pipeline
        except ImportError as e:
            raise ImportError(f"Missing required libraries: {e}")
        
        if not getattr(settings, 'DOCUMENT_PROCESSING_ENABLED', True):
            raise RuntimeError("Document processing is disabled in settings")

    @property
    @lru_cache(maxsize=1)
    def nlp(self):
        """Cache SpaCy model instance"""
        import spacy
        logger.info("Loading SpaCy model...")
        return spacy.load('en_core_web_sm')

    @property
    @lru_cache(maxsize=1)
    def grammar_tool(self):
        """Cache LanguageTool instance"""
        import language_tool_python
        logger.info("Loading LanguageTool...")
        return language_tool_python.LanguageTool('en-US')

    @property
    @lru_cache(maxsize=1)
    def paraphrase_model(self):
        """Cache paraphrase model"""
        from transformers import pipeline
        logger.info("Loading paraphrase model...")
        return pipeline("text2text-generation", 
                       model="t5-small",
                       device=0 if settings.USE_GPU else -1)

    def process_document(self, document_path: str, async_mode: bool = False) -> Dict[str, Any]:
        """
        Main processing method that can work in both sync and async modes
        
        Args:
            document_path: Path to the document file
            async_mode: If True, returns task ID instead of results
            
        Returns:
            Processing results or task ID
        """
        if async_mode:
            from .tasks import process_document_task
            task = process_document_task.delay(document_path)
            return {'task_id': task.id, 'status': 'queued'}
        
        try:
            content = self._read_and_clean(document_path)
            if not content:
                raise ValueError("Empty document content")
            
            # Parallel processing of different components
            with ThreadPoolExecutor() as executor:
                future_paraphrase = executor.submit(self._paraphrase_content, content)
                future_analysis = executor.submit(self._analyze_content, content)
                
                paraphrased = future_paraphrase.result()
                analysis = future_analysis.result()
            
            return {
                'status': 'success',
                'original_text': content,
                'paraphrased_text': paraphrased,
                'improvements': analysis
            }
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _read_and_clean(self, document_path: str) -> str:
        """Read and preprocess document content"""
        try:
            with default_storage.open(document_path, 'rb') as f:
                # Check file extension
                if document_path.lower().endswith('.pdf'):
                    reader = PdfReader(f)
                    raw_content = "\n".join([page.extract_text() for page in reader.pages])
                else:
                    # Handle other file types (txt, docx)
                    raw_content = f.read().decode('utf-8')
                
                return self._clean_text(raw_content)
        except Exception as e:
            logger.error(f"Failed to read document: {str(e)}")
            raise

    def _clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Implement your cleaning logic here
        return text.strip()

    def _paraphrase_content(self, text: str) -> str:
        """Handle document paraphrasing with chunking"""
        try:
            chunks = self._chunk_text(text)
            paraphrased = []
            
            for chunk in chunks:
                try:
                    result = self.paraphrase_model(
                        f"paraphrase: {chunk}",
                        max_length=100,
                        do_sample=True
                    )
                    paraphrased.append(result[0]['generated_text'])
                except Exception as e:
                    logger.warning(f"Paraphrase failed for chunk: {str(e)}")
                    paraphrased.append(chunk)  # Fallback to original
            
            return ' '.join(paraphrased)
        except Exception as e:
            logger.error(f"Paraphrasing failed: {str(e)}")
            raise

    def _chunk_text(self, text: str, max_words: int = 200) -> List[str]:
        """Split text into processing-friendly chunks"""
        words = text.split()
        return [' '.join(words[i:i+max_words]) 
               for i in range(0, len(words), max_words)]

    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Coordinate all analysis tasks"""
        with ThreadPoolExecutor() as executor:
            future_grammar = executor.submit(self._check_grammar, text)
            future_readability = executor.submit(self._assess_readability, text)
            future_style = executor.submit(self._check_style, text)
            
            return {
                'grammar': future_grammar.result(),
                'readability': future_readability.result(),
                'style': future_style.result()
            }

    def _check_grammar(self, text: str) -> Dict[str, Any]:
        """Grammar checking implementation"""
        try:
            matches = self.grammar_tool.check(text)
            return {
                'issues': len(matches),
                'suggestions': [{
                    'message': m.message,
                    'replacements': m.replacements[:5],  # Limit suggestions
                    'context': m.context
                } for m in matches]
            }
        except Exception as e:
            logger.error(f"Grammar check failed: {str(e)}")
            return {'error': str(e)}

    def _assess_readability(self, text: str) -> Dict[str, Any]:
        """Readability analysis"""
        try:
            doc = self.nlp(text)
            sentences = list(doc.sents)
            words = [token.text for token in doc if not token.is_punct]
            
            return {
                'sentence_count': len(sentences),
                'word_count': len(words),
                'avg_sentence_length': len(words)/len(sentences) if sentences else 0,
                'flesch_reading_ease': self._calculate_flesch_score(text)
            }
        except Exception as e:
            logger.error(f"Readability analysis failed: {str(e)}")
            return {'error': str(e)}

    def _calculate_flesch_score(self, text: str) -> float:
        """Calculate readability score"""
        # Implement Flesch-Kincaid or other metric
        return 0.0

    def _check_style(self, text: str) -> Dict[str, Any]:
        """Style analysis"""
        try:
            doc = self.nlp(text)
            return {
                'passive_voice': self._find_passive_voice(doc),
                'word_repetition': self._find_repetitions(doc),
                'complex_words': self._find_complex_terms(doc)
            }
        except Exception as e:
            logger.error(f"Style analysis failed: {str(e)}")
            return {'error': str(e)}

    def _find_passive_voice(self, doc) -> List[Dict]:
        """Passive voice detection"""
        # Implement using SpaCy patterns
        return []

    def _find_repetitions(self, doc) -> List[Dict]:
        """Word repetition analysis"""
        word_freq = {}
        for token in doc:
            if not token.is_stop and not token.is_punct:
                word_freq[token.lemma_] = word_freq.get(token.lemma_, 0) + 1
        return [{'word': w, 'count': c} for w, c in word_freq.items() if c > 3]

    def _find_complex_terms(self, doc) -> List[Dict]:
        """Complex terminology detection"""
        # Implement based on syllable count or domain-specific terms
        return []

