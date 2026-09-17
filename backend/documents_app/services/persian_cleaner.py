import re
import unicodedata


class PersianCleaner:
    def __init__(self, text):
        self.text = text

    def clean(self):
        # ۱) نرمال‌سازی یونیکد (presentation form → normal form)
        text = unicodedata.normalize('NFKC', self.text)

        # ۲) فاصله‌های اضافه
        text = re.sub(r' +', ' ', text)

        # ۳) Enter های اضافه (بیشتر از ۲ تا → ۲ تا)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # ۴) فاصله اول/آخر خطوط
        text = '\n'.join(line.strip() for line in text.split('\n'))

        return text.strip()