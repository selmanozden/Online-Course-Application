"""Enrollment and Certificate models."""
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .course_model import Course


class Enrollment(models.Model):
    """Student course enrollment model."""
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        DROPPED = 'DROPPED', 'Dropped'
        SUSPENDED = 'SUSPENDED', 'Suspended'
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'},
        help_text='Enrolled student'
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text='Enrolled course'
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text='Enrollment status'
    )
    
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Enrollment date'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Course completion date'
    )
    
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='Course completion progress'
    )
    
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        help_text='Last time student accessed course'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Is enrollment active'
    )
    
    # Payment information
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Amount paid for enrollment'
    )
    
    payment_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Payment date'
    )
    
    # Rating
    rating = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Student rating (1-5)'
    )
    
    review = models.TextField(
        blank=True,
        help_text='Student review'
    )
    
    review_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Review submission date'
    )
    
    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = [['student', 'course']]
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
    
    def mark_completed(self):
        """Mark enrollment as completed."""
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.progress_percentage = 100.00
        self.save()
    
    def update_progress(self):
        """Calculate and update course progress."""
        from .progress_model import Progress
        
        # Get or create progress
        progress_obj, _ = Progress.objects.get_or_create(
            student=self.student,
            course=self.course
        )
        
        total_contents = self.course.contents.filter(is_mandatory=True).count()
        if total_contents == 0:
            self.progress_percentage = 100.00
        else:
            completed_contents = progress_obj.content_progress.filter(
                content__is_mandatory=True,
                is_completed=True
            ).count()
            self.progress_percentage = (completed_contents / total_contents) * 100
        
        # Check if all required exams are passed
        if self.progress_percentage == 100.00:
            required_exams = self.course.exams.filter(is_required=True)
            all_exams_passed = all(
                self.student.exam_results.filter(
                    exam=exam,
                    is_passed=True
                ).exists()
                for exam in required_exams
            )
            
            if all_exams_passed and self.status == self.Status.ACTIVE:
                self.mark_completed()
        
        self.save()


class Certificate(models.Model):
    """Course completion certificate model."""
    
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate',
        help_text='Associated enrollment'
    )
    
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique certificate number'
    )
    
    issued_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Certificate issue date'
    )
    
    certificate_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf'])],
        help_text='Generated certificate PDF'
    )
    
    verification_code = models.CharField(
        max_length=100,
        unique=True,
        help_text='Certificate verification code'
    )
    
    is_verified = models.BooleanField(
        default=True,
        help_text='Is certificate valid'
    )
    
    class Meta:
        db_table = 'certificates'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"Certificate {self.certificate_number} for {self.enrollment.student.username}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate certificate number
            import uuid
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:8].upper()
            self.certificate_number = f"CERT-{date_str}-{unique_id}"
        
        if not self.verification_code:
            # Generate verification code
            import hashlib
            import uuid
            code = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:20].upper()
            self.verification_code = code
        
        super().save(*args, **kwargs)

