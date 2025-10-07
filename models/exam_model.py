"""Exam model placeholder."""
from django.db import models


class Exam(models.Model):
    course = models.ForeignKey('course_model.Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
