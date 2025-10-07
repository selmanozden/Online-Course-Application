"""Custom validators for forms and models."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os


def validate_file_size(file, max_size_mb=10):
    """Validate file size."""
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _(f'File size cannot exceed {max_size_mb}MB. Your file is {file.size / (1024 * 1024):.2f}MB.')
        )


def validate_image_file(file):
    """Validate image file type and size."""
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if ext not in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed: %(extensions)s'),
                            params={'extensions': ', '.join(valid_extensions)})
    validate_file_size(file, max_size_mb=5)


def validate_video_file(file):
    """Validate video file type and size."""
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
    if ext not in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed: %(extensions)s'),
                            params={'extensions': ', '.join(valid_extensions)})
    validate_file_size(file, max_size_mb=500)


def validate_document_file(file):
    """Validate document file type and size."""
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.xlsx', '.xls']
    if ext not in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed: %(extensions)s'),
                            params={'extensions': ', '.join(valid_extensions)})
    validate_file_size(file, max_size_mb=50)


def validate_course_price(value):
    """Validate course price."""
    if value < 0:
        raise ValidationError(_('Price cannot be negative.'))
    if value > 10000:
        raise ValidationError(_('Price cannot exceed $10,000.'))


def validate_rating(value):
    """Validate rating value (1-5)."""
    if value < 1 or value > 5:
        raise ValidationError(_('Rating must be between 1 and 5.'))


def validate_percentage(value):
    """Validate percentage value (0-100)."""
    if value < 0 or value > 100:
        raise ValidationError(_('Percentage must be between 0 and 100.'))

