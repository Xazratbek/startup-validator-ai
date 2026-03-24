from django.conf import settings
from django.db import models
from core.common.enums import ProjectStatus, DecisionType

class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    idea_one_liner = models.CharField(max_length=255)
    raw_description = models.TextField()
    status = models.CharField(max_length=32, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT)
    current_decision = models.CharField(max_length=32, choices=DecisionType.choices, blank=True)
    latest_research_snapshot = models.JSONField(default=dict, blank=True)
    latest_structured_model_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StartupProfileSnapshot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='snapshots')
    version = models.PositiveIntegerField()
    summary = models.TextField(blank=True)
    icp = models.TextField(blank=True)
    problem_statement = models.TextField(blank=True)
    alternatives = models.JSONField(default=list, blank=True)
    value_prop = models.TextField(blank=True)
    monetization_hypothesis = models.TextField(blank=True)
    acquisition_hypothesis = models.TextField(blank=True)
    founder_edge = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    structured_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'version')
        ordering = ['-version']

class Assumption(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assumptions')
    snapshot = models.ForeignKey(StartupProfileSnapshot, on_delete=models.CASCADE, related_name='assumptions')
    category = models.CharField(max_length=64)
    statement = models.TextField()
    confidence = models.FloatField(default=0.5)
    evidence_status = models.CharField(max_length=64, default='UNVERIFIED')
    created_at = models.DateTimeField(auto_now_add=True)
