from django.db import models
from apps.projects.models import Project
from core.common.enums import InterviewPhase, InterviewRole

class InterviewSession(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='interview_sessions')
    status = models.CharField(max_length=32, default='ACTIVE')
    current_phase = models.CharField(max_length=32, choices=InterviewPhase.choices, default=InterviewPhase.CLARIFY)
    completion_percent = models.PositiveIntegerField(default=0)
    phase_confidence_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class InterviewMessage(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=16, choices=InterviewRole.choices)
    phase = models.CharField(max_length=32, choices=InterviewPhase.choices)
    content = models.TextField()
    extracted_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
