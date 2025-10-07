"""Admin controller for admin-specific views (custom admin panel)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta
from utils.decorators import admin_required
from models.user_model import User
from models.course_model import Course, Category
from models.enrollment_model import Enrollment, Certificate
from models.exam_model import Exam, ExamResult


@method_decorator([login_required, admin_required], name='dispatch')
class AdminDashboardView(TemplateView):
    """Admin dashboard with statistics."""
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Genel İstatistikler
        context['total_users'] = User.objects.count()
        context['total_students'] = User.objects.filter(role='STUDENT').count()
        context['total_teachers'] = User.objects.filter(role='TEACHER').count()
        context['total_courses'] = Course.objects.count()
        context['published_courses'] = Course.objects.filter(status='PUBLISHED').count()
        context['total_enrollments'] = Enrollment.objects.count()
        context['total_certificates'] = Certificate.objects.count()
        
        # Son 7 günlük istatistikler
        last_week = timezone.now() - timedelta(days=7)
        context['new_users_week'] = User.objects.filter(date_joined__gte=last_week).count()
        context['new_enrollments_week'] = Enrollment.objects.filter(enrolled_at__gte=last_week).count()
        
        # En popüler kurslar
        context['popular_courses'] = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5]
        
        # Son kayıtlar
        context['recent_users'] = User.objects.order_by('-date_joined')[:10]
        context['recent_enrollments'] = Enrollment.objects.select_related(
            'student', 'course'
        ).order_by('-enrolled_at')[:10]
        
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class UsersManagementView(TemplateView):
    """Manage all users."""
    template_name = 'admin/users_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtreleme
        role = self.request.GET.get('role', '')
        search = self.request.GET.get('search', '')
        
        users = User.objects.all().order_by('-date_joined')
        
        if role:
            users = users.filter(role=role)
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        context['users'] = users
        context['current_role'] = role
        context['current_search'] = search
        
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class CoursesManagementView(TemplateView):
    """Manage all courses."""
    template_name = 'admin/courses_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtreleme
        status = self.request.GET.get('status', '')
        category = self.request.GET.get('category', '')
        search = self.request.GET.get('search', '')
        
        courses = Course.objects.select_related('teacher', 'category').annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-created_at')
        
        if status:
            courses = courses.filter(status=status)
        
        if category:
            courses = courses.filter(category__slug=category)
        
        if search:
            courses = courses.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        context['courses'] = courses
        context['categories'] = Category.objects.all()
        context['current_status'] = status
        context['current_category'] = category
        context['current_search'] = search
        
        return context


@method_decorator([login_required, admin_required], name='dispatch')
class ReportsView(TemplateView):
    """Generate reports and analytics."""
    template_name = 'admin/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Kullanıcı istatistikleri
        context['user_stats'] = {
            'total': User.objects.count(),
            'students': User.objects.filter(role='STUDENT').count(),
            'teachers': User.objects.filter(role='TEACHER').count(),
            'admins': User.objects.filter(role='ADMIN').count(),
            'active': User.objects.filter(is_active=True).count(),
        }
        
        # Kurs istatistikleri
        context['course_stats'] = {
            'total': Course.objects.count(),
            'published': Course.objects.filter(status='PUBLISHED').count(),
            'draft': Course.objects.filter(status='DRAFT').count(),
            'pending': Course.objects.filter(status='PENDING').count(),
            'avg_rating': Course.objects.aggregate(Avg('rating'))['rating__avg'] or 0,
        }
        
        # Kayıt istatistikleri
        context['enrollment_stats'] = {
            'total': Enrollment.objects.count(),
            'completed': Enrollment.objects.filter(is_completed=True).count(),
            'in_progress': Enrollment.objects.filter(is_completed=False).count(),
        }
        
        # Sınav istatistikleri
        exam_results = ExamResult.objects.all()
        context['exam_stats'] = {
            'total_exams': Exam.objects.count(),
            'total_attempts': exam_results.count(),
            'avg_score': exam_results.aggregate(Avg('score'))['score__avg'] or 0,
            'pass_rate': (exam_results.filter(passed=True).count() / exam_results.count() * 100) if exam_results.count() > 0 else 0,
        }
        
        # Kategori bazlı istatistikler
        context['category_stats'] = Category.objects.annotate(
            course_count=Count('courses'),
            enrollment_count=Count('courses__enrollments')
        ).order_by('-enrollment_count')[:10]
        
        return context


@login_required
@admin_required
def toggle_user_status(request, user_id):
    """Toggle user active status."""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "aktif" if user.is_active else "pasif"
    messages.success(request, f'{user.username} kullanıcısı {status} duruma getirildi.')
    
    return redirect('users_management')


@login_required
@admin_required
def approve_course(request, course_id):
    """Approve a pending course."""
    course = get_object_or_404(Course, id=course_id)
    course.status = 'PUBLISHED'
    course.published_at = timezone.now()
    course.save()
    
    messages.success(request, f'{course.title} kursu onaylandı ve yayınlandı.')
    return redirect('courses_management')


@login_required
@admin_required
def reject_course(request, course_id):
    """Reject a pending course."""
    course = get_object_or_404(Course, id=course_id)
    course.status = 'DRAFT'
    course.save()
    
    messages.warning(request, f'{course.title} kursu reddedildi.')
    return redirect('courses_management')
