# documents_app/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Category, Document


class DocumentTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # ایجاد دو کاربر
        self.user_a = User.objects.create_user(
            username='userA',
            password='pass123'
        )
        self.user_b = User.objects.create_user(
            username='userB',
            password='pass123'
        )

        # لاگین userA
        response = self.client.post('/api/accounts/login/', {
            'username': 'userA',
            'password': 'pass123'
        }, format='json')

        self.token_a = response.data.get('data', {}).get('tokens', {}).get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')

        # ایجاد Category برای userA
        response = self.client.post('/api/categories/', {
            'name': 'Test Category',
            'description': 'Test Description'
        }, format='json')

        self.category_id = response.data.get('id')

        # ایجاد Document برای userA (مستقیم با مدل)
        self.document = Document.objects.create(
            title="Test Document",
            description="Test Description",
            owner=self.user_a,
            category_id=self.category_id,
            file_name="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="uploaded"
        )

        # لاگین userB
        response = self.client.post('/api/accounts/login/', {
            'username': 'userB',
            'password': 'pass123'
        }, format='json')

        self.token_b = response.data.get('data', {}).get('tokens', {}).get('access')

    # documents_app/tests.py

    def test_upload_document(self):
        """تست آپلود Document"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')

        uploaded_file = SimpleUploadedFile(
            "test_file.txt",
            b"test content",
            content_type="text/plain"
        )

        response = self.client.post('/api/documents/', {
            'title': 'New Document',
            'description': 'New Description',
            'category': self.category_id,
            'file': uploaded_file,
            'file_name': 'new_file.txt',
            'file_size': 1024,
            'mime_type': 'text/plain'
        }, format='multipart')  # ✅ این رو اضافه کن

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_own_document(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')

        response = self.client.patch(f'/api/documents/{self.document.id}/', {  # ✅ PATCH
            'title': 'Updated Document',
            'description': 'Updated Description',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_upload_document_with_invalid_category(self):
        """تست آپلود Document با Category نامعتبر"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')

        uploaded_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )

        response = self.client.post('/api/documents/', {
            'title': 'New Document',
            'category': 999,
            'file': uploaded_file,
            'file_name': 'test.txt',
            'file_size': 1024,
            'mime_type': 'text/plain'
        }, format='multipart')  # ✅ این رو اضافه کن

        self.assertIn(response.status_code, [400, 404])

    def test_user_b_upload_document_to_user_a_category(self):
        """تست آپلود Document توسط userB در Category کاربر A"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')

        uploaded_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )

        response = self.client.post('/api/documents/', {
            'title': 'UserB Document',
            'category': self.category_id,
            'file': uploaded_file,
            'file_name': 'test.txt',
            'file_size': 1024,
            'mime_type': 'text/plain'
        }, format='multipart')  # ✅ این رو اضافه کن

        self.assertIn(response.status_code, [400, 404])

