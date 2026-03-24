# Backend

Django REST API for Founder Validation OS.

## Commands
```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
celery -A config worker -l info
pytest
```

## Apps
- `apps.accounts` auth and profile endpoints
- `apps.projects` project workspace models and APIs
- `apps.interviews` interview sessions and state machine
- `apps.research` research runs, evidence, competitors, providers
- `apps.scoring` explainable scoring engine
- `apps.recommendations` decision logic
- `apps.artifacts` generated founder action artifacts
- `core.ai` provider abstraction and prompt templates
