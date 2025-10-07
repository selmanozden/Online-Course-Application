"""Course and Category models."""
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    """Course category model."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Category name'
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text='URL-friendly category identifier'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Category description'
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Icon class (e.g., fa-code, fa-paint-brush)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """Course model."""
    
    class Level(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        ARCHIVED = 'ARCHIVED', 'Archived'
    
    title = models.CharField(
        max_length=200,
        help_text='Course title'
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text='URL-friendly course identifier'
    )
    
    description = models.TextField(
        help_text='Course description'
    )
    
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': 'TEACHER'},
        help_text='Course instructor'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
        help_text='Course category'
    )
    
    level = models.CharField(
        max_length=15,
        choices=Level.choices,
        default=Level.BEGINNER,
        help_text='Course difficulty level'
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text='Course publication status'
    )
    
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text='Course thumbnail image'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text='Course price (0 for free)'
    )
    
    duration_hours = models.PositiveIntegerField(
        default=0,
        help_text='Estimated course duration in hours'
    )
    
    max_students = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Maximum number of students (null for unlimited)'
    )
    
    prerequisites = models.TextField(
        blank=True,
        help_text='Course prerequisites'
    )
    
    learning_objectives = models.TextField(
        blank=True,
        help_text='What students will learn'
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text='Feature this course on homepage'
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Average course rating'
    )
    
    total_ratings = models.PositiveIntegerField(
        default=0,
        help_text='Total number of ratings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['teacher', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Check if course is published."""
        return self.status == self.Status.PUBLISHED
    
    @property
    def is_free(self):
        """Check if course is free."""
        return self.price == 0
    
    @property
    def enrolled_count(self):
        """Get number of enrolled students."""
        return self.enrollments.filter(is_active=True).count()
    
    @property
    def is_full(self):
        """Check if course has reached maximum capacity."""
        if self.max_students:
            return self.enrolled_count >= self.max_students
        return False
    
    def can_enroll(self):
        """Check if new students can enroll."""
        return self.is_published and not self.is_full

