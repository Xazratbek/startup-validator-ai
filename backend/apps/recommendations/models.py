from django.db import models
from apps.projects.models import Project, StartupProfileSnapshot
from apps.scoring.models import ScoringResult
from core.common.enums import DecisionType

class Recommendation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='recommendations')
    snapshot = models.ForeignKey(StartupProfileSnapshot, on_delete=models.CASCADE, related_name='recommendations')
    scoring_result = models.ForeignKey(ScoringResult, on_delete=models.CASCADE, related_name='recommendations')
    decision = models.CharField(max_length=32, choices=DecisionType.choices)
    reasoning = models.TextField()
    strengths_json = models.JSONField(default=list)
    weaknesses_json = models.JSONField(default=list)
    blockers_json = models.JSONField(default=list)
    conditions_json = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
