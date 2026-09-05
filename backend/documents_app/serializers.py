from rest_framework import serializers

from documents_app.models import Category,Document


class CategorySerilizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','name','description','created_at','owner')
        read_only_fields = ('id','created_at','owner')


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'owner', 'category', 'title', 'description',
            'file', 'file_name', 'file_size', 'mime_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']