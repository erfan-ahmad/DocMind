from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    """
    فقط کاربران فعال می‌توانند دسترسی داشته باشند
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)


class IsVerifiedUser(BasePermission):
    """
    فقط کاربرانی که ایمیل خود را تایید کرده‌اند
    """
    def has_permission(self, request, view):
        # فرض کنید یک فیلد is_email_verified در مدل کاربر دارید
        return bool(request.user and getattr(request.user, 'is_email_verified', False))


class IsOwner(BasePermission):
    """
    فقط صاحب شیء می‌تواند به آن دسترسی داشته باشد
    """
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id