import os
import PyPDF2
from docx import Document
from rest_framework import serializers
from .models import DocumentVersion

class DocumentVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for DocumentVersion model
    """
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 
            'user', 
            'original_file', 
            'original_text',
            'improved_file', 
            'improved_text',
            'grammar_suggestions', 
            'style_suggestions', 
            'clarity_suggestions',
            'uploaded_at', 
            'processed_at', 
            'status'
        ]
        read_only_fields = ['id', 'processed_at', 'status']

class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for document upload
    """
    file = serializers.FileField()
    
    def validate_file(self, value):
        """
        Validate uploaded file
        """
        # Validate file type
        allowed_extensions = ['.docx', '.txt', '.pdf']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (e.g., max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size should not exceed 10MB")
        
        # Additional file type checks
        try:
            # Try to read the file to ensure it's not corrupted
            if ext == '.docx':
                doc = Document(value)
            elif ext == '.pdf':
                PyPDF2.PdfReader(value)
            elif ext == '.txt':
                # For txt, we'll just try to decode
                value.read().decode('utf-8')
        except Exception as e:
            raise serializers.ValidationError(f"Invalid or corrupted {ext} file: {str(e)}")
        
        # Reset file pointer
        value.seek(0)
        
        return value

class DocumentImprovementSerializer(serializers.Serializer):
    """
    Serializer for document improvement request
    """
    improvement_level = serializers.ChoiceField(
        choices=['basic', 'advanced', 'professional'], 
        default='basic'
    )
    focus_areas = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['grammar', 'style', 'clarity', 'vocabulary']
        ),
        required=False
    )