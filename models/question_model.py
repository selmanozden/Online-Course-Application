"""Question and Answer models for exams."""
from django.db import models
from .exam_model import Exam


class Question(models.Model):
    """Question model for exams."""
    
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice'
        TRUE_FALSE = 'TRUE_FALSE', 'True/False'
        SHORT_ANSWER = 'SHORT_ANSWER', 'Short Answer'
        ESSAY = 'ESSAY', 'Essay'
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text='Associated exam'
    )
    
    question_text = models.TextField(
        help_text='Question text'
    )
    
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
        help_text='Type of question'
    )
    
    marks = models.PositiveIntegerField(
        default=1,
        help_text='Marks for this question'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Question order in exam'
    )
    
    explanation = models.TextField(
        blank=True,
        help_text='Explanation of correct answer (shown after exam)'
    )
    
    # For multiple choice questions
    correct_answer = models.CharField(
        max_length=10,
        blank=True,
        help_text='Correct answer identifier (A, B, C, D, TRUE, FALSE)'
    )
    
    # Image support
    image = models.ImageField(
        upload_to='questions/',
        blank=True,
        null=True,
        help_text='Question image (optional)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['exam', 'order', 'created_at']
        indexes = [
            models.Index(fields=['exam', 'order']),
        ]
    
    def __str__(self):
        return f"{self.exam.title} - Q{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    """Answer options for multiple choice questions."""
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        help_text='Associated question'
    )
    
    answer_text = models.TextField(
        help_text='Answer option text'
    )
    
    identifier = models.CharField(
        max_length=10,
        help_text='Answer identifier (A, B, C, D)'
    )
    
    is_correct = models.BooleanField(
        default=False,
        help_text='Is this the correct answer'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Answer option order'
    )
    
    class Meta:
        db_table = 'answers'
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question} - {self.identifier}: {self.answer_text[:30]}"

