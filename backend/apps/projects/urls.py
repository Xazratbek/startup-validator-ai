from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, ProjectHistoryView, ProjectCompareView
urlpatterns = [
    path('projects', ProjectListCreateView.as_view()),
    path('projects/<int:pk>', ProjectDetailView.as_view()),
    path('projects/<int:pk>/history', ProjectHistoryView.as_view()),
    path('projects/<int:pk>/compare', ProjectCompareView.as_view()),
]
