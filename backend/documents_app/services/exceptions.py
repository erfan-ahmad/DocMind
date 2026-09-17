


class DocumentProcessingError(Exception):
    """خطای عمومی پردازش سند"""
    pass


class TextExtractionError(DocumentProcessingError):
    """خطا در استخراج متن"""
    pass


class UnsupportedFormatError(DocumentProcessingError):
    """فرمت پشتیبانی نمی‌شود"""
    pass