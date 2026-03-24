import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.artifacts.services import ArtifactService
from apps.interviews.services import InterviewService
from apps.projects.models import Project
from apps.recommendations.services import RecommendationEngine
from apps.research.models import ResearchRun
from apps.scoring.services import ScoringEngine
from apps.accounts.models import TelegramAuthSession


@pytest.mark.django_db
def test_project_lifecycle():
    User = get_user_model()
    User.objects.create_user(email='a@b.com', username='ab', password='pass12345')
    client = APIClient()
    token = client.post('/api/auth/login', {'email': 'a@b.com', 'password': 'pass12345'}, format='json').data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    project = client.post('/api/projects', {'title': 'Test', 'idea_one_liner': 'Idea', 'raw_description': 'Raw'}, format='json')
    assert project.status_code == 201
    pid = project.data['id']
    start = client.post(f'/api/projects/{pid}/interview/start')
    assert start.status_code == 200
    reply = client.post(f'/api/projects/{pid}/interview/reply', {'content': 'B2B founders at 10-50 person SaaS teams'}, format='json')
    assert reply.status_code == 200
    assert Project.objects.get(id=pid).snapshots.count() >= 1


@pytest.mark.django_db
def test_scoring_recommendation_and_artifacts_are_database_integrated():
    User = get_user_model()
    user = User.objects.create_user(email='demo2@x.com', username='demo2', password='pass12345')
    project = Project.objects.create(owner=user, title='Test', idea_one_liner='Idea', raw_description='Desc')
    session = InterviewService.start(project)
    answers = [
        'A workflow tool for specialty recruiters.',
        'Recruiting agencies focused on healthcare hiring.',
        'They lose hours each week screening low-fit applicants manually.',
        'They use ATS filters and spreadsheets today.',
        'Agency owners would pay monthly if it reliably cuts screening time.',
        'Founder-led outbound and partner referrals from recruiter communities.',
        'Founder previously ran recruiting operations but compliance requirements may slow rollout.',
        'The riskiest assumption is whether agencies trust AI-generated fit summaries.',
    ]
    for answer in answers:
        session = InterviewService.reply(session, answer)
    snapshot = project.snapshots.first()
    run = ResearchRun.objects.create(project=project, snapshot=snapshot, status='COMPLETED', provider='test', summary_json={})
    score = ScoringEngine.compute(project, snapshot, run)
    recommendation = RecommendationEngine.generate(project, snapshot, score)
    artifacts = ArtifactService.generate_all(project, snapshot, recommendation)
    assert score.total_score > 0
    assert recommendation.decision in {'BUILD_NOW', 'RUN_VALIDATION_FIRST', 'NARROW_NICHE', 'PIVOT', 'KILL'}
    assert len(artifacts) == 8


@pytest.mark.django_db
def test_telegram_auth_flow_registers_and_verifies_with_6_digit_code():
    client = APIClient()
    start = client.post('/api/auth/telegram/start', {'language': 'uz'}, format='json')
    assert start.status_code == 200
    token = start.data['session_token']

    client.post('/api/auth/telegram/webhook', {
        'update_id': 1,
        'message': {
            'text': f'/start auth_{token}',
            'from': {'id': 778899, 'username': 'newuser', 'first_name': 'Ali'},
        },
    }, format='json')
    client.post('/api/auth/telegram/webhook', {
        'update_id': 2,
        'message': {
            'text': 'Ali Valiyev',
            'from': {'id': 778899, 'username': 'newuser', 'first_name': 'Ali'},
        },
    }, format='json')
    client.post('/api/auth/telegram/webhook', {
        'update_id': 3,
        'message': {
            'text': '+998901112233',
            'from': {'id': 778899, 'username': 'newuser', 'first_name': 'Ali'},
        },
    }, format='json')

    session = TelegramAuthSession.objects.get(session_token=token)
    assert session.code
    verify = client.post('/api/auth/telegram/verify', {'session_token': token, 'code': session.code}, format='json')
    assert verify.status_code == 200
    assert 'access' in verify.data
