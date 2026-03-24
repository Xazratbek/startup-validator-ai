from django.contrib import admin
from django.urls import include, path
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.projects.urls')),
    path('api/', include('apps.interviews.urls')),
    path('api/', include('apps.research.urls')),
    path('api/', include('apps.scoring.urls')),
    path('api/', include('apps.recommendations.urls')),
    path('api/', include('apps.artifacts.urls')),
]
