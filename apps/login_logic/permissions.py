from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission


class FinalUserPermissions(BasePermission):
    protected_methods = ("GET", "PATCH", "PUT", "DELETE")

    def has_permission(self, request, _):
        method = request.method
        user = request.user

        if isinstance(user, AnonymousUser) and method in self.protected_methods:
            return False

        return True
