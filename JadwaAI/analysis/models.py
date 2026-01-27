from django.db import models
from django.contrib.auth.models import User


class AnalysisResult(models.Model):
    # The user who requested the analysis
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Temporary project identifier (will be replaced with ForeignKey to Project model)
    project_id = models.IntegerField()

    # Project name (used for display purposes only)
    project_name = models.CharField(max_length=255, blank=True)

    # Feasibility probability returned by the prediction model
    probability = models.FloatField()

    # Decision threshold used to determine feasibility
    threshold = models.FloatField(default=0.5)

    # Final feasibility label (e.g., Feasible / Not Feasible)
    label = models.CharField(max_length=50)

    # AI-generated recommendations (stored as plain text)
    recommendations = models.TextField(blank=True, default="")

    # Recommendations generation status: pending / ready / failed
    recommendations_status = models.CharField(
        max_length=20,
        default="pending"
    )

    # Timestamp when the analysis result was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.project_name} - {self.label}"
