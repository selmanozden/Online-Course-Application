"""Enrollment model placeholder."""
from django.db import models


class Enrollment(models.Model):
    user = models.ForeignKey('user_model.User', on_delete=models.CASCADE)
    course = models.ForeignKey('course_model.Course', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.course}"
