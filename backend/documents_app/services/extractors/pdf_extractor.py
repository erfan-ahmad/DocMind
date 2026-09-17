import logging
from pdf2image import convert_from_bytes
import pytesseract
import pymupdf

from .persian_utils import fix_persian_text
from ..exceptions import TextExtractionError

logger = logging.getLogger(__name__)


def extract_from_pdf(pdf_bytes: bytes) -> str:
    """
    استخراج متن از PDF.

    جریان:
      1. تلاش با pymupdf (برای PDF متنی)
      2. اگه متن کم بود → OCR (برای PDF اسکن‌شده)
    """
    # مرحله ۱: pymupdf
    text = _extract_with_pymupdf(pdf_bytes)

    # اگه متن کافی بود → برگردون
    if text and len(text.strip()) > 50:
        logger.info("pymupdf موفق بود: %d کاراکتر", len(text))
        return fix_persian_text(text)

    # مرحله ۲: fallback به OCR
    logger.info("pymupdf متن کافی نداد، می‌رم سراغ OCR")
    text = _extract_with_ocr(pdf_bytes)

    if not text:
        raise TextExtractionError("هیچ متنی از PDF استخراج نشد.")

    return fix_persian_text(text)


def _extract_with_pymupdf(pdf_bytes: bytes) -> str:
    """استخراج متن از PDF متنی (سریع)"""
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []

        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)

        doc.close()
        return '\n'.join(text_parts).strip()

    except Exception as exc:
        logger.warning("pymupdf خطا داد: %s", exc)
        return ''


def _extract_with_ocr(pdf_bytes: bytes) -> str:
    """OCR برای PDF اسکن‌شده (کند)"""
    try:
        # PDF → عکس
        images = convert_from_bytes(pdf_bytes, dpi=300)
    except Exception as exc:
        logger.error("pdf2image خطا داد: %s", exc)
        raise TextExtractionError(f"خطا در تبدیل PDF به عکس: {exc}")

    text_parts = []
    for i, img in enumerate(images):
        try:
            # OCR روی هر صفحه
            page_text = pytesseract.image_to_string(img, lang='fas')
            text_parts.append(page_text)
        except Exception as exc:
            logger.warning("OCR صفحه %d خطا داد: %s", i, exc)

    return '\n'.join(text_parts).strip()