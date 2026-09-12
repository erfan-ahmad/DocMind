from rest_framework import serializers

from documents_app.models import Category,Document


class CategorySerilizer(serializers.ModelSerializer):


    class Meta:
        model = Category
        fields = ('id','name','description','created_at','owner')
        read_only_fields = ('id','created_at','owner')


class DocumentSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=255,
        min_length=3,
        allow_blank=False,
        error_messages={'blank':'فایل نمیتواند خالی باشد',
                          'min_length':'طول کاراکتر حداقل سه باشد' ,
                          'max_length':"طول بیشتر از حد مجاز است",
                        })
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages ={
         'required': 'ارسال فایل الزامی است.',
         'empty': 'فایل ارسال‌شده خالی است.',

     })

    class Meta:
        model = Document
        fields = [
            'id', 'owner', 'category', 'title', 'description',
            'file', 'file_name', 'file_size', 'mime_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at','file_name', 'file_size', 'mime_type']

    ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'docx']
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"فرمت فایل مجاز نیست. فرمت‌های مجاز: {', '.join(self.ALLOWED_EXTENSIONS)}")
        content_type = getattr(value, 'content_type', None)
        if content_type and content_type not in self.ALLOWED_MIME_TYPES:
            raise serializers.ValidationError("نوع MIME فایل مجاز نیست.")

        if value.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"حجم فایل نباید بیشتر از {self.MAX_FILE_SIZE // (1024*1024)} مگابایت باشد."
            )

        return value

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("عنوان نمی‌تواند فقط فاصله باشد.")

        if Document.objects.filter(title__iexact=value).exists():
            raise serializers.ValidationError("این عنوان قبلاً استفاده شده است.")
        return value

    def validate_category(self, value):
        request = self.context['request']
        if value.owner != request.user:
            raise serializers.ValidationError("این دسته‌بندی متعلق به شما نیست.")
        return value

    def create(self, validated_data):
        file = validated_data.get('file')
        if file:
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
            validated_data['mime_type'] = file.content_type
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file = validated_data.get('file')
        if file:
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
            validated_data['mime_type'] = file.content_type
        return super().update(instance, validated_data)




