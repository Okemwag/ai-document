import os
os.environ['DJANGO_TEST'] = 'True'

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import DocumentVersion
from ..serializers import DocumentVersionSerializer, DocumentUploadSerializer
from ..views import process_document

User = get_user_model()

class DocumentVersionSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

        self.sample_file = SimpleUploadedFile(
            "test.docx", 
            b"Test content", 
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        self.document = DocumentVersion.objects.create(
            user=self.user,
            original_file=self.sample_file,
            original_text="Sample text",
            status='processing'
        )

    def test_serializer_valid_data(self):
        serializer = DocumentVersionSerializer(instance=self.document)
        data = serializer.data

        self.assertEqual(data['id'], str(self.document.id))
        self.assertEqual(data['status'], 'processing')
        self.assertEqual(data['original_text'], 'Sample text')
        self.assertEqual(data['user'], self.user.id)

    def test_serializer_read_only_fields(self):
        data = {
            'id': self.document.id,
            'processed_at': '2025-01-01T00:00:00Z',
            'status': 'completed'
        }
        serializer = DocumentVersionSerializer(instance=self.document, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Read-only fields should NOT be updated
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'processing')

class DocumentUploadSerializerTest(TestCase):
    def test_valid_docx_file(self):
        file = SimpleUploadedFile("ada.docx", b"Test content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        data = {'file': file}
        serializer = DocumentUploadSerializer(data=data)

        doc_version = DocumentVersion.objects.create(
            user=User.objects.create_user(username='testuser', password='password'),
            original_file=file,
            status='processing'
        )
        process_document.delay(doc_version.id)

        self.assertTrue(DocumentVersion.objects.exists())
        self.assertEqual(DocumentVersion.objects.last().status, 'processing')   


    def test_valid_txt_file(self):
        file = SimpleUploadedFile("test.txt", b"Sample text content", content_type="text/plain")
        data = {'file': file}
        serializer = DocumentUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_file_type(self):
        file = SimpleUploadedFile("test.exe", b"Executable content", content_type="application/x-msdownload")
        data = {'file': file}
        serializer = DocumentUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Unsupported file type", str(serializer.errors))

    def test_file_size_too_large(self):
        file = SimpleUploadedFile("test.docx", b"A" * (11 * 1024 * 1024), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        data = {'file': file}
        serializer = DocumentUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("File size should not exceed 10MB", str(serializer.errors))

    def test_invalid_docx_file(self):
        file = SimpleUploadedFile("test.docx", b"Invalid content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        data = {'file': file}
        serializer = DocumentUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Invalid or corrupted .docx file", str(serializer.errors))

    def test_invalid_txt_file(self):
        file = SimpleUploadedFile("test.txt", b"\x00\x01\x02", content_type="text/plain")
        data = {'file': file}
        serializer = DocumentUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Invalid or corrupted .txt file", str(serializer.errors))
