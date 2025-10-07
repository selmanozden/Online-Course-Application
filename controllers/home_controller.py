"""Home controller for public pages."""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Avg
from models.course_model import Course, Category
from models.user_model import User


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured courses
        context['featured_courses'] = Course.objects.filter(
            status='PUBLISHED',
            is_featured=True
        ).select_related('teacher', 'category')[:6]
        
        # Get popular courses (by enrollment count)
        context['popular_courses'] = Course.objects.filter(
            status='PUBLISHED'
        ).annotate(
            enrolled_count=Count('enrollments')
        ).order_by('-enrolled_count')[:6]
        
        # Get categories with course count
        context['categories'] = Category.objects.annotate(
            course_count=Count('courses')
        ).filter(course_count__gt=0)[:8]
        
        # Statistics
        context['total_courses'] = Course.objects.filter(status='PUBLISHED').count()
        context['total_students'] = User.objects.filter(role='STUDENT').count()
        context['total_teachers'] = User.objects.filter(role='TEACHER').count()
        
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'about.html'


class ContactView(TemplateView):
    """Contact page view."""
    template_name = 'contact.html'
