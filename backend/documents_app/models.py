from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Document(models.Model):

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PROCESSING = "PROCESSING", "Processing"
        PROCESSED = "PROCESSED", "Processed"
        INDEXED = "INDEXED", "Indexed"
        FAILED = "FAILED", "Failed"

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    file = models.FileField(
        upload_to="documents/%Y/%m/%d"
    )

    file_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extracted_text = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return self.title








class chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE,related_name='chunks')
    text = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    index = models.PositiveIntegerField()
    class Meta:
        ordering = ['index']
        unique_together = (('document', 'index'),)