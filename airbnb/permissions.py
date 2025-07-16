from rest_framework import permissions


class IsHostOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.host == request.user and request.user.status == 'host'


class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.status == 'guest'
