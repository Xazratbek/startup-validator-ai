from rest_framework.response import Response
from rest_framework.views import APIView
from apps.projects.models import Project
from .serializers import ScoringResultSerializer

class LatestScoreView(APIView):
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id, owner=request.user)
        score = project.scoring_results.order_by('-created_at').first()
        return Response(ScoringResultSerializer(score).data if score else {})
