"""Question model placeholder."""
from django.db import models


class Question(models.Model):
    exam = models.ForeignKey('exam_model.Exam', on_delete=models.CASCADE)
    text = models.TextField()
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.text[:50]
