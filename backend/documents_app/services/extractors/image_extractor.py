import logging
from io import BytesIO
from PIL import Image
import pytesseract

from .persian_utils import fix_persian_text
from ..exceptions import TextExtractionError

logger = logging.getLogger(__name__)


def extract_from_image(file_bytes: bytes) -> str:
    """OCR روی عکس (jpg, png)"""
    try:
        img = Image.open(BytesIO(file_bytes))
    except Exception as exc:
        logger.error("PIL خطا داد: %s", exc)
        raise TextExtractionError(f"خطا در باز کردن عکس: {exc}")

    # اگه عکس کوچیکه، بزرگش کن (OCR بهتر کار می‌کنه)
    if img.width < 1000:
        ratio = 1000 / img.width
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    try:
        text = pytesseract.image_to_string(img, lang='fas')
    except Exception as exc:
        logger.error("OCR خطا داد: %s", exc)
        raise TextExtractionError(f"خطا در OCR: {exc}")

    text = text.strip()

    if not text:
        raise TextExtractionError("هیچ متنی از عکس استخراج نشد.")

    return fix_persian_text(text)