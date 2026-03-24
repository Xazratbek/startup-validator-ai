from celery import shared_task
from apps.projects.models import Project
from .services import ResearchPipelineService

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def run_research_pipeline_task(self, project_id: int):
    project = Project.objects.get(id=project_id)
    return ResearchPipelineService.run(project).id
