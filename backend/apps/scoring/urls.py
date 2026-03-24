from django.urls import path
from .views import LatestScoreView
urlpatterns = [path('projects/<int:project_id>/scores/latest', LatestScoreView.as_view())]
