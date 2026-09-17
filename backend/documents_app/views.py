from rest_framework import viewsets, permissions, parsers,filters
from .services.document_processor import DocumentProcessor
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerilizer, DocumentSerializer
from .models import Category, Document
from .paginations import  DocumentPagination


# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerilizer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]
    filter_fields = ('category','status')
    search_fields = ['title','description']
    pagination_class = DocumentPagination

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
        document = serializer.save(owner=self.request.user)
        try:
            DocumentProcessor(document).process()
        except Exception:
            pass
        document.refresh_from_db()