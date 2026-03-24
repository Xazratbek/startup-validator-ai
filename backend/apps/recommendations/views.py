from rest_framework.response import Response
from rest_framework.views import APIView
from apps.projects.models import Project
from .serializers import RecommendationSerializer

class LatestRecommendationView(APIView):
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id, owner=request.user)
        recommendation = project.recommendations.order_by('-created_at').first()
        return Response(RecommendationSerializer(recommendation).data if recommendation else {})
