import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DocumentVersion(models.Model):
    """
    Model to store different versions of a document
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    original_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    original_text = models.TextField(blank=True, null=True)
    improved_file = models.FileField(upload_to='improved_documents/', blank=True, null=True)
    improved_text = models.TextField(blank=True, null=True)
    
    # Improvement metadata
    grammar_suggestions = models.JSONField(blank=True, null=True)
    style_suggestions = models.JSONField(blank=True, null=True)
    clarity_suggestions = models.JSONField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Document {self.id} - {self.uploaded_at}"
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Document Version'
        verbose_name_plural = 'Document Versions'