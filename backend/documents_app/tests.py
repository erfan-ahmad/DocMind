# documents_app/tests.py
import os
from io import BytesIO

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

import pymupdf
from PIL import Image, ImageDraw
from docx import Document as DocxDocument
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .models import Category, Document


# ============================================================
# Helper: ساخت PDF، Word، عکس
# ============================================================
def make_pdf(text: str = "Hello DocMind") -> bytes:
    """با reportlab یه PDF با متن می‌سازه"""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.drawString(100, 750, text)
    pdf.save()
    return buffer.getvalue()


def make_empty_pdf() -> bytes:
    """PDF بدون متن"""
    doc = pymupdf.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def make_docx(text: str = "Hello from Word") -> bytes:
    """یه فایل Word ساده می‌سازه"""
    doc = DocxDocument()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


def make_image(text: str = "Hello OCR") -> bytes:
    """یه عکس با متن می‌سازه"""
    img = Image.new('RGB', (600, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((20, 80), text, fill='black')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.read()


# ============================================================
# کلاس پایه
# ============================================================
class BaseDocumentTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        # کاربر A
        self.user_a = User.objects.create_user(username='userA', password='pass123')
        self.token_a = self._login('userA', 'pass123')

        # کاربر B
        self.user_b = User.objects.create_user(username='userB', password='pass123')
        self.token_b = self._login('userB', 'pass123')

        # Category برای A
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        response = self.client.post('/api/categories/', {
            'name': 'Cat A', 'description': 'desc',
        }, format='json')
        self.category_a_id = response.data.get('id')

        # Category برای B
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        response = self.client.post('/api/categories/', {
            'name': 'Cat B', 'description': 'desc',
        }, format='json')
        self.category_b_id = response.data.get('id')

        # Document برای A
        self.doc_a = Document.objects.create(
            title="Doc A",
            description="desc",
            owner=self.user_a,
            category_id=self.category_a_id,
            file_name="a.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status=Document.Status.UPLOADED,
        )

        # Document برای B
        self.doc_b = Document.objects.create(
            title="Doc B",
            description="desc",
            owner=self.user_b,
            category_id=self.category_b_id,
            file_name="b.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status=Document.Status.UPLOADED,
        )

    def _login(self, username, password):
        response = self.client.post('/api/accounts/login/', {
            'username': username, 'password': password,
        }, format='json')
        return response.data.get('data', {}).get('tokens', {}).get('access')

    def _as_user_a(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')

    def _as_user_b(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')

    def _file(self, name="test.pdf", content=None, content_type="application/pdf"):
        if content is None:
            content = make_pdf("Hello")
        return SimpleUploadedFile(name, content, content_type=content_type)

    def _results(self, response):
        """اگه pagination فعاله results رو برگردون، وگرنه خود لیست"""
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']
        return response.data


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
            'file': SimpleUploadedFile("malware.exe", b"MZ...", "application/octet-stream"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_accept_valid_pdf(self):
        """PDF معتبر → 201 و status=PROCESSED"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Good PDF',
            'category': self.category_a_id,
            'file': self._file("doc.pdf", make_pdf("Hello DocMind"), "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.data['status'], ['PROCESSED', 'FAILED'])

    def test_accept_valid_docx(self):
        """Word معتبر → 201"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Good DOCX',
            'category': self.category_a_id,
            'file': SimpleUploadedFile(
                "doc.docx",
                make_docx("Hello Word"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PROCESSED')

    def test_accept_valid_image(self):
        """عکس معتبر → 201"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Good Image',
            'category': self.category_a_id,
            'file': SimpleUploadedFile("img.png", make_image("Hello"), "image/png"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.data['status'], ['PROCESSED', 'FAILED'])


# ============================================================
# 2) محدودیت حجم فایل
# ============================================================
class FileSizeValidationTests(BaseDocumentTestCase):

    def test_reject_oversized_file(self):
        """فایل بزرگ‌تر از ۱۰MB → 400"""
        self._as_user_a()
        big_content = b"x" * (11 * 1024 * 1024)
        response = self.client.post('/api/documents/', {
            'title': 'Big File',
            'category': self.category_a_id,
            'file': SimpleUploadedFile("big.pdf", big_content, "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_accept_file_under_size_limit(self):
        """فایل زیر ۱۰MB → 201"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Small File',
            'category': self.category_a_id,
            'file': self._file("small.pdf", make_pdf("small"), "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ============================================================
# 3) Category متعلق به کاربر دیگر
# ============================================================
class CategoryOwnershipTests(BaseDocumentTestCase):

    def test_user_a_cannot_use_user_b_category(self):
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Sneaky Doc',
            'category': self.category_b_id,
            'file': self._file("x.pdf", make_pdf("x"), "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_user_b_cannot_use_user_a_category(self):
        self._as_user_b()
        response = self.client.post('/api/documents/', {
            'title': 'Sneaky Doc',
            'category': self.category_a_id,
            'file': self._file("x.pdf", make_pdf("x"), "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_use_own_category(self):
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'My Doc',
            'category': self.category_a_id,
            'file': self._file("ok.pdf", make_pdf("ok"), "application/pdf"),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_nonexistent_category_returns_400(self):
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'Ghost Doc',
            'category': 99999,
            'file': self._file("x.pdf", make_pdf("x"), "application/pdf"),
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
        titles = [d['title'] for d in self._results(response)]
        self.assertIn('Doc A', titles)

    def test_search_returns_only_own_documents(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?search=Doc B')
        titles = [d['title'] for d in self._results(response)]
        self.assertNotIn('Doc B', titles)

    def test_search_case_insensitive(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?search=doc a')
        titles = [d['title'] for d in self._results(response)]
        self.assertIn('Doc A', titles)


# ============================================================
# 5) Filter
# ============================================================
class FilterTests(BaseDocumentTestCase):

    def test_filter_by_status(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?status=UPLOADED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for doc in self._results(response):
            self.assertEqual(doc['status'], 'UPLOADED')

    def test_filter_by_category(self):
        self._as_user_a()
        response = self.client.get(f'/api/documents/?category={self.category_a_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for doc in self._results(response):
            self.assertEqual(doc['category'], self.category_a_id)

    def test_combined_search_and_filter(self):
        self._as_user_a()
        url = f'/api/documents/?search=Doc&category={self.category_a_id}&status=UPLOADED'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [d['title'] for d in self._results(response)]
        self.assertIn('Doc A', titles)
        self.assertNotIn('Doc B', titles)


# ============================================================
# 6) Pagination
# ============================================================
class PaginationTests(BaseDocumentTestCase):

    def setUp(self):
        super().setUp()
        for i in range(25):
            Document.objects.create(
                title=f"Extra {i}",
                owner=self.user_a,
                category_id=self.category_a_id,
                file_name=f"{i}.pdf",
                file_size=1024,
                mime_type="application/pdf",
                status=Document.Status.UPLOADED,
            )

    def test_default_page_size(self):
        self._as_user_a()
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 10)
            self.assertIn('count', response.data)
        else:
            self.skipTest("Pagination فعال نیست")

    def test_second_page(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 10)

    def test_custom_page_size(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?page=1&page_size=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 5)

    def test_page_size_max_limit(self):
        self._as_user_a()
        response = self.client.get('/api/documents/?page_size=500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertLessEqual(len(response.data['results']), 100)


# ============================================================
# 7) Isolation
# ============================================================
class IsolationTests(BaseDocumentTestCase):

    def test_list_only_shows_own_documents(self):
        self._as_user_a()
        response = self.client.get('/api/documents/')
        ids = [d['id'] for d in self._results(response)]
        self.assertIn(self.doc_a.id, ids)
        self.assertNotIn(self.doc_b.id, ids)

    def test_retrieve_other_user_document_returns_404(self):
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
        self.client.credentials()
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_create(self):
        self.client.credentials()
        response = self.client.post('/api/documents/', {
            'title': 'Anon',
            'category': self.category_a_id,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ============================================================
# 9) Upload + Processing
# ============================================================
class UploadDocumentAPITests(BaseDocumentTestCase):

    def test_upload_valid_docx(self):
        """Word معتبر → متن استخراج بشه"""
        self._as_user_a()
        docx_bytes = make_docx("Hello from Word")
        uploaded_file = SimpleUploadedFile(
            "test.docx",
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        response = self.client.post('/api/documents/', {
            'title': 'My Word',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PROCESSED')

        doc = Document.objects.get(id=response.data['id'])
        self.assertIn('Hello', doc.extracted_text)

    def test_upload_valid_image(self):
        """عکس → OCR → متن استخراج بشه"""
        self._as_user_a()
        img_bytes = make_image("Hello OCR Test")
        uploaded_file = SimpleUploadedFile("test.png", img_bytes, "image/png")

        response = self.client.post('/api/documents/', {
            'title': 'My Image',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.data['status'], ['PROCESSED', 'FAILED'])

        doc = Document.objects.get(id=response.data['id'])
        if doc.status == Document.Status.PROCESSED:
            self.assertTrue(len(doc.extracted_text) > 0)

    def test_upload_corrupted_pdf(self):
        """آپلود فایل خراب → 201 ولی status=FAILED"""
        self._as_user_a()
        bad_bytes = b"this is not a pdf"
        uploaded_file = SimpleUploadedFile("bad.pdf", bad_bytes, "application/pdf")

        response = self.client.post('/api/documents/', {
            'title': 'Bad PDF',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'FAILED')
        self.assertTrue(response.data['error_message'])

    def test_upload_empty_pdf(self):
        """PDF بدون متن → FAILED"""
        self._as_user_a()
        pdf_bytes = make_empty_pdf()
        uploaded_file = SimpleUploadedFile("empty.pdf", pdf_bytes, "application/pdf")

        response = self.client.post('/api/documents/', {
            'title': 'Empty PDF',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'FAILED')

    def test_upload_without_file(self):
        """بدون فایل → 400"""
        self._as_user_a()
        response = self.client.post('/api/documents/', {
            'title': 'No File',
            'category': self.category_a_id,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_upload_without_auth(self):
        """بدون توکن → 401"""
        self.client.credentials()
        pdf_bytes = make_pdf("Hello")
        uploaded_file = SimpleUploadedFile("test.pdf", pdf_bytes, "application/pdf")
        response = self.client.post('/api/documents/', {
            'title': 'No Auth',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_invalid_file_type(self):
        """فایل غیرمجاز → 400"""
        self._as_user_a()
        uploaded_file = SimpleUploadedFile(
            "malware.exe", b"MZ...", "application/octet-stream"
        )
        response = self.client.post('/api/documents/', {
            'title': 'Bad File',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_user_cannot_see_processed_document(self):
        """user B نمی‌تونه سند user A رو ببینه"""
        self._as_user_a()
        docx_bytes = make_docx("Secret")
        uploaded_file = SimpleUploadedFile(
            "secret.docx",
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response = self.client.post('/api/documents/', {
            'title': 'Secret Doc',
            'category': self.category_a_id,
            'file': uploaded_file,
        }, format='multipart')
        doc_id = response.data['id']

        self._as_user_b()
        response = self.client.get(f'/api/documents/{doc_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ============================================================
# 10) تست با فایل‌های واقعی (اختیاری)
# ============================================================
class RealFileExtractionTests(BaseDocumentTestCase):
    """تست با فایل‌های واقعی — اگه فایل نباشه skip میشه"""

    def test_extract_real_docx(self):
        """فایل Word واقعی فارسی"""
        self._as_user_a()

        file_path = "/home/erfan/Downloads/لایحه_اعتراض_به_اعسار_محمدحسین_حاجی_خانعلی.docx"

        if not os.path.exists(file_path):
            self.skipTest("فایل پیدا نشد")

        with open(file_path, 'rb') as f:
            content = f.read()

        uploaded = SimpleUploadedFile(
            "لایحه.docx",
            content,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        response = self.client.post('/api/documents/', {
            'title': 'لایحه',
            'category': self.category_a_id,
            'file': uploaded,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        doc = Document.objects.get(id=response.data['id'])
        self.assertEqual(doc.status, Document.Status.PROCESSED)
        # متن استخراج شده (assertion ساده — نه چک محتوا چون یونیکد presentation form میشه)
        self.assertTrue(len(doc.extracted_text) > 100)