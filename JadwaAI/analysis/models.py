from django.db import models
from django.conf import settings

class AnalysisResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    project_id = models.IntegerField()

    project_name = models.CharField(max_length=255, blank=True)

    probability = models.FloatField()
    threshold = models.FloatField(default=0.5)

    label = models.CharField(max_length=50)

    recommendations_ar = models.TextField(blank=True, default="")

    recommendations_en = models.TextField(blank=True, default="")

    recommendations_status_ar = models.CharField(
        max_length=20,
        default="pending"
    )

    recommendations_status_en = models.CharField(
        max_length=20,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.project_name} - {self.label}"