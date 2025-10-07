"""Exam and ExamResult models."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from .course_model import Course


class Exam(models.Model):
    """Exam model for course assessments."""
    
    class ExamType(models.TextChoices):
        QUIZ = 'QUIZ', 'Quiz'
        MIDTERM = 'MIDTERM', 'Midterm'
        FINAL = 'FINAL', 'Final'
        PRACTICE = 'PRACTICE', 'Practice'
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='exams',
        help_text='Associated course'
    )
    
    title = models.CharField(
        max_length=200,
        help_text='Exam title'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Exam description and instructions'
    )
    
    exam_type = models.CharField(
        max_length=10,
        choices=ExamType.choices,
        default=ExamType.QUIZ,
        help_text='Type of exam'
    )
    
    duration_minutes = models.PositiveIntegerField(
        help_text='Exam duration in minutes'
    )
    
    total_marks = models.PositiveIntegerField(
        default=100,
        help_text='Total marks for the exam'
    )
    
    passing_marks = models.PositiveIntegerField(
        help_text='Minimum marks required to pass'
    )
    
    max_attempts = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of attempts allowed'
    )
    
    is_published = models.BooleanField(
        default=False,
        help_text='Is exam available to students'
    )
    
    is_required = models.BooleanField(
        default=True,
        help_text='Must be passed to complete course'
    )
    
    randomize_questions = models.BooleanField(
        default=True,
        help_text='Randomize question order for each attempt'
    )
    
    show_results_immediately = models.BooleanField(
        default=True,
        help_text='Show results immediately after submission'
    )
    
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Exam availability start date'
    )
    
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Exam availability end date'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exams'
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        ordering = ['course', '-created_at']
        indexes = [
            models.Index(fields=['course', 'is_published']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def passing_percentage(self):
        """Calculate passing percentage."""
        if self.total_marks > 0:
            return (self.passing_marks / self.total_marks) * 100
        return 0
    
    @property
    def question_count(self):
        """Get total number of questions."""
        return self.questions.count()
    
    def is_available(self):
        """Check if exam is currently available."""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_published:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True


class ExamResult(models.Model):
    """Student exam attempt and result model."""
    
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        GRADED = 'GRADED', 'Graded'
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results',
        help_text='Associated exam'
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_results',
        limit_choices_to={'role': 'STUDENT'},
        help_text='Student who took the exam'
    )
    
    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text='Attempt number'
    )
    
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        help_text='Exam attempt status'
    )
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text='Score obtained'
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage score'
    )
    
    is_passed = models.BooleanField(
        default=False,
        help_text='Did student pass the exam'
    )
    
    answers = models.JSONField(
        default=dict,
        help_text='Student answers (question_id: answer)'
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    
    time_taken_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Time taken to complete exam'
    )
    
    feedback = models.TextField(
        blank=True,
        help_text='Teacher feedback'
    )
    
    class Meta:
        db_table = 'exam_results'
        verbose_name = 'Exam Result'
        verbose_name_plural = 'Exam Results'
        ordering = ['-started_at']
        unique_together = [['exam', 'student', 'attempt_number']]
        indexes = [
            models.Index(fields=['student', '-started_at']),
            models.Index(fields=['exam', 'student']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title} (Attempt {self.attempt_number})"
    
    def calculate_result(self):
        """Calculate exam score and percentage."""
        total_questions = self.exam.questions.count()
        if total_questions == 0:
            return
        
        correct_answers = 0
        for question in self.exam.questions.all():
            student_answer = self.answers.get(str(question.id))
            if student_answer == question.correct_answer:
                correct_answers += 1
        
        # Calculate score
        marks_per_question = self.exam.total_marks / total_questions
        self.score = correct_answers * marks_per_question
        
        # Calculate percentage
        self.percentage = (self.score / self.exam.total_marks) * 100
        
        # Check if passed
        self.is_passed = self.score >= self.exam.passing_marks
        
        self.status = self.Status.GRADED
        self.save()

