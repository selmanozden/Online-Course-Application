"""User model for role-based authentication."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    """Extended user model with role-based access control."""
    
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'
        ADMIN = 'ADMIN', 'Admin'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text='User role in the system'
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        help_text='User biography'
    )
    
    profile_picture = models.ImageField(
        upload_to='user_uploads/profiles/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text='User profile picture'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='Date of birth'
    )
    
    # Teacher-specific fields
    expertise = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Teacher expertise/specialization'
    )
    
    qualification = models.TextField(
        blank=True,
        null=True,
        help_text='Teacher qualifications'
    )
    
    # Student-specific fields
    education_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Student education level'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == self.Role.STUDENT
    
    @property
    def is_teacher(self):
        """Check if user is a teacher."""
        return self.role == self.Role.TEACHER
    
    @property
    def is_admin_role(self):
        """Check if user is an admin."""
        return self.role == self.Role.ADMIN
    
    def get_dashboard_url(self):
        """Get the appropriate dashboard URL based on role."""
        if self.is_student:
            return 'student:dashboard'
        elif self.is_teacher:
            return 'teacher:dashboard'
        elif self.is_admin_role:
            return 'admin:dashboard'
        return 'home:index'

