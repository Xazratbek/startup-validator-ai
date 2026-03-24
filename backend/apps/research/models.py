from django.db import models
from apps.projects.models import Project, StartupProfileSnapshot
from core.common.enums import ResearchRunStatus, EvidenceType

class ResearchRun(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='research_runs')
    snapshot = models.ForeignKey(StartupProfileSnapshot, on_delete=models.CASCADE, related_name='research_runs')
    status = models.CharField(max_length=32, choices=ResearchRunStatus.choices, default=ResearchRunStatus.QUEUED)
    provider = models.CharField(max_length=64, default='live_web')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    summary_json = models.JSONField(default=dict, blank=True)

class ResearchSource(models.Model):
    research_run = models.ForeignKey(ResearchRun, on_delete=models.CASCADE, related_name='sources')
    source_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    url = models.URLField()
    published_at = models.DateField(null=True, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=64, default='web')
    credibility_score = models.FloatField(default=0.5)

class EvidenceItem(models.Model):
    research_run = models.ForeignKey(ResearchRun, on_delete=models.CASCADE, related_name='evidence_items')
    source = models.ForeignKey(ResearchSource, on_delete=models.CASCADE, related_name='evidence_items')
    category = models.CharField(max_length=32, choices=EvidenceType.choices)
    title = models.CharField(max_length=255)
    snippet = models.TextField()
    extracted_claim = models.TextField()
    relevance_score = models.FloatField(default=0.5)
    confidence_score = models.FloatField(default=0.5)
    citation_json = models.JSONField(default=dict, blank=True)

class Competitor(models.Model):
    research_run = models.ForeignKey(ResearchRun, on_delete=models.CASCADE, related_name='competitors')
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    positioning = models.TextField(blank=True)
    target_customer = models.TextField(blank=True)
    pricing_summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
