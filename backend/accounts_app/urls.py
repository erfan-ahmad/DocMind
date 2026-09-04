from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    register_view,
    UserLoginApiView,
    ProfileView,
    AdminOnlyView,
    dashboard_view,
    public_view,
    UserDetailView
)

app_name = 'your_app_name'

urlpatterns = [
    # ============ عمومی (بدون احراز هویت) ============
    path('register/', register_view, name='register'),
    path('login/', UserLoginApiView.as_view(), name='login'),
    path('public/', public_view, name='public'),

    # ============ خصوصی (نیاز به احراز هویت) ============
    path('profile/', ProfileView.as_view(), name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),

    # ============ تازه‌سازی توکن ============
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]