from rest_framework import viewsets, permissions, parsers, filters
from rest_framework.views import APIView

from .services.document_processor import DocumentProcessor
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerilizer, DocumentSerializer
from .models import Category, Document
from .paginations import DocumentPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .serializers import AskSerializer
from .services.retriever import retrieve
from .services.llm import generate, build_prompt
from django.contrib.auth import get_user_model
User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerilizer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filter_fields = ('category', 'status')
    search_fields = ['title', 'description']
    pagination_class = DocumentPagination

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
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


class AskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data["query"]
        k = serializer.validated_data["k"]

        results = retrieve(query, user=request.user, k=k)
        if not results:
            return Response(
                {"query": query, "answer": "در اسناد موجود پاسخی یافت نشد.", "sources": []},
                status=status.HTTP_200_OK,
            )

        chunks = [r["chunk"] for r in results]
        prompt = build_prompt(query, chunks)
        answer = generate(prompt)

        sources = [
            {
                "document_id": r["chunk"].document_id,
                "document_title": r["chunk"].document.title,
                "chunk_index": r["chunk"].index,
                "score": r["score"],
                "text": r["chunk"].text,
            }
            for r in results
        ]

        return Response(
            {"query": query, "answer": answer, "sources": sources},
            status=status.HTTP_200_OK,
        )