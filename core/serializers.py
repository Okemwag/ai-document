import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from PyPDF2 import PdfReader

from .models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for DocumentVersion with:
    - Content validation
    - Secure file handling
    - Dynamic field selection
    """
    class Meta:
        model = DocumentVersion
        fields = [
            'id',
            'version_type',
            'content',
            'file',
            'suggestions',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'file': {'required': False},
            'suggestions': {'required': False}
        }

    def validate_version_type(self, value):
        """Ensure version_type is valid and matches document state"""
        document = self.context.get('document')
        if document and value == 'original' and document.versions.filter(version_type='original').exists():
            raise serializers.ValidationError("Original version already exists")
        return value

    def validate(self, data):
        """Cross-field validation"""
        if not data.get('content') and not data.get('file'):
            raise serializers.ValidationError("Either content or file must be provided")
        return data

    def create(self, validated_data):
        """Handle file and content processing"""
        file_obj = validated_data.pop('file', None)
        if file_obj:
            validated_data['content'] = self._extract_file_content(file_obj)
        
        return super().create(validated_data)

    def _extract_file_content(self, file):
        """Extract text content from uploaded file"""
        # Implement file content extraction (e.g., using python-docx for .docx)
        try:
            if file.name.endswith('.txt'):
                return file.read().decode('utf-8')
            elif file.name.endswith('.docx'):
                from docx import Document
                doc = Document(file)
                return "\n".join([para.text for para in doc.paragraphs])
            elif file.name.endswith('.pdf'):
                reader = PdfReader(file)
                raw_content = "\n".join([page.extract_text() for page in reader.pages])
                return raw_content
            else:
                raise serializers.ValidationError("Unsupported file format")
        except Exception as e:
            raise serializers.ValidationError(f"File processing failed: {str(e)}")


class DocumentSerializer(serializers.ModelSerializer):
    """
    Comprehensive Document serializer with:
    - Nested version handling
    - File upload validation
    - Status transitions
    """
    versions = DocumentVersionSerializer(many=True, read_only=True)
    original_file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['docx', 'txt', 'pdf'])],
        write_only=True,
        required=True
    )

    class Meta:
        model = Document
        fields = [
            'id',
            'user',
            'title',
            'original_file',
            'status',
            'uploaded_at',
            'versions'
        ]
        read_only_fields = ['id', 'user', 'uploaded_at', 'status', 'versions']
        extra_kwargs = {
            'title': {'required': False}
        }

    def validate(self, data):
        """Validate document before creation"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            data['user'] = request.user
        
        if not data.get('title') and 'original_file' in data:
            data['title'] = data['original_file'].name
        
        return data

    def create(self, validated_data):
        """Create document with initial version"""
        file_obj = validated_data.pop('original_file')
        document = Document.objects.create(**validated_data)
        
        # Create original version
        DocumentVersion.objects.create(
            document=document,
            version_type='original',
            file=file_obj,
            content=DocumentVersionSerializer()._extract_file_content(file_obj)
        )
        
        return document

    def update(self, instance, validated_data):
        """Handle status transitions"""
        new_status = validated_data.get('status')
        if new_status and new_status != instance.status:
            self._validate_status_transition(instance.status, new_status)
        
        return super().update(instance, validated_data)

    def _validate_status_transition(self, old_status, new_status):
        """Ensure valid workflow progression"""
        valid_transitions = {
            'pending': ['processing', 'failed'],
            'processing': ['completed', 'failed'],
            'completed': [],
            'failed': ['pending']
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            raise serializers.ValidationError(
                f"Invalid status transition from {old_status} to {new_status}"
            )


class DocumentImprovementSerializer(serializers.Serializer):
    """
    Custom serializer for document improvement requests
    """
    document_id = serializers.UUIDField()
    improvement_types = serializers.MultipleChoiceField(
        choices=['grammar', 'style', 'clarity'],
        required=False
    )
    aggressiveness = serializers.IntegerField(
        min_value=1,
        max_value=5,
        default=3
    )

    def validate_document_id(self, value):
        """Verify document exists and is processable"""
        try:
            document = Document.objects.get(pk=value)
            if document.status != 'completed':
                raise serializers.ValidationError("Document must be in completed state")
            return document
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document not found")


class DocumentExportSerializer(serializers.Serializer):
    """
    Comprehensive serializer for document export operations with:
    - Template validation
    - Version verification
    - Export configuration options
    """
    document_id = serializers.UUIDField(
        required=True,
        help_text="UUID of the document to export"
    )
    version_type = serializers.ChoiceField(
        choices=DocumentVersion.VERSION_TYPES,
        default='improved',
        help_text="Which version to export (original/improved/exported)"
    )
    template_name = serializers.CharField(
        max_length=100,
        default='default',
        help_text="Name of the template to use (without .docx extension)"
    )
    format = serializers.ChoiceField(
        choices=[('docx', 'Word Document'), ('pdf', 'PDF')],
        default='docx',
        required=False,
        help_text="Output file format"
    )
    include_comments = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Whether to include improvement suggestions as comments"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_templates = self._get_available_templates()

    def validate_document_id(self, value):
        """Verify document exists and is exportable"""
        try:
            document = Document.objects.get(pk=value)
            if document.status != 'completed':
                raise ValidationError("Document must be in completed state before export")
            return value
        except Document.DoesNotExist:
            raise ValidationError("Document not found")

    def validate_template_name(self, value):
        """Validate template exists"""
        if value not in self.available_templates:
            raise ValidationError(
                f"Template '{value}' not found. Available templates: {', '.join(self.available_templates)}"
            )
        return value

    def validate(self, data):
        """Verify the specified version exists"""
        try:
            version = DocumentVersion.objects.get(
                document_id=data['document_id'],
                version_type=data['version_type']
            )
            data['version'] = version
            return data
        except DocumentVersion.DoesNotExist:
            raise ValidationError(
                f"{data['version_type']} version not found for document"
            )

    def _get_available_templates(self):
        """Discover available templates in templates directory"""
        template_dir = getattr(settings, 'DOCUMENT_TEMPLATES_DIR', 'document_templates')
        template_path = os.path.join(settings.BASE_DIR, template_dir)
        
        templates = []
        if os.path.exists(template_path):
            for f in os.listdir(template_path):
                if f.endswith('.docx'):
                    templates.append(f.replace('.docx', ''))
        return templates

    def get_export_config(self):
        """Return validated data in export-ready format"""
        return {
            'version': self.validated_data['version'],
            'template_path': os.path.join(
                settings.BASE_DIR,
                getattr(settings, 'DOCUMENT_TEMPLATES_DIR', 'document_templates'),
                f"{self.validated_data['template_name']}.docx"
            ),
            'output_format': self.validated_data['format'],
            'include_comments': self.validated_data['include_comments']
        }

    class Meta:
        ref_name = "DocumentExport"
        extra_kwargs = {
            'document_id': {'write_only': True},
            'version_type': {'write_only': True}
        }