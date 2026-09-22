from django.urls import path ,include
from  rest_framework.routers import DefaultRouter
from  .views import AskView

from documents_app.views import CategoryViewSet, DocumentViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet,basename='categories')
router.register('documents', DocumentViewSet,basename='documents')
urlpatterns = [
    path('', include(router.urls)),
path("ask/", AskView.as_view(), name="ask"),

]



