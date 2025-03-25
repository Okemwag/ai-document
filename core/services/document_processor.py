import os
import re
from typing import Any, Dict, List
import chardet
import language_tool_python
import nltk
import spacy
from textblob import TextBlob
from docx import Document
from transformers import pipeline
from ..utils import (
    _read_docx,
    _read_pdf,
    _read_rtf,
    _read_txt
)

class DocumentProcessor:
    def __init__(self):
        # Load SpaCy English model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Grammar checker
        self.grammar_tool = language_tool_python.LanguageTool('en-US')
        
        # Paraphraser
        self.paraphrase_model = pipeline("text2text-generation", model="t5-small")
        
        # Download necessary NLTK resources
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        


    def correct_spelling(self, text):
        """Corrects spelling using TextBlob."""
        return str(TextBlob(text).correct())

    def paraphrase_text(self, text):
        """Paraphrases text using a T5 transformer model."""
        response = self.paraphrase_model(f"paraphrase: {text}", max_length=100, do_sample=True)
        return response[0]['generated_text']


    def analyze_grammar(self, text: str) -> Dict[str, Any]:
        """
        Perform grammar and style checks
        """
        # Check grammar using LanguageTool
        matches = self.grammar_tool.check(text)
        
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

    def analyze_readability(self, text: str) -> Dict[str, float]:
        """
        Analyze document readability
        """
        doc = self.nlp(text)
        
        # Calculate readability metrics
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

    def suggest_improvements(self, text: str) -> Dict[str, Any]:
        """
        Generate comprehensive document improvement suggestions
        """
        # Grammar analysis
        grammar_analysis = self.analyze_grammar(text)
        
        # Readability analysis
        readability = self.analyze_readability(text)
        
        # Style and clarity suggestions
        style_suggestions = self._generate_style_suggestions(text)
        
        return {
            'grammar': grammar_analysis,
            'readability': readability,
            'style_suggestions': style_suggestions
        }

    def _generate_style_suggestions(self, text: str) -> List[Dict[str, str]]:
        """
        Generate style and clarity improvement suggestions
        """
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
        doc = self.nlp(text)
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

    def apply_improvements(self, text: str, suggestions: Dict[str, Any]) -> str:
        """
        Apply NLP-based improvements to the document
        """
        # Apply grammar corrections
        improved_text = text
        
        # Sort grammar suggestions in reverse order to avoid offset issues
        grammar_suggestions = suggestions.get('grammar', {}).get('suggestions', [])
        sorted_suggestions = sorted(grammar_suggestions, key=lambda x: x['offset'], reverse=True)
        
        for suggestion in sorted_suggestions:
            if suggestion['suggestions']:
                # Replace text with the first suggested correction
                improved_text = (
                    improved_text[:suggestion['offset']] + 
                    suggestion['suggestions'][0] + 
                    improved_text[suggestion['offset'] + suggestion['length']:]
                )
        
        return improved_text