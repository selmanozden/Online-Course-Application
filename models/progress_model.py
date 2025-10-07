"""Progress tracking models."""
from django.db import models
from django.conf import settings
from .course_model import Course
from .content_model import Content


class Progress(models.Model):
    """Overall course progress tracking model."""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress',
        limit_choices_to={'role': 'STUDENT'},
        help_text='Student'
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='student_progress',
        help_text='Course'
    )
    
    total_time_spent_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Total time spent on course (minutes)'
    )
    
    last_accessed_content = models.ForeignKey(
        Content,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='last_accessed_by',
        help_text='Last accessed content'
    )
    
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        help_text='Last access time'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Student notes for this course'
    )
    
    class Meta:
        db_table = 'progress'
        verbose_name = 'Progress'
        verbose_name_plural = 'Progress'
        unique_together = [['student', 'course']]
        ordering = ['-last_accessed_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} progress"


class ContentProgress(models.Model):
    """Individual content item progress tracking."""
    
    progress = models.ForeignKey(
        Progress,
        on_delete=models.CASCADE,
        related_name='content_progress',
        help_text='Overall progress record'
    )
    
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='student_progress',
        help_text='Content item'
    )
    
    is_completed = models.BooleanField(
        default=False,
        help_text='Has student completed this content'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Completion date'
    )
    
    time_spent_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Time spent on this content (minutes)'
    )
    
    # For video content
    video_progress_seconds = models.PositiveIntegerField(
        default=0,
        help_text='Video playback position (seconds)'
    )
    
    video_watched_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='Percentage of video watched'
    )
    
    # For document content
    last_page_viewed = models.PositiveIntegerField(
        default=0,
        help_text='Last page viewed in document'
    )
    
    attempts_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of attempts (for quiz content)'
    )
    
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        help_text='Last time content was accessed'
    )
    
    class Meta:
        db_table = 'content_progress'
        verbose_name = 'Content Progress'
        verbose_name_plural = 'Content Progress'
        unique_together = [['progress', 'content']]
        ordering = ['content__order']
    
    def __str__(self):
        return f"{self.progress.student.username} - {self.content.title}"
    
    def mark_completed(self):
        """Mark content as completed."""
        from django.utils import timezone
        from .enrollment_model import Enrollment
        
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
        
        # Update enrollment progress
        enrollment = Enrollment.objects.filter(
            student=self.progress.student,
            course=self.progress.course
        ).first()
        if enrollment:
            enrollment.update_progress()

