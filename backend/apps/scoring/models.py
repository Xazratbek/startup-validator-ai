from django.db import models
from apps.projects.models import Project, StartupProfileSnapshot
from apps.research.models import ResearchRun

class ScoringResult(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scoring_results')
    snapshot = models.ForeignKey(StartupProfileSnapshot, on_delete=models.CASCADE, related_name='scoring_results')
    research_run = models.ForeignKey(ResearchRun, on_delete=models.CASCADE, related_name='scoring_results')
    total_score = models.FloatField()
    dimension_scores_json = models.JSONField(default=dict)
    weights_json = models.JSONField(default=dict)
    risk_flags_json = models.JSONField(default=list)
    rationale_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
