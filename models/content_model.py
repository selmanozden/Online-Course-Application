"""Content models for course materials."""
from django.db import models
from django.core.validators import FileExtensionValidator
from .course_model import Course


class Content(models.Model):
    """Base content model for course materials."""
    
    class ContentType(models.TextChoices):
        VIDEO = 'VIDEO', 'Video'
        DOCUMENT = 'DOCUMENT', 'Document'
        QUIZ = 'QUIZ', 'Quiz'
        TEXT = 'TEXT', 'Text'
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='contents',
        help_text='Associated course'
    )
    
    title = models.CharField(
        max_length=200,
        help_text='Content title'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Content description'
    )
    
    content_type = models.CharField(
        max_length=10,
        choices=ContentType.choices,
        help_text='Type of content'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order within course'
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Estimated time to complete (in minutes)'
    )
    
    is_preview = models.BooleanField(
        default=False,
        help_text='Can be previewed without enrollment'
    )
    
    is_mandatory = models.BooleanField(
        default=True,
        help_text='Must be completed to finish course'
    )
    
    text_content = models.TextField(
        blank=True,
        help_text='Text/HTML content (for TEXT type)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contents'
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'
        ordering = ['course', 'order', 'created_at']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    """Video content model."""
    
    content = models.OneToOneField(
        Content,
        on_delete=models.CASCADE,
        related_name='video',
        help_text='Associated content'
    )
    
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(['mp4', 'avi', 'mov', 'wmv'])],
        help_text='Video file',
        blank=True,
        null=True
    )
    
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text='External video URL (YouTube, Vimeo, etc.)'
    )
    
    thumbnail = models.ImageField(
        upload_to='videos/thumbnails/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text='Video thumbnail'
    )
    
    quality = models.CharField(
        max_length=10,
        blank=True,
        help_text='Video quality (e.g., 720p, 1080p)'
    )
    
    file_size_mb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='File size in MB'
    )
    
    class Meta:
        db_table = 'videos'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
    
    def __str__(self):
        return f"Video: {self.content.title}"


class Document(models.Model):
    """Document/file content model."""
    
    content = models.OneToOneField(
        Content,
        on_delete=models.CASCADE,
        related_name='document',
        help_text='Associated content'
    )
    
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'])],
        help_text='Document file'
    )
    
    file_size_mb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='File size in MB'
    )
    
    download_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of downloads'
    )
    
    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
    
    def __str__(self):
        return f"Document: {self.content.title}"

