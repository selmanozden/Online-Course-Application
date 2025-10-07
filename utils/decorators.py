"""Role-based access control decorators."""
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps


def role_required(*allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Usage: @role_required('STUDENT', 'TEACHER')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'role'):
                messages.error(request, 'Access denied. Invalid user role.')
                return redirect('home:index')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(request.user.get_dashboard_url())
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def student_required(view_func):
    """Decorator to restrict access to students only."""
    return role_required('STUDENT')(view_func)


def teacher_required(view_func):
    """Decorator to restrict access to teachers only."""
    return role_required('TEACHER')(view_func)


def admin_required(view_func):
    """Decorator to restrict access to admins only."""
    return role_required('ADMIN')(view_func)


def enrollment_required(view_func):
    """
    Decorator to check if student is enrolled in a course.
    Expects 'course_id' or 'slug' in kwargs.
    """
    @wraps(view_func)
    @login_required
    @student_required
    def _wrapped_view(request, *args, **kwargs):
        from models.course_model import Course
        from models.enrollment_model import Enrollment
        
        # Get course from kwargs
        course_id = kwargs.get('course_id') or kwargs.get('pk')
        slug = kwargs.get('slug')
        
        try:
            if course_id:
                course = Course.objects.get(id=course_id)
            elif slug:
                course = Course.objects.get(slug=slug)
            else:
                messages.error(request, 'Course not found.')
                return redirect('student:browse_courses')
            
            # Check enrollment
            enrollment = Enrollment.objects.filter(
                student=request.user,
                course=course,
                is_active=True
            ).first()
            
            if not enrollment:
                messages.error(request, 'You must be enrolled in this course to access its content.')
                return redirect('course:detail', slug=course.slug)
            
            # Add enrollment to request for easy access in view
            request.enrollment = enrollment
            
        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')
            return redirect('student:browse_courses')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def course_owner_required(view_func):
    """
    Decorator to check if teacher owns the course.
    Expects 'course_id' or 'slug' in kwargs.
    """
    @wraps(view_func)
    @login_required
    @teacher_required
    def _wrapped_view(request, *args, **kwargs):
        from models.course_model import Course
        
        # Get course from kwargs
        course_id = kwargs.get('course_id') or kwargs.get('pk')
        slug = kwargs.get('slug')
        
        try:
            if course_id:
                course = Course.objects.get(id=course_id)
            elif slug:
                course = Course.objects.get(slug=slug)
            else:
                messages.error(request, 'Course not found.')
                return redirect('teacher:my_courses')
            
            # Check ownership
            if course.teacher != request.user:
                messages.error(request, 'You do not have permission to modify this course.')
                return redirect('teacher:my_courses')
            
            # Add course to request for easy access in view
            request.course = course
            
        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')
            return redirect('teacher:my_courses')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

