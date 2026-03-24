from django.urls import path
from .views import RunResearchView, LatestResearchView, ResearchRunsView, ResearchRunDetailView
urlpatterns = [
    path('projects/<int:project_id>/research/run', RunResearchView.as_view()),
    path('projects/<int:project_id>/research/latest', LatestResearchView.as_view()),
    path('projects/<int:project_id>/research/runs', ResearchRunsView.as_view()),
    path('research-runs/<int:pk>', ResearchRunDetailView.as_view()),
]
