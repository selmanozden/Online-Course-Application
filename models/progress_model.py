"""Progress tracking model placeholder."""
from django.db import models


class Progress(models.Model):
    enrollment = models.ForeignKey('enrollment_model.Enrollment', on_delete=models.CASCADE)
    content = models.ForeignKey('content_model.Content', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.enrollment.user} - {self.content} - {self.completed}"
