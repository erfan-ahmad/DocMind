from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)


class IsVerifiedUser(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'is_email_verified', False))


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
