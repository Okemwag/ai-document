import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class DocumentStatus(models.TextChoices):
    UPLOADED = 'uploaded', _('Uploaded')
    PROCESSING = 'processing', _('Processing')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')

class DocumentType(models.TextChoices):
    TXT = 'txt', _('Text')
    DOCX = 'docx', _('Word Document')
    PDF = 'pdf', _('PDF')

class Document(models.Model):
    """
    Model to store information about uploaded documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    original_file = models.FileField(upload_to='documents/original/')
    file_type = models.CharField(max_length=10, choices=DocumentType.choices)
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.UPLOADED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"
    
    class Meta:
        ordering = ['-created_at']

class DocumentContent(models.Model):
    """
    Model to store the extracted content from the document.
    """
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='content')
    original_content = models.TextField()
    
    def __str__(self):
        return f"Content for {self.document.title}"

class DocumentVersion(models.Model):
    """
    Model to store improved versions of the document.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    version_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['document', 'version_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Version {self.version_number} of {self.document.title}"

class Suggestion(models.Model):
    """
    Model to store improvement suggestions for a document.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='suggestions')
    original_text = models.TextField()
    suggested_text = models.TextField()
    improvement_type = models.CharField(max_length=50)  
    start_position = models.PositiveIntegerField()  
    end_position = models.PositiveIntegerField()
    is_accepted = models.BooleanField(null=True)  # null = pending, True/False = accepted/rejected
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_position']
    
    def __str__(self):
        return f"Suggestion for {self.document.title}: {self.improvement_type}"

class Template(models.Model):
    """
    Model to store document templates for exporting improved documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template_file = models.FileField(upload_to='templates/')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']