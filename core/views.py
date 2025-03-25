from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Document, DocumentVersion
from .serializers import (
    DocumentSerializer,
    DocumentVersionSerializer,
    DocumentImprovementSerializer,
    DocumentExportSerializer
)
from .services import DocumentProcessingService
from .tasks import process_document
from .exporter import DocumentExporter

class DocumentUploadView(generics.CreateAPIView):
    """
    POST /upload
    Upload a document and initiate processing
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        
        # Process synchronously for small files (<1MB), async for larger
        if document.original_file.size < 1024 * 1024:
            service = DocumentProcessingService()
            result = service.process_document(document.original_file.path)
            if result['status'] == 'success':
                DocumentVersion.objects.create(
                    document=document,
                    version_type='improved',
                    content=result['paraphrased_text'],
                    suggestions=result['improvements']
                )
                document.status = 'completed'
                document.save()
        else:
            process_document.delay(document.id)
            document.status = 'processing'
            document.save()

        return document

class DocumentRetrieveView(generics.RetrieveAPIView):
    """
    GET /documents/{id}
    Retrieve document with all versions
    """
    queryset = Document.objects.prefetch_related('versions')
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), id=self.kwargs['id'])
        if obj.user != self.request.user:
            self.permission_denied(self.request)
        return obj

class DocumentImproveView(APIView):
    """
    POST /documents/{id}/improve
    Request additional improvements to a document
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        document = get_object_or_404(
            Document.objects.filter(user=request.user),
            id=self.kwargs['id']
        )
        
        serializer = DocumentImprovementSerializer(
            data=request.data,
            context={'document': document}
        )
        serializer.is_valid(raise_exception=True)

        # Initiate reprocessing
        process_document_task.delay(
            document.id,
            improvement_types=serializer.validated_data.get('improvement_types'),
            aggressiveness=serializer.validated_data.get('aggressiveness', 3)
        )

        return Response(
            {'status': 'processing_started', 'document_id': str(document.id)},
            status=status.HTTP_202_ACCEPTED
        )

class DocumentExportView(APIView):
    """
    POST /documents/{id}/export
    Export a document version with template
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        document = get_object_or_404(
            Document.objects.filter(user=request.user),
            id=self.kwargs['id']
        )
        
        serializer = DocumentExportSerializer(
            data=request.data,
            context={'document': document}
        )
        serializer.is_valid(raise_exception=True)

        # Generate export file
        exporter = DocumentExporter(**serializer.get_export_config())
        export_file = exporter.generate()

        return Response({
            'download_url': export_file.url,
            'expires_at': export_file.expiry.isoformat(),
            'format': serializer.validated_data['format']
        })

class DocumentStatusView(APIView):
    """
    GET /documents/{id}/status
    Check processing status
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        document = get_object_or_404(
            Document.objects.filter(user=request.user),
            id=self.kwargs['id']
        )
        
        return Response({
            'document_id': str(document.id),
            'status': document.status,
            'last_updated': document.updated_at,
            'versions': [
                {'type': v.version_type, 'created_at': v.created_at}
                for v in document.versions.all()
            ]
        })
    
class DocumentVersionRetrieveView(generics.RetrieveAPIView):
    """
    GET /documents/{id}/versions/{version_id}
    Retrieve a specific document version
    """
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'