"""Student controller for student-specific views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.db.models import Q, Avg, Count
from utils.decorators import student_required, enrollment_required
from models.course_model import Course, Category
from models.enrollment_model import Enrollment, Certificate
from models.exam_model import Exam, ExamResult
from models.progress_model import Progress, ContentProgress
from models.content_model import Content
from models.question_model import Question, Answer
from datetime import datetime


@method_decorator([login_required, student_required], name='dispatch')
class StudentDashboardView(ListView):
    """Student dashboard view."""
    template_name = 'student/dashboard.html'
    context_object_name = 'enrolled_courses'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__teacher').order_by('-enrolled_at')[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get overall statistics
        context['total_enrolled'] = Enrollment.objects.filter(student=user).count()
        context['completed_courses'] = Enrollment.objects.filter(
            student=user, 
            is_completed=True
        ).count()
        context['certificates_earned'] = Certificate.objects.filter(student=user).count()
        
        # Recent exam results
        context['recent_results'] = ExamResult.objects.filter(
            student=user
        ).select_related('exam', 'exam__course').order_by('-submitted_at')[:5]
        
        return context


@method_decorator([login_required, student_required], name='dispatch')
class BrowseCoursesView(ListView):
    """Browse all available courses."""
    model = Course
    template_name = 'student/browse_courses.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='PUBLISHED').select_related('teacher', 'category')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by level
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by price
        price = self.request.GET.get('price')
        if price == 'free':
            queryset = queryset.filter(price=0)
        elif price == 'paid':
            queryset = queryset.filter(price__gt=0)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


@method_decorator([login_required, student_required], name='dispatch')
class EnrolledCoursesView(ListView):
    """View enrolled courses."""
    template_name = 'student/enrolled_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 12
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__teacher').order_by('-enrolled_at')


@method_decorator([login_required, student_required, enrollment_required], name='dispatch')
class CourseContentView(DetailView):
    """View course content."""
    model = Course
    template_name = 'student/course_content.html'
    context_object_name = 'course'
    slug_url_kwarg = 'course_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        
        # Get enrollment
        context['enrollment'] = Enrollment.objects.get(
            student=user, 
            course=course
        )
        
        # Get course contents
        context['contents'] = Content.objects.filter(
            course=course
        ).order_by('order')
        
        # Get progress
        progress, _ = Progress.objects.get_or_create(
            student=user,
            course=course
        )
        context['progress'] = progress
        
        # Get completed contents
        completed_contents = ContentProgress.objects.filter(
            progress=progress,
            is_completed=True
        ).values_list('content_id', flat=True)
        context['completed_contents'] = completed_contents
        
        return context


@login_required
@student_required
def enroll_course(request, course_slug):
    """Enroll in a course."""
    course = get_object_or_404(Course, slug=course_slug, status='PUBLISHED')
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_content', course_slug=course_slug)
    
    # Create enrollment
    Enrollment.objects.create(
        student=request.user,
        course=course
    )
    
    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('course_content', course_slug=course_slug)


@method_decorator([login_required, student_required], name='dispatch')
class MyResultsView(ListView):
    """View exam results."""
    template_name = 'student/my_results.html'
    context_object_name = 'results'
    paginate_by = 20
    
    def get_queryset(self):
        return ExamResult.objects.filter(
            student=self.request.user
        ).select_related('exam', 'exam__course').order_by('-submitted_at')


@method_decorator([login_required, student_required], name='dispatch')
class TakeExamView(DetailView):
    """Take an exam."""
    model = Exam
    template_name = 'student/take_exam.html'
    context_object_name = 'exam'
    pk_url_kwarg = 'exam_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object
        
        # Get questions with answers
        context['questions'] = Question.objects.filter(
            exam=exam
        ).prefetch_related('answers').order_by('order')
        
        # Check previous attempts
        context['previous_attempts'] = ExamResult.objects.filter(
            student=self.request.user,
            exam=exam
        ).count()
        
        return context
    
    def post(self, request, *args, **kwargs):
        exam = self.get_object()
        
        # Check max attempts
        attempts = ExamResult.objects.filter(
            student=request.user,
            exam=exam
        ).count()
        
        if attempts >= exam.max_attempts:
            messages.error(request, 'Maximum attempts reached for this exam.')
            return redirect('student_dashboard')
        
        # Create exam result
        exam_result = ExamResult.objects.create(
            student=request.user,
            exam=exam,
            submitted_at=datetime.now()
        )
        
        # Process answers
        for question in exam.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                try:
                    selected_answer = Answer.objects.get(id=answer_id, question=question)
                    exam_result.answers.add(selected_answer)
                except Answer.DoesNotExist:
                    pass
        
        # Calculate result
        exam_result.calculate_result()
        
        messages.success(request, f'Exam submitted! Your score: {exam_result.score}%')
        return redirect('my_results')
