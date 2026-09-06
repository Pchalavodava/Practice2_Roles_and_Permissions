from rest_framework.permissions import BasePermission, SAFE_METHODS


class ResumePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.role:
            return False

        role_perms = user.role.permissions.values_list('codename', flat=True)

        if request.method in SAFE_METHODS:
            return 'view_resume' in role_perms
        elif request.method == 'POST':
            return 'add_resume' in role_perms
        elif request.method in ('PUT', 'PATCH'):
            return 'change_resume' in role_perms
        elif request.method == 'DELETE':
            return 'delete_resume' in role_perms

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role and user.role.name == 'admin':
            return True

        if user.role and user.role.name == 'hr':
            return request.method in SAFE_METHODS

        if user.role and user.role.name == 'candidate':
            return obj.user == user and request.method in ('GET', 'PUT', 'PATCH', 'DELETE')

        return False
