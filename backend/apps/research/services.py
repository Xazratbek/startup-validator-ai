from __future__ import annotations

from collections import Counter
from urllib.parse import urlparse

from django.utils import timezone

from apps.artifacts.services import ArtifactService
from apps.projects.models import Project
from apps.recommendations.services import RecommendationEngine
from apps.scoring.services import ScoringEngine
from core.common.enums import ProjectStatus, ResearchRunStatus
from core.research_providers.base import ResearchQuery
from core.research_providers.provider_factory import get_research_provider
from .models import Competitor, EvidenceItem, ResearchRun, ResearchSource

class ResearchPipelineService:
    @staticmethod
    def build_queries(project: Project, snapshot) -> list[ResearchQuery]:
        profile = snapshot.structured_json if snapshot else {}
        icp = profile.get('icp') or project.idea_one_liner
        problem = profile.get('problem_statement') or project.raw_description
        value_prop = profile.get('value_prop') or project.idea_one_liner
        return [
            ResearchQuery(query=f'best software alternatives for {problem}', category='COMPETITOR'),
            ResearchQuery(query=f'{problem} market trend {icp}', category='MARKET'),
            ResearchQuery(query=f'{icp} complaint about {problem}', category='PAIN'),
            ResearchQuery(query=f'{value_prop} pricing SaaS', category='PRICING'),
            ResearchQuery(query=f'{problem} search demand trend', category='SEARCH'),
            ResearchQuery(query=f'{problem} compliance regulation risk', category='RISK'),
        ]

    @staticmethod
    def run(project: Project) -> ResearchRun:
        snapshot = project.snapshots.first()
        existing = project.research_runs.filter(snapshot=snapshot, status=ResearchRunStatus.COMPLETED).order_by('-started_at').first()
        if existing:
            return existing
        queries = ResearchPipelineService.build_queries(project, snapshot)
        run = ResearchRun.objects.create(project=project, snapshot=snapshot, status=ResearchRunStatus.RUNNING, provider='live_web')
        provider = get_research_provider()
        docs = provider.collect(project.title, snapshot.structured_json if snapshot else {}, queries)
        category_counter = Counter()
        for doc in docs:
            parsed = urlparse(doc.url)
            source = ResearchSource.objects.create(
                research_run=run,
                source_name=doc.source_name,
                title=doc.title[:255],
                url=doc.url,
                domain=parsed.netloc,
                source_type='web',
                credibility_score=doc.confidence,
            )
            EvidenceItem.objects.create(
                research_run=run,
                source=source,
                category=doc.category,
                title=doc.title[:255],
                snippet=doc.snippet,
                extracted_claim=doc.claim,
                relevance_score=ResearchPipelineService._relevance_score(snapshot.structured_json if snapshot else {}, doc),
                confidence_score=doc.confidence,
                citation_json=doc.citation_metadata,
            )
            category_counter[doc.category] += 1
            if doc.category == 'COMPETITOR':
                Competitor.objects.get_or_create(
                    research_run=run,
                    name=ResearchPipelineService._competitor_name(doc),
                    defaults={
                        'url': doc.url,
                        'positioning': doc.claim,
                        'target_customer': (snapshot.icp if snapshot else '')[:500],
                        'pricing_summary': ResearchPipelineService._extract_pricing(doc.snippet),
                        'strengths': [doc.title[:120], 'Existing visibility in search results'],
                        'weaknesses': ['Differentiation against focused niche players may be needed'],
                    },
                )
        run.status = ResearchRunStatus.COMPLETED
        run.completed_at = timezone.now()
        run.summary_json = {
            'queries': [q.query for q in queries],
            'categories': dict(category_counter),
            'evidence_count': len(docs),
            'competitor_count': run.competitors.count(),
        }
        run.save(update_fields=['status', 'completed_at', 'summary_json'])
        project.latest_research_snapshot = run.summary_json
        project.status = ProjectStatus.RESEARCHING
        project.save(update_fields=['latest_research_snapshot', 'status', 'updated_at'])
        scoring = ScoringEngine.compute(project, snapshot, run)
        recommendation = RecommendationEngine.generate(project, snapshot, scoring)
        ArtifactService.generate_all(project, snapshot, recommendation)
        project.current_decision = recommendation.decision
        project.status = ProjectStatus.DECIDED
        project.save(update_fields=['current_decision', 'status', 'updated_at'])
        return run

    @staticmethod
    def _competitor_name(doc) -> str:
        domain = urlparse(doc.url).netloc.replace('www.', '').split('.')[0]
        return domain.replace('-', ' ').title() or doc.source_name[:120]

    @staticmethod
    def _extract_pricing(snippet: str) -> str:
        import re
        matches = re.findall(r'\$\s?\d+[\d,]*(?:/\w+)?', snippet)
        return ', '.join(matches[:3]) if matches else 'Pricing not surfaced in source excerpt'

    @staticmethod
    def _relevance_score(profile: dict, doc) -> float:
        icp = (profile.get('icp') or '').lower()
        problem = (profile.get('problem_statement') or '').lower()
        text = f'{doc.title} {doc.snippet}'.lower()
        score = 0.45
        if icp and any(token in text for token in icp.split()[:4]):
            score += 0.2
        if problem and any(token in text for token in problem.split()[:5]):
            score += 0.2
        if doc.category in {'PAIN', 'PRICING', 'COMPETITOR'}:
            score += 0.1
        return round(min(score, 0.95), 2)
