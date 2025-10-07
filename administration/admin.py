"""Admin configuration for Online Course Application models."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from models.user_model import User
from models.course_model import Course, Category
from models.content_model import Content, Video, Document
from models.exam_model import Exam, ExamResult
from models.question_model import Question, Answer
from models.enrollment_model import Enrollment, Certificate
from models.progress_model import Progress, ContentProgress


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'bio', 'profile_picture', 'phone_number', 'date_of_birth')
        }),
        ('Teacher Info', {
            'fields': ('expertise', 'qualification'),
            'classes': ('collapse',)
        }),
        ('Student Info', {
            'fields': ('education_level',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    list_display = ['title', 'teacher', 'category', 'level', 'status', 'price', 'rating', 'enrolled_count', 'created_at']
    list_filter = ['status', 'level', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['rating', 'total_ratings', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'teacher', 'category')
        }),
        ('Course Details', {
            'fields': ('level', 'status', 'price', 'duration_hours', 'max_students')
        }),
        ('Media', {
            'fields': ('thumbnail',)
        }),
        ('Additional Info', {
            'fields': ('prerequisites', 'learning_objectives', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('rating', 'total_ratings', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AnswerInline(admin.TabularInline):
    """Inline admin for Answer model."""
    model = Answer
    extra = 4
    fields = ['identifier', 'answer_text', 'is_correct', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model."""
    list_display = ['exam', 'question_type', 'marks', 'order']
    list_filter = ['question_type', 'exam']
    search_fields = ['question_text', 'exam__title']
    inlines = [AnswerInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin configuration for Exam model."""
    list_display = ['title', 'course', 'exam_type', 'is_published', 'duration_minutes', 'total_marks', 'passing_marks']
    list_filter = ['exam_type', 'is_published', 'is_required', 'created_at']
    search_fields = ['title', 'course__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    """Admin configuration for ExamResult model."""
    list_display = ['exam', 'student', 'attempt_number', 'status', 'score', 'percentage', 'is_passed', 'started_at']
    list_filter = ['status', 'is_passed', 'started_at']
    search_fields = ['exam__title', 'student__username']
    readonly_fields = ['started_at', 'submitted_at', 'graded_at']


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """Admin configuration for Content model."""
    list_display = ['title', 'course', 'content_type', 'order', 'is_mandatory', 'is_preview', 'created_at']
    list_filter = ['content_type', 'is_mandatory', 'is_preview', 'created_at']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for Video model."""
    list_display = ['content', 'quality', 'file_size_mb']
    search_fields = ['content__title']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model."""
    list_display = ['content', 'file_size_mb', 'download_count']
    search_fields = ['content__title']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Enrollment model."""
    list_display = ['student', 'course', 'status', 'progress_percentage', 'enrolled_at', 'is_active']
    list_filter = ['status', 'is_active', 'enrolled_at']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at', 'last_accessed_at']
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('student', 'course', 'status', 'is_active')
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'enrolled_at', 'completed_at', 'last_accessed_at')
        }),
        ('Payment', {
            'fields': ('payment_amount', 'payment_date')
        }),
        ('Review', {
            'fields': ('rating', 'review', 'review_date')
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin configuration for Certificate model."""
    list_display = ['certificate_number', 'enrollment', 'issued_date', 'is_verified']
    list_filter = ['is_verified', 'issued_date']
    search_fields = ['certificate_number', 'verification_code', 'enrollment__student__username']
    readonly_fields = ['certificate_number', 'verification_code', 'issued_date']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    """Admin configuration for Progress model."""
    list_display = ['student', 'course', 'total_time_spent_minutes', 'last_accessed_at']
    list_filter = ['last_accessed_at']
    search_fields = ['student__username', 'course__title']


@admin.register(ContentProgress)
class ContentProgressAdmin(admin.ModelAdmin):
    """Admin configuration for ContentProgress model."""
    list_display = ['progress', 'content', 'is_completed', 'time_spent_minutes', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['progress__student__username', 'content__title']


# Customize admin site
admin.site.site_header = "Online Course Application Admin"
admin.site.site_title = "Course Admin Portal"
admin.site.index_title = "Welcome to Course Administration"
