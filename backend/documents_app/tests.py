# documents_app/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from .models import Category, Document


class BaseDocumentTestCase(TestCase):
    """کلاس پایه برای setup مشترک"""

    def setUp(self):
        self.client = APIClient()

        # --- کاربر A ---
        self.user_a = User.objects.create_user(username='userA', password='pass123')
        self.token_a = self._login('userA', 'pass123')

        # --- کاربر B ---
        self.user_b = User.objects.create_user(username='userB', password='pass123')
        self.token_b = self._login('userB', 'pass123')

        # --- Category برای user A ---
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        response = self.client.post('/api/categories/', {
            'name': 'Cat A',
            'description': 'desc',
        }, format='json')
        self.category_a_id = response.data.get('id')

        # --- Category برای user B ---
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        response = self.client.post('/api/categories/', {
            'name': 'Cat B',
            'description': 'desc',
        }, format='json')
        self.category_b_id = response.data.get('id')

        # --- Document متعلق به user A ---
        self.doc_a = Document.objects.create(
            title="Doc A",
            description="desc",
            owner=self.user_a,
            category_id=self.category_a_id,
            file_name="a.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="uploaded",
        )

        # --- Document متعلق به user B ---
        self.doc_b = Document.objects.create(
            title="Doc B",
            description="desc",
            owner=self.user_b,
            category_id=self.category_b_id,
            file_name="b.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="uploaded",
        )

    def _login(self, username, password):
        response = self.client.post('/api/accounts/login/', {
            'username': username,
            'password': password,
        }, format='json')
        return response.data.get('data', {}).get('tokens', {}).get('access')

    def _as_user_a(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')

    def _as_user_b(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')

    def _file(self, name="test.txt", content=b"content", content_type="text/plain"):
        return SimpleUploadedFile(name, content, content_type=content_type)


# ============================================================
# 1) اعتبارسنجی نوع فایل
# ============================================================
class FileTypeValidationTests(BaseDocumentTestCase):

    def test_reject_invalid_file_extension(self):
        """پسوند غیرمجاز (exe) باید رد بشه"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Bad File',
            'category': self.category_a_id,
            'file': self._file("malware.exe", b"MZ...", "application/octet-stream"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_accept_valid_file_extension(self):
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Good File',
            'category': self.category_a_id,
            'file': self._file("doc.pdf", b"%PDF-1.4 ...", "application/pdf"),
        }, format='multipart')
        print("RESPONSE DATA:", response.data)  # ← این خط
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# ============================================================
# 2) محدودیت حجم فایل
# ============================================================
class FileSizeValidationTests(BaseDocumentTestCase):

    def test_reject_oversized_file(self):
        """فایل بزرگ‌تر از حد مجاز (۵MB) باید رد بشه"""
        self._as_user_a()
        big_content = b"x" * (6 * 1024 * 1024)  # 6MB
        response = self.client.post('/api/documents/', {
            'title': 'Big File',
            'category': self.category_a_id,
            'file': self._file("big.pdf", big_content, "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_accept_file_under_size_limit(self):
        """فایل زیر حد مجاز باید قبول بشه"""
        self._as_user_a()
        small_content = b"x" * (1024 * 1024)  # 1MB
        response = self.client.post('/api/documents/', {
            'title': 'Small File',
            'category': self.category_a_id,
            'file': self._file("small.pdf", small_content, "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ============================================================
# 3) Category متعلق به کاربر دیگر
# ============================================================
class CategoryOwnershipTests(BaseDocumentTestCase):

    def test_user_a_cannot_use_user_b_category(self):
        """user A نباید بتونه از category کاربر B استفاده کنه"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Sneaky Doc',
            'category': self.category_b_id,
            'file': self._file("x.pdf", b"%PDF", "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_user_b_cannot_use_user_a_category(self):
        """user B نباید بتونه از category کاربر A استفاده کنه"""
        self._as_user_b()
        response = self.client.post('/api/documents/', {
            'title': 'Sneaky Doc',
            'category': self.category_a_id,
            'file': self._file("x.pdf", b"%PDF", "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_use_own_category(self):
        """هر کاربر باید بتونه از category خودش استفاده کنه"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'My Doc',
            'category': self.category_a_id,
            'file': self._file("ok.pdf", b"%PDF", "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_nonexistent_category_returns_400(self):
        """category ناموجود باید 400 بده، نه 403"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Ghost Doc',
            'category': 99999,
            'file': self._file("x.pdf", b"%PDF", "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ============================================================
# 4) Search
# ============================================================
class SearchTests(BaseDocumentTestCase):

    def test_search_by_title(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?search=Doc A')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [d['title'] for d in response.data['results']]
        self.assertIn('Doc A', titles)

    def test_search_returns_only_own_documents(self):
        """سرچ نباید اسناد بقیه رو برگردونه"""
        self._as_user_a()
        response = self.client.get('/api/documents/?search=Doc B')
        titles = [d['title'] for d in response.data['results']]
        self.assertNotIn('Doc B', titles)

    def test_search_case_insensitive(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?search=doc a')
        titles = [d['title'] for d in response.data['results']]
        self.assertIn('Doc A', titles)


# ============================================================
# 5) Filter
# ============================================================
class FilterTests(BaseDocumentTestCase):

    def test_filter_by_status(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?status=uploaded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for doc in response.data['results']:
            self.assertEqual(doc['status'], 'uploaded')

    def test_filter_by_category(self):
        self._as_user_a()
        response = self.client.get(f'/api/documents/?category={self.category_a_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for doc in response.data['results']:
            self.assertEqual(doc['category'], self.category_a_id)

    def test_combined_search_and_filter(self):
        self._as_user_a()
        url = f'/api/documents/?search=Doc&category={self.category_a_id}&status=uploaded'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [d['title'] for d in response.data['results']]
        self.assertIn('Doc A', titles)
        self.assertNotIn('Doc B', titles)


# ============================================================
# 6) Pagination
# ============================================================
class PaginationTests(BaseDocumentTestCase):

    def setUp(self):
        super().setUp()
        # 25 تا داکیومنت اضافه برای user A
        for i in range(25):
            Document.objects.create(
                title=f"Extra {i}",
                owner=self.user_a,
                category_id=self.category_a_id,
                file_name=f"{i}.pdf",
                file_size=1024,
                mime_type="application/pdf",
                status="uploaded",
            )

    def test_default_page_size(self):
        """پیش‌فرض باید page_size=10 باشه"""
        self._as_user_a()
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)

    def test_second_page(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_custom_page_size(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?page=1&page_size=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_page_size_max_limit(self):
        """page_size نباید بیشتر از max_page_size بشه (100)"""
        self._as_user_a()
        response = self.client.get('/api/documents/?page_size=500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 100)


# ============================================================
# 7) Isolation — user A نباید به اسناد user B دسترسی داشته باشه
# ============================================================
class IsolationTests(BaseDocumentTestCase):

    def test_list_only_shows_own_documents(self):
        self._as_user_a()
        response = self.client.get('/api/documents/')
        ids = [d['id'] for d in response.data['results']]
        self.assertIn(self.doc_a.id, ids)
        self.assertNotIn(self.doc_b.id, ids)

    def test_retrieve_other_user_document_returns_404(self):
        """user A نباید بتونه سند user B رو ببینه"""
        self._as_user_a()
        response = self.client.get(f'/api/documents/{self.doc_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_other_user_document_returns_404(self):
        self._as_user_a()
        response = self.client.patch(f'/api/documents/{self.doc_b.id}/', {
            'title': 'Hacked',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_other_user_document_returns_404(self):
        self._as_user_a()
        response = self.client.delete(f'/api/documents/{self.doc_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_own_document(self):
        self._as_user_a()
        response = self.client.get(f'/api/documents/{self.doc_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Doc A')

    def test_delete_own_document(self):
        self._as_user_a()
        response = self.client.delete(f'/api/documents/{self.doc_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ============================================================
# 8) Unauthenticated
# ============================================================
class AuthTests(BaseDocumentTestCase):

    def test_unauthenticated_cannot_list(self):
        self.client.credentials()  # پاک کردن توکن
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_create(self):
        self.client.credentials()
        response = self.client.post('/api/documents/', {
            'title': 'Anon',
            'category': self.category_a_id,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
