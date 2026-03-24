from django.db import models
from apps.projects.models import Project, StartupProfileSnapshot
from core.common.enums import ArtifactType

class GeneratedArtifact(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='artifacts')
    snapshot = models.ForeignKey(StartupProfileSnapshot, on_delete=models.CASCADE, related_name='artifacts')
    artifact_type = models.CharField(max_length=32, choices=ArtifactType.choices)
    title = models.CharField(max_length=255)
    content = models.TextField()
    metadata_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
