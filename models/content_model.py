"""Content model placeholder."""
from django.db import models


class Content(models.Model):
    course = models.ForeignKey('course_model.Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
