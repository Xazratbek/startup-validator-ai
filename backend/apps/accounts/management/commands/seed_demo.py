from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.interviews.services import InterviewService
from apps.projects.models import Project

User = get_user_model()

STARTER_PROJECTS = [
    {
        'title': 'AI Sales Qualifier',
        'idea_one_liner': 'AI assistant that helps consultants qualify inbound B2B leads.',
        'raw_description': 'Help independent consultants qualify inbound leads before live calls so they spend more time on high-fit opportunities.',
    },
    {
        'title': 'Clinic Follow-up Copilot',
        'idea_one_liner': 'Patient follow-up automation for specialty clinics.',
        'raw_description': 'Reduce missed follow-ups and manual staff work after appointments for small specialty clinics.',
    },
]

class Command(BaseCommand):
    help = 'Create a demo user and starter projects without synthetic research output'

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            email='demo@founderos.dev',
            defaults={'username': 'demo', 'first_name': 'Demo'},
        )
        user.set_password('demo12345')
        user.save()
        for payload in STARTER_PROJECTS:
            project, _ = Project.objects.get_or_create(owner=user, title=payload['title'], defaults=payload)
            InterviewService.start(project)
        self.stdout.write(self.style.SUCCESS('Demo user and starter projects are ready.'))
