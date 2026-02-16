from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTeacherOrReadOnly(BasePermission):
    """
    Les enseignants peuvent tout modifier,
    les étudiants peuvent juste lire.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'teacher'


class IsOwnerOrReadOnly(BasePermission):
    """
    Les utilisateurs peuvent modifier uniquement leurs propres ressources.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTeacherOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'teacher' or request.user.is_superuser

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        # Si l'objet a un attribut 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Si l'objet a un attribut 'student'
        if hasattr(obj, 'student'):
            return obj.student == request.user
        
        # Si l'objet a un attribut 'teacher'
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        
        return False

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'teacher' or request.user.is_superuser

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser