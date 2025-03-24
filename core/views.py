# apps/documents/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Document, DocumentVersion, Suggestion, Template
from .serializers import (
    DocumentSerializer, DocumentUploadSerializer, DocumentDetailSerializer,
    DocumentVersionSerializer, SuggestionSerializer, SuggestionActionSerializer,
    TemplateSerializer, DocumentExportSerializer
)
from .services.document_processor import DocumentProcessor

class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        elif self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer
    
    def perform_create(self, serializer):
        document = serializer.save()
        # Start async task to process the document
        DocumentProcessor.process_document(document.id)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process/re-process a document to generate improvement suggestions.
        """
        document = self.get_object()
        DocumentProcessor.process_document(document.id)
        return Response({'status': 'Processing started'}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        Export document with improvements to a template.
        """
        document = self.get_object()
        serializer = DocumentExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        template_id = serializer.validated_data.get('template_id')
        version_id = serializer.validated_data.get('version_id')
        
        # Get template (use default if not specified)
        if template_id:
            template = get_object_or_404(Template, id=template_id)
        else:
            template = Template.objects.filter(is_default=True).first()
            if not template:
                return Response(
                    {'error': 'No template specified and no default template found.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get document version
        if version_id:
            version = get_object_or_404(DocumentVersion, id=version_id, document=document)
        else:
            # Use latest version
            version = document.versions.order_by('-created_at').first()
            if not version:
                return Response(
                    {'error': 'No document versions available.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate exported document
        try:
            exported_file_url = DocumentProcessor.export_document(document.id, version.id, template.id)
            return Response({'url': exported_file_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing suggestions.
    """
    serializer_class = SuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Suggestion.objects.filter(document__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def action(self, request, pk=None):
        """
        Accept or reject a suggestion.
        """
        suggestion = self.get_object()
        serializer = SuggestionActionSerializer(suggestion, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # If accepting suggestion, update the latest document version
        if serializer.validated_data['is_accepted']:
            DocumentProcessor.apply_suggestion(suggestion.id)
        
        return Response(serializer.data)

class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing available templates.
    """
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

