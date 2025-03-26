import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Document(models.Model):
    """
    Main document model storing metadata and ownership
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255, blank=True)
    original_file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.get_status_display()}"


class DocumentVersion(models.Model):
    """
    Model to store different versions of a document with improvements
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="versions",
        null=True,
        blank=True,
    )

    VERSION_TYPES = [
        ("original", "Original"),
        ("improved", "Improved"),
        ("exported", "Exported"),
    ]
    version_type = models.CharField(
        max_length=20, choices=VERSION_TYPES, default="original"
    )

    content = models.TextField(default="No content Provided")
    file = models.FileField(upload_to="document_versions/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Improvement metadata
    suggestions = models.JSONField(
        default=dict, blank=True
    )  # Stores all types of suggestions

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document Version"
        verbose_name_plural = "Document Versions"
        unique_together = ["document", "version_type"]

    def __str__(self):
        return f"{self.document} - {self.get_version_type_display()}"
