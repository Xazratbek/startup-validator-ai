from django.urls import path
from .views import InterviewStartView, InterviewDetailView, InterviewReplyView, InterviewStateView
urlpatterns = [
    path('projects/<int:project_id>/interview/start', InterviewStartView.as_view()),
    path('projects/<int:project_id>/interview', InterviewDetailView.as_view()),
    path('projects/<int:project_id>/interview/reply', InterviewReplyView.as_view()),
    path('projects/<int:project_id>/interview/state', InterviewStateView.as_view()),
]
