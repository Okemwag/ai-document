from rest_framework import serializers
from .models import Document, DocumentContent, DocumentVersion, Suggestion, Template

class DocumentSerializer(serializers.ModelSerializer):
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'original_file', 'file_type', 'file_type_display', 
                  'status', 'status_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'file_type', 'status', 'created_at', 'updated_at', 'file_type_display', 'status_display']

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'original_file']
    
    def validate_original_file(self, value):
        # Get file extension
        file_extension = value.name.split('.')[-1].lower()
        
        # Check if the file type is supported
        if file_extension not in ['txt', 'docx', 'pdf']:
            raise serializers.ValidationError("Unsupported file type. Supported types are: txt, docx, pdf")
        
        # Check file size (limit to 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File too large. Size should not exceed 10MB.")
        
        return value
    
    def create(self, validated_data):
        file_extension = validated_data['original_file'].name.split('.')[-1].lower()
        validated_data['file_type'] = file_extension
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DocumentContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentContent
        fields = ['original_content']

class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ['id', 'content', 'version_number', 'created_at']
        read_only_fields = ['id', 'created_at']

class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'original_text', 'suggested_text', 'improvement_type', 
                  'start_position', 'end_position', 'is_accepted', 'created_at']
        read_only_fields = ['id', 'created_at']

class SuggestionActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'is_accepted']
        read_only_fields = ['id']

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'name', 'description', 'template_file', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

class DocumentDetailSerializer(serializers.ModelSerializer):
    content = DocumentContentSerializer(read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    suggestions = SuggestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'original_file', 'file_type', 'status', 
                  'created_at', 'updated_at', 'content', 'versions', 'suggestions']
        read_only_fields = ['id', 'file_type', 'status', 'created_at', 'updated_at']

class DocumentExportSerializer(serializers.Serializer):
    template_id = serializers.UUIDField(required=False)
    version_id = serializers.UUIDField(required=False)
    
    def validate(self, attrs):
        template_id = attrs.get('template_id')
        if template_id:
            try:
                Template.objects.get(id=template_id)
            except Template.DoesNotExist:
                raise serializers.ValidationError({"template_id": "Template not found."})
        
        version_id = attrs.get('version_id')
        if version_id:
            try:
                DocumentVersion.objects.get(id=version_id)
            except DocumentVersion.DoesNotExist:
                raise serializers.ValidationError({"version_id": "Document version not found."})
        
        return attrs