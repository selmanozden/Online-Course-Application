"""Helper functions for the application."""
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io


def generate_certificate_pdf(enrollment):
    """Generate a PDF certificate for course completion."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Draw border
    p.setStrokeColor(colors.HexColor('#1a73e8'))
    p.setLineWidth(3)
    p.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)
    
    # Title
    p.setFont("Helvetica-Bold", 36)
    p.setFillColor(colors.HexColor('#1a73e8'))
    p.drawCentredString(width / 2, height - 120, "CERTIFICATE")
    
    p.setFont("Helvetica", 18)
    p.setFillColor(colors.HexColor('#333333'))
    p.drawCentredString(width / 2, height - 150, "OF COMPLETION")
    
    # Student name
    p.setFont("Helvetica-Bold", 24)
    student_name = enrollment.student.get_full_name() or enrollment.student.username
    p.drawCentredString(width / 2, height - 260, student_name)
    
    # Course title
    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 300, "has successfully completed the course")
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 335, enrollment.course.title)
    
    # Completion date
    p.setFont("Helvetica", 12)
    completion_date = enrollment.completed_at.strftime('%B %d, %Y') if enrollment.completed_at else timezone.now().strftime('%B %d, %Y')
    p.drawCentredString(width / 2, height - 380, f"Completed on: {completion_date}")
    
    # Certificate details
    from models.enrollment_model import Certificate
    try:
        certificate = enrollment.certificate
        p.setFont("Helvetica", 9)
        p.setFillColor(colors.gray)
        p.drawString(60, 80, f"Certificate No: {certificate.certificate_number}")
        p.drawString(60, 65, f"Verification Code: {certificate.verification_code}")
    except Certificate.DoesNotExist:
        pass
    
    # Instructor signature
    p.setFont("Helvetica-Bold", 12)
    instructor_name = enrollment.course.teacher.get_full_name() or enrollment.course.teacher.username
    p.line(width - 250, 150, width - 100, 150)
    p.setFont("Helvetica", 10)
    p.drawCentredString(width - 175, 135, instructor_name)
    p.drawCentredString(width - 175, 120, "Instructor")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return ContentFile(buffer.read())


def calculate_course_rating(course):
    """Calculate average course rating from enrollments."""
    enrollments_with_rating = course.enrollments.filter(rating__isnull=False)
    total_ratings = enrollments_with_rating.count()
    if total_ratings == 0:
        return 0.00, 0
    total_score = sum(e.rating for e in enrollments_with_rating)
    return round(total_score / total_ratings, 2), total_ratings


def update_course_rating(course):
    """Update course rating based on enrollments."""
    avg_rating, total = calculate_course_rating(course)
    course.rating = avg_rating
    course.total_ratings = total
    course.save(update_fields=['rating', 'total_ratings'])


def format_duration(minutes):
    """Format duration in minutes to human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h" if remaining_minutes == 0 else f"{hours}h {remaining_minutes}m"


def generate_unique_slug(model_class, title, max_length=200):
    """Generate a unique slug for a model instance."""
    from django.utils.text import slugify
    slug = slugify(title)[:max_length]
    unique_slug = slug
    counter = 1
    while model_class.objects.filter(slug=unique_slug).exists():
        suffix = f"-{counter}"
        unique_slug = f"{slug[:max_length - len(suffix)]}{suffix}"
        counter += 1
    return unique_slug

