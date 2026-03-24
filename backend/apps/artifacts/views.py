from rest_framework.response import Response
from rest_framework.views import APIView
from apps.projects.models import Project
from apps.recommendations.services import RecommendationEngine
from apps.scoring.services import ScoringEngine
from .serializers import GeneratedArtifactSerializer
from .services import ArtifactService

class ArtifactListView(APIView):
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id, owner=request.user)
        return Response(GeneratedArtifactSerializer(project.artifacts.order_by('artifact_type'), many=True).data)

class ArtifactRegenerateView(APIView):
    def post(self, request, project_id):
        project = Project.objects.get(id=project_id, owner=request.user)
        snapshot = project.snapshots.first()
        score = project.scoring_results.first()
        recommendation = project.recommendations.first() or RecommendationEngine.generate(project, snapshot, score)
        artifacts = ArtifactService.generate_all(project, snapshot, recommendation)
        return Response(GeneratedArtifactSerializer(artifacts, many=True).data)
