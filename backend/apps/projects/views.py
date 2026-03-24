from rest_framework import generics
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer

class OwnedProjectMixin:
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProjectListCreateView(OwnedProjectMixin, generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

class ProjectDetailView(OwnedProjectMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer

class ProjectHistoryView(OwnedProjectMixin, generics.RetrieveAPIView):
    serializer_class = ProjectSerializer

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        data = ProjectSerializer(project).data
        data['history'] = [
            {
                'version': s.version,
                'created_at': s.created_at,
                'summary': s.summary,
                'structured_json': s.structured_json,
            }
            for s in project.snapshots.all().order_by('-version')
        ]
        return Response(data)

class ProjectCompareView(OwnedProjectMixin, generics.RetrieveAPIView):
    serializer_class = ProjectSerializer

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        from_version = int(request.query_params.get('from', 1))
        to_version = int(request.query_params.get('to', 1))
        source = project.snapshots.get(version=from_version)
        target = project.snapshots.get(version=to_version)
        changed_keys = sorted({*source.structured_json.keys(), *target.structured_json.keys()})
        diff = {
            key: {'from': source.structured_json.get(key), 'to': target.structured_json.get(key)}
            for key in changed_keys
            if source.structured_json.get(key) != target.structured_json.get(key)
        }
        return Response({'project_id': project.id, 'from_version': from_version, 'to_version': to_version, 'changes': diff})
