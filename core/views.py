import os

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .document_template import apply_organization_template
from .models import DocumentVersion
from .serializers import (DocumentImprovementSerializer,
                          DocumentUploadSerializer, DocumentVersionSerializer)
from .services.document_processor import DocumentProcessor


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling document upload, processing, and improvements
    """
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'], serializer_class=DocumentUploadSerializer)
    def upload(self, request):
        """
        Handle document upload
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['file']
        
        # Create document version
        doc_version = DocumentVersion.objects.create(
            user=request.user,
            original_file=uploaded_file,
            status='processing'
        )
        
        # Trigger async processing
        process_document.delay(doc_version.id)
        
        return Response({
            'document_id': doc_version.id,
            'status': 'Processing started'
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['POST'], serializer_class=DocumentImprovementSerializer)
    def improve(self, request, pk=None):
        """
        Apply improvements to a specific document
        """
        document = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Trigger improvement processing
        improve_document.delay(
            document_id=pk, 
            improvement_level=serializer.validated_data.get('improvement_level'),
            focus_areas=serializer.validated_data.get('focus_areas', [])
        )
        
        return Response({
            'document_id': pk,
            'status': 'Improvement processing started'
        }, status=status.HTTP_202_ACCEPTED)

@shared_task
def process_document(document_id):
    """
    Celery task to process uploaded document
    """
    try:
        # Retrieve document
        doc_version = DocumentVersion.objects.get(id=document_id)
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Extract text from uploaded file
        doc_version.original_text = processor.extract_text_from_file(
            os.path.join(settings.MEDIA_ROOT, str(doc_version.original_file))
        )
        
        # Analyze document
        analysis_results = processor.suggest_improvements(doc_version.original_text)
        
        # Store suggestions
        doc_version.grammar_suggestions = analysis_results.get('grammar')
        doc_version.style_suggestions = analysis_results.get('style_suggestions')
        doc_version.clarity_suggestions = analysis_results.get('readability')
        
        doc_version.status = 'completed'
        doc_version.save()
        
        return str(doc_version.id)
    
    except Exception as e:
        # Update status to failed
        doc_version.status = 'failed'
        doc_version.save()
        raise

@shared_task
def improve_document(document_id, improvement_level='basic', focus_areas=None):
    """
    Celery task to improve document
    """
    try:
        # Retrieve document
        doc_version = DocumentVersion.objects.get(id=document_id)
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Get suggestions from previous processing
        suggestions = {
            'grammar': doc_version.grammar_suggestions,
            'style_suggestions': doc_version.style_suggestions
        }
        
        # Apply improvements
        improved_text = processor.apply_improvements(
            doc_version.original_text, 
            suggestions
        )
        
        # Save improved text
        doc_version.improved_text = improved_text
        
        # Apply organization template
        improved_file_path = apply_organization_template(
            improved_text, 
            f'{settings.MEDIA_ROOT}/improved_documents/{doc_version.id}.docx'
        )
        
        # Update document with improved file
        doc_version.improved_file = improved_file_path
        doc_version.processed_at = timezone.now()
        doc_version.save()
        
        return str(doc_version.id)
    
    except Exception as e:
        # Log error
        raise