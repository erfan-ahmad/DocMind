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
        error_messages={
            'blank': 'عنوان سند نمی‌تواند خالی باشد.',
            'min_length': 'طول عنوان باید حداقل سه کاراکتر باشد.',
            'max_length': 'طول عنوان بیشتر از حد مجاز است.',
        }
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={
            'required': 'انتخاب دسته‌بندی الزامی است.',
            'null': 'دسته‌بندی نامعتبر است.',
        }
    )

    class Meta:
        model = Document
        fields = [
            'id', 'owner', 'category', 'title', 'description',
            'file', 'file_name', 'file_size', 'mime_type',
            'status', 'created_at', 'updated_at', 'error_message', 'extracted_text'
        ]
        read_only_fields = [
            'id', 'owner', 'created_at', 'updated_at', 'file_name',
            'file_size', 'mime_type', 'status', 'error_message', 'extracted_text'
        ]

    ALLOWED_EXTENSIONS = ['pdf', 'docx', 'jpg', 'jpeg', 'png']
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
    ]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"فرمت مجاز نیست. مجازها: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # چک حجم
        if value.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"حجم فایل نباید بیشتر از {self.MAX_FILE_SIZE // (1024 * 1024)}MB باشد."
            )

        return value

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("عنوان نمی‌تواند فقط فاصله باشد.")

        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        qs = Document.objects.filter(title__iexact=value)
        if user:
            qs = qs.filter(owner=user)

        # در صورت ویرایش (PUT/PATCH)، خود سند را مستثنی کن
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("شما قبلاً سندی با این عنوان ثبت کرده‌اید.")
        return value

    def validate_category(self, value):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
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






class AskSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=1000)
    k = serializers.IntegerField(default=5, min_value=1, max_value=20)