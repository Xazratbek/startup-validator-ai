from django.urls import path
from .views import ArtifactListView, ArtifactRegenerateView
urlpatterns = [
    path('projects/<int:project_id>/artifacts', ArtifactListView.as_view()),
    path('projects/<int:project_id>/artifacts/regenerate', ArtifactRegenerateView.as_view()),
]
