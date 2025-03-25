from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import DocumentVersion
from unittest.mock import patch
from ..views import process_document, improve_document
from django.test import TestCase


User = get_user_model()

class DocumentViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

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

    def test_upload_valid_file(self):
        """
        Test uploading a valid file
        """
        url = reverse('document-upload')
        file = SimpleUploadedFile("test.docx", b"Test content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = self.client.post(url, {'file': file})
        self.assertTrue(DocumentVersion.objects.exists())
        self.assertEqual(DocumentVersion.objects.last().status, 'processing')

    def test_upload_invalid_file_type(self):
        """
        Test uploading an invalid file type
        """
        url = reverse('document-upload')
        file = SimpleUploadedFile("test.exe", b"Invalid content", content_type="application/x-msdownload")

        response = self.client.post(url, {'file': file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Unsupported file type', str(response.data))

    def test_upload_large_file(self):
        """
        Test file size limit exceeded
        """
        url = reverse('document-upload')
        file = SimpleUploadedFile("test.pdf", b"A" * (11 * 1024 * 1024), content_type="application/pdf") # 11MB

        response = self.client.post(url, {'file': file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('File size should not exceed 10MB', str(response.data))

    def test_improve_valid_request(self):
        """
        Test improving a document with valid data
        """
        url = reverse('document-improve', args=[self.document.id])
        data = {
            'improvement_level': 'advanced',
            'focus_areas': ['grammar', 'style']
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], 'Improvement processing started')

    def test_improve_invalid_focus_area(self):
        """
        Test improving a document with an invalid focus area
        """
        url = reverse('document-improve', args=[self.document.id])
        data = {
            'improvement_level': 'advanced',
            'focus_areas': ['invalid_area']
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invalid_area', str(response.data))

    def test_improve_invalid_improvement_level(self):
        """
        Test invalid improvement level
        """
        url = reverse('document-improve', args=[self.document.id])
        data = {
            'improvement_level': 'expert', # Invalid choice
            'focus_areas': ['grammar']
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expert', str(response.data))

    def test_upload_unauthenticated_request(self):
        """
        Test uploading a file without authentication
        """
        self.client.logout()
        url = reverse('document-upload')
        file = SimpleUploadedFile("test.docx", b"Test content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = self.client.post(url, {'file': file})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_improve_unauthenticated_request(self):
        """
        Test improving a file without authentication
        """
        self.client.logout()
        url = reverse('document-improve', args=[self.document.id])
        data = {
            'improvement_level': 'basic',
            'focus_areas': ['grammar']
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

