from django.urls import path
from .views import LatestRecommendationView
urlpatterns = [path('projects/<int:project_id>/recommendation/latest', LatestRecommendationView.as_view())]
