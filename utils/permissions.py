"""Permission classes for REST API."""
from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """Permission class to check if user is a student."""
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                hasattr(request.user, 'role') and request.user.role == 'STUDENT')


class IsTeacher(permissions.BasePermission):
    """Permission class to check if user is a teacher."""
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                hasattr(request.user, 'role') and request.user.role == 'TEACHER')


class IsAdmin(permissions.BasePermission):
    """Permission class to check if user is an admin."""
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                hasattr(request.user, 'role') and request.user.role == 'ADMIN')


class IsCourseOwner(permissions.BasePermission):
    """Permission class to check if teacher owns the course."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (request.user and request.user.is_authenticated and 
                hasattr(obj, 'teacher') and obj.teacher == request.user)


class IsEnrolled(permissions.BasePermission):
    """Permission class to check if student is enrolled in the course."""
    
    def has_object_permission(self, request, view, obj):
        from models.enrollment_model import Enrollment
        if not request.user or not request.user.is_authenticated:
            return False
        course = getattr(obj, 'course', obj)
        return Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()

