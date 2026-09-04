from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User

from .serializers import UserSerializer, UserLoginSerializer


# ============ ویوهای عمومی (بدون احراز هویت) ============

@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ همه می‌توانند ثبت‌نام کنند
def register_view(request):
    """
    ثبت‌نام کاربر جدید
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "success": True,
            "message": "User registered successfully",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        "success": False,
        "message": "Registration failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginApiView(APIView):
    """
    ورود کاربر و دریافت توکن‌های JWT
    """
    permission_classes = [AllowAny]  # ✅ همه می‌توانند لاگین کنند

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Login successful",
                "data": {
                    "tokens": {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'token_type': 'Bearer',
                    },
                    "user": {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    }
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Login failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ============ ویوهای خصوصی (نیاز به احراز هویت) ============

class ProfileView(APIView):
    """
    دریافت و به‌روزرسانی اطلاعات کاربر احراز هویت شده
    فقط کاربران احراز هویت شده می‌توانند دسترسی داشته باشند
    """
    authentication_classes = [JWTAuthentication]  # احراز هویت با JWT
    permission_classes = [IsAuthenticated]  # ✅ نیاز به احراز هویت

    def get(self, request):
        """دریافت اطلاعات کاربر"""
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        """به‌روزرسانی اطلاعات کاربر"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Profile update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class AdminOnlyView(APIView):
    """
    فقط ادمین‌ها می‌توانند به این ویو دسترسی داشته باشند
    """
    permission_classes = [IsAdminUser]  # ✅ فقط ادمین‌ها

    def get(self, request):
        return Response({
            "success": True,
            "message": "Welcome to admin panel!",
            "data": {
                "admin_panel": "This is admin only area",
                "total_users": User.objects.count(),
                "active_users": User.objects.filter(is_active=True).count(),
            }
        }, status=status.HTTP_200_OK)


# ============ ویوهای با تابع ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """
    داشبورد کاربر - فقط کاربران احراز هویت شده
    """
    user = request.user
    return Response({
        "success": True,
        "message": f"Welcome to your dashboard, {user.username}!",
        "data": {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_view(request):
    """
    ویو عمومی - بدون نیاز به احراز هویت
    """
    return Response({
        "success": True,
        "message": "This is a public endpoint",
        "data": {
            "public_info": "Anyone can access this",
            "timestamp": datetime.now().isoformat()
        }
    }, status=status.HTTP_200_OK)


# ============ ویو با Permission سفارشی ============

from rest_framework.permissions import BasePermission
from datetime import datetime


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission سفارشی: فقط صاحب شیء می‌تواند آن را تغییر دهد
    """

    def has_object_permission(self, request, view, obj):
        # خواندن برای همه مجاز است
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # نوشتن فقط برای صاحب شیء
        return obj.user == request.user


class UserDetailView(APIView):
    """
    نمایش و به‌روزرسانی اطلاعات یک کاربر خاص
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            self.check_object_permissions(request, user)  # بررسی permission
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)