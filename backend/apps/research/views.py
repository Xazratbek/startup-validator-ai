from rest_framework.response import Response
from rest_framework.views import APIView
from apps.projects.models import Project
from .models import ResearchRun
from .serializers import ResearchRunSerializer
from .services import ResearchPipelineService

class OwnedProjectMixin:
    def get_project(self, request, project_id):
        return Project.objects.get(id=project_id, owner=request.user)

class RunResearchView(OwnedProjectMixin, APIView):
    def post(self, request, project_id):
        run = ResearchPipelineService.run(self.get_project(request, project_id))
        return Response(ResearchRunSerializer(run).data)

class LatestResearchView(OwnedProjectMixin, APIView):
    def get(self, request, project_id):
        run = self.get_project(request, project_id).research_runs.order_by('-started_at').first()
        return Response(ResearchRunSerializer(run).data if run else {})

class ResearchRunsView(OwnedProjectMixin, APIView):
    def get(self, request, project_id):
        runs = self.get_project(request, project_id).research_runs.order_by('-started_at')
        return Response(ResearchRunSerializer(runs, many=True).data)

class ResearchRunDetailView(APIView):
    def get(self, request, pk):
        run = ResearchRun.objects.get(id=pk, project__owner=request.user)
        return Response(ResearchRunSerializer(run).data)
