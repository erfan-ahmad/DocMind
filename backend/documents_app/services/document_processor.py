from documents_app.models import Document
from pypdf import PdfReader

from .persian_cleaner import persian_claener

"""""lass DocumentProcessor:
    def __init__(self, document):
        self.document = document

    def process(self):
      self.document.status= Document.Status.PROCESSING
      self.document.save(update_fields=['status'])

      try:

         file = self.document.file
         file.seek(0)
         text_reader =  PdfReader(file)
         text_data = []
         for page in text_reader.pages:
             text_data.append(page.extract_text()or '')

         text = '\n'.join(text_data).strip()
         self.document.extracted_text = text
         self.document.status = Document.Status.PROCESSED
         self.document.save(update_fields=['status', 'extracted_text'])
      except Exception:
          self.document.status = Document.Status.FAILED
          self.document.save(update_fields=['status'])
          raise
"""""

import logging
from django.utils import timezone

from documents_app.models import Document,chunk as Chunk
from .extractors.pdf_extractor import extract_from_pdf
from .extractors.docx_extractor import extract_from_docx
from .extractors.image_extractor import extract_from_image
from .exceptions import TextExtractionError
from .persian_cleaner import PersianCleaner
from .chunker  import Chunker
logger = logging.getLogger(__name__)


class DocumentProcessor:

    def __init__(self, document):
        self.document = document

    def process(self):
        # ۱) PROCESSING
        self.document.status = Document.Status.PROCESSING
        self.document.error_message = ''
        self.document.save(update_fields=['status', 'error_message'])

        try:
            # ۲) استخراج متن
            text = self._extract_text()

            if not text:
                raise TextExtractionError("هیچ متنی استخراج نشد.")

            # ۳) PROCESSED
            self.document.extracted_text = text
            cleaned_text = PersianCleaner(self.document.extracted_text).clean()
            chunks = Chunker(cleaned_text).chunking()

            self.document.status = Document.Status.PROCESSED
            self.document.processed_at = timezone.now()
            self.document.save(update_fields=[
                'extracted_text', 'status', 'processed_at'
            ])
            self.document.chunks.all().delete()
            Chunk.objects.bulk_create([
                Chunk(document=self.document, text=t, index=i)
                for i, t in enumerate(chunks)
            ])

        except Exception as exc:
            # ۴) FAILED
            logger.exception("خطا در پردازش سند %s", self.document.id)
            self.document.status = Document.Status.FAILED
            self.document.error_message = str(exc)
            self.document.save(update_fields=['status', 'error_message'])

            raise

    def _extract_text(self) -> str:
        """تشخیص نوع فایل + انتخاب extractor مناسب"""
        file = self.document.file
        file.seek(0)
        file_bytes = file.read()

        mime = (self.document.mime_type or '').lower()
        name = (self.document.file_name or '').lower()

        # PDF
        if name.endswith('.pdf') or mime == 'application/pdf':
            return extract_from_pdf(file_bytes)

        # Word
        if name.endswith('.docx') or 'wordprocessingml' in mime:
            return extract_from_docx(file_bytes)

        # عکس
        if mime.startswith('image/') or any(
                name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']
        ):
            return extract_from_image(file_bytes)

        # ناشناخته → سعی کن به عنوان PDF
        try:
            return extract_from_pdf(file_bytes)
        except Exception:
            raise TextExtractionError(f"فرمت پشتیبانی نمی‌شود: {mime}")