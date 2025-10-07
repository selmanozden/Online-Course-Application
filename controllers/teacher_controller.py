"""Teacher controller for teacher-specific views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import Count, Avg
from utils.decorators import teacher_required, course_owner_required
from models.course_model import Course, Category
from models.content_model import Content, Video, Document
from models.exam_model import Exam, ExamResult
from models.question_model import Question, Answer
from models.enrollment_model import Enrollment
from models.user_model import User


@method_decorator([login_required, teacher_required], name='dispatch')
class TeacherDashboardView(ListView):
    """Teacher dashboard view."""
    template_name = 'teacher/dashboard.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(
            teacher=self.request.user
        ).annotate(
            student_count=Count('enrollments')
        ).order_by('-created_at')[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        # Statistics
        context['total_courses'] = Course.objects.filter(teacher=teacher).count()
        context['total_students'] = Enrollment.objects.filter(
            course__teacher=teacher
        ).values('student').distinct().count()
        context['published_courses'] = Course.objects.filter(
            teacher=teacher, 
            status='PUBLISHED'
        ).count()
        
        # Average rating
        courses = Course.objects.filter(teacher=teacher)
        if courses.exists():
            avg_rating = courses.aggregate(Avg('rating'))['rating__avg']
            context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        else:
            context['avg_rating'] = 0
        
        return context


@method_decorator([login_required, teacher_required], name='dispatch')
class MyCoursesView(ListView):
    """View all teacher's courses."""
    template_name = 'teacher/my_courses.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        return Course.objects.filter(
            teacher=self.request.user
        ).annotate(
            student_count=Count('enrollments')
        ).order_by('-created_at')


@method_decorator([login_required, teacher_required], name='dispatch')
class CreateCourseView(CreateView):
    """Create a new course."""
    model = Course
    template_name = 'teacher/create_course.html'
    fields = ['title', 'description', 'category', 'thumbnail', 'level', 
              'language', 'price', 'requirements', 'what_you_will_learn', 
              'is_featured']
    success_url = reverse_lazy('my_courses')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        form.instance.status = 'DRAFT'
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


@method_decorator([login_required, teacher_required, course_owner_required], name='dispatch')
class EditCourseView(UpdateView):
    """Edit an existing course."""
    model = Course
    template_name = 'teacher/edit_course.html'
    fields = ['title', 'description', 'category', 'thumbnail', 'level', 
              'language', 'price', 'requirements', 'what_you_will_learn', 
              'is_featured', 'status']
    slug_url_kwarg = 'course_slug'
    
    def get_success_url(self):
        return reverse_lazy('edit_course', kwargs={'course_slug': self.object.slug})
    
    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['contents'] = Content.objects.filter(
            course=self.object
        ).order_by('order')
        return context


@login_required
@teacher_required
@course_owner_required
def delete_course(request, course_slug):
    """Delete a course."""
    course = get_object_or_404(Course, slug=course_slug)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('my_courses')
    
    return render(request, 'teacher/delete_course_confirm.html', {'course': course})


@method_decorator([login_required, teacher_required], name='dispatch')
class StudentsListView(ListView):
    """View all enrolled students."""
    template_name = 'teacher/students_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20
    
    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        if course_slug:
            return Enrollment.objects.filter(
                course__slug=course_slug,
                course__teacher=self.request.user
            ).select_related('student', 'course').order_by('-enrolled_at')
        else:
            return Enrollment.objects.filter(
                course__teacher=self.request.user
            ).select_related('student', 'course').order_by('-enrolled_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs.get('course_slug')
        if course_slug:
            context['course'] = get_object_or_404(
                Course, 
                slug=course_slug, 
                teacher=self.request.user
            )
        return context


@method_decorator([login_required, teacher_required], name='dispatch')
class CreateExamView(CreateView):
    """Create a new exam."""
    model = Exam
    template_name = 'teacher/create_exam.html'
    fields = ['title', 'description', 'course', 'exam_type', 'duration_minutes', 
              'passing_score', 'max_attempts', 'is_published']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter courses to only show teacher's courses
        form.fields['course'].queryset = Course.objects.filter(
            teacher=self.request.user
        )
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Exam created successfully! Now add questions.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('edit_exam', kwargs={'exam_id': self.object.id})


@login_required
@teacher_required
def add_content(request, course_slug):
    """Add content to a course."""
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        # Get the next order number
        max_order = Content.objects.filter(course=course).count()
        
        if content_type == 'VIDEO':
            video_file = request.FILES.get('video_file')
            video_url = request.POST.get('video_url', '')
            duration = request.POST.get('duration', 0)
            
            Video.objects.create(
                course=course,
                title=title,
                description=description,
                content_type='VIDEO',
                order=max_order + 1,
                video_file=video_file,
                video_url=video_url,
                duration=duration
            )
        elif content_type == 'DOCUMENT':
            document_file = request.FILES.get('document_file')
            
            Document.objects.create(
                course=course,
                title=title,
                description=description,
                content_type='DOCUMENT',
                order=max_order + 1,
                document_file=document_file
            )
        else:
            Content.objects.create(
                course=course,
                title=title,
                description=description,
                content_type=content_type,
                order=max_order + 1
            )
        
        messages.success(request, 'Content added successfully!')
        return redirect('edit_course', course_slug=course_slug)
    
    return render(request, 'teacher/add_content.html', {'course': course})
