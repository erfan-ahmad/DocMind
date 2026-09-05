from rest_framework import viewsets, permissions, parsers
from rest_framework.exceptions import PermissionDenied

from .serializers import CategorySerilizer, DocumentSerializer
from .models import Category, Document


# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerilizer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        category_id = self.request.data.get('category')

        try:
            category = Category.objects.get(id=category_id, owner=self.request.user)
        except Category.DoesNotExist:  # ✅ اینجا : اضافه کن
            raise PermissionDenied("شما به این Category دسترسی ندارید")

        file = self.request.FILES.get('file')

        serializer.save(  # ✅ serializer_class.save نیست، serializer.save هست
            owner=self.request.user,
            category=category,
            file=file,
            file_name=file.name if file else '',
            file_size=file.size if file else 0,
            mime_type=file.content_type if file else ''
        )