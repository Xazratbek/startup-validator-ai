from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.projects.models import Project
from .serializers import InterviewReplySerializer, InterviewSessionSerializer
from .services import InterviewService

class ProjectOwnedMixin:
    def get_project(self, request, project_id):
        return Project.objects.get(id=project_id, owner=request.user)

class InterviewStartView(ProjectOwnedMixin, APIView):
    def post(self, request, project_id):
        session = InterviewService.start(self.get_project(request, project_id))
        return Response(InterviewSessionSerializer(session).data)

class InterviewDetailView(ProjectOwnedMixin, APIView):
    def get(self, request, project_id):
        session = self.get_project(request, project_id).interview_sessions.order_by('-created_at').first()
        return Response(InterviewSessionSerializer(session).data if session else {})

class InterviewReplyView(ProjectOwnedMixin, APIView):
    def post(self, request, project_id):
        serializer = InterviewReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = self.get_project(request, project_id)
        session = project.interview_sessions.order_by('-created_at').first() or InterviewService.start(project)
        session = InterviewService.reply(session, serializer.validated_data['content'])
        return Response(InterviewSessionSerializer(session).data, status=status.HTTP_200_OK)

class InterviewStateView(ProjectOwnedMixin, APIView):
    def get(self, request, project_id):
        session = self.get_project(request, project_id).interview_sessions.order_by('-created_at').first()
        return Response({'current_phase': getattr(session, 'current_phase', None), 'completion_percent': getattr(session, 'completion_percent', 0), 'status': getattr(session, 'status', 'NOT_STARTED')})
