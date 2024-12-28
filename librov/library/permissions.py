from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
    
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only authors of a review to edit or delete it.
    Unauthenticated users can view reviews, but only authenticated users can create them.
    """

    def has_permission(self, request, view):
        # Allow viewing (GET, HEAD, OPTIONS) for any user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only authenticated users can create reviews
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow viewing for any user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the author of the review can edit or delete it
        return obj.user == request.user
        