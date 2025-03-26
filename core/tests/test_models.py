from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import now

from ..models import DocumentVersion

User = get_user_model()

class DocumentVersionModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a sample file
        self.sample_file = SimpleUploadedFile(
            "test.docx", 
            b"Test content", 
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # Create a DocumentVersion instance
        self.document = DocumentVersion.objects.create(
            user=self.user,
            original_file=self.sample_file,
            original_text="This is a test document.",
            status='processing'
        )

    def test_document_creation(self):
        """
        Test that the document is created correctly
        """
        self.assertEqual(self.document.user, self.user)
        self.assertEqual(self.document.original_text, "This is a test document.")
        self.assertEqual(self.document.status, 'processing')

    def test_document_default_status(self):
        """
        Test that default status is 'pending'
        """
        new_document = DocumentVersion.objects.create(
            user=self.user,
            original_file=self.sample_file
        )
        self.assertEqual(new_document.status, 'pending')

    def test_document_status_choices(self):
        """
        Test that status choices are enforced
        """
        self.document.status = 'completed'
        self.document.save()
        self.assertEqual(self.document.status, 'completed')

        with self.assertRaises(ValidationError):
            self.document.status = 'invalid_status'
            self.document.full_clean() 

    def test_file_upload(self):
        """
        Test that the file is uploaded and accessible
        """
        self.assertIsNotNone(self.document.original_file)
        self.assertTrue(self.document.original_file.name.startswith('uploads/'))

    def test_model_string_representation(self):
        """
        Test the string representation of the model
        """
        expected = f"Document {self.document.id} - {self.document.uploaded_at}"
        self.assertEqual(str(self.document), expected)

    def test_json_field_handling(self):
        """
        Test JSON field handling
        """
        self.document.grammar_suggestions = {"suggestion_1": "Fix punctuation"}
        self.document.save()
        self.assertEqual(self.document.grammar_suggestions["suggestion_1"], "Fix punctuation")

    def test_processed_at(self):
        """
        Test that processed_at is null by default and can be updated
        """
        self.assertIsNone(self.document.processed_at)
        self.document.processed_at = now()
        self.document.save()
        self.assertIsNotNone(self.document.processed_at)

    def test_ordering(self):
        """
        Test that documents are ordered by uploaded_at
        """
        doc1 = DocumentVersion.objects.create(user=self.user)
        doc2 = DocumentVersion.objects.create(user=self.user)
        docs = DocumentVersion.objects.all()
        self.assertEqual(docs[0], doc2)  # Newest first
        self.assertEqual(docs[1], doc1)
