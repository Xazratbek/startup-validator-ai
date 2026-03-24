from __future__ import annotations

import re
from collections import defaultdict

from django.db import transaction

from apps.projects.models import Assumption, Project, StartupProfileSnapshot
from apps.research.tasks import run_research_pipeline_task
from core.common.enums import InterviewPhase, InterviewRole, ProjectStatus
from .models import InterviewMessage, InterviewSession
from .state_machine import PHASES, PHASE_FIELD_MAP, get_question, phase_completion_index

class InterviewService:
    @staticmethod
    def start(project: Project) -> InterviewSession:
        session = project.interview_sessions.order_by('-created_at').first()
        if session and session.status == 'ACTIVE':
            return session
        session = InterviewSession.objects.create(project=project)
        InterviewMessage.objects.create(
            session=session,
            role=InterviewRole.ASSISTANT,
            phase=session.current_phase,
            content=get_question(session.current_phase),
        )
        project.status = ProjectStatus.INTERVIEWING
        project.save(update_fields=['status', 'updated_at'])
        return session

    @staticmethod
    @transaction.atomic
    def reply(session: InterviewSession, content: str) -> InterviewSession:
        InterviewMessage.objects.create(session=session, role=InterviewRole.USER, phase=session.current_phase, content=content)
        snapshot = ProfileExtractionService.extract_snapshot(session.project)
        current_phase = session.current_phase
        session.phase_confidence_json[current_phase] = ProfileExtractionService.phase_confidence(snapshot, current_phase)
        next_phase = InterviewService._determine_next_phase(snapshot, current_phase)
        session.current_phase = next_phase
        session.completion_percent = phase_completion_index(next_phase)
        if next_phase == InterviewPhase.COMPLETE:
            session.status = 'COMPLETED'
        session.save(update_fields=['phase_confidence_json', 'current_phase', 'completion_percent', 'status', 'updated_at'])
        if next_phase != InterviewPhase.COMPLETE:
            asked_count = session.messages.filter(role=InterviewRole.ASSISTANT, phase=next_phase).count()
            InterviewMessage.objects.create(
                session=session,
                role=InterviewRole.ASSISTANT,
                phase=next_phase,
                content=get_question(next_phase, asked_count),
            )
        else:
            run_research_pipeline_task.delay(session.project_id)
        return session

    @staticmethod
    def _determine_next_phase(snapshot: StartupProfileSnapshot, current_phase: str) -> str:
        data = snapshot.structured_json
        for phase in PHASES:
            if ProfileExtractionService.phase_confidence(snapshot, phase) < 0.7:
                return phase
        return InterviewPhase.COMPLETE

class ProfileExtractionService:
    @staticmethod
    def extract_snapshot(project: Project) -> StartupProfileSnapshot:
        session = project.interview_sessions.order_by('-created_at').first()
        messages = list(session.messages.all()) if session else []
        grouped_answers = defaultdict(list)
        founder_assumptions: list[str] = []
        for message in messages:
            if message.role != InterviewRole.USER:
                continue
            grouped_answers[message.phase].append(message.content.strip())
            if any(keyword in message.content.lower() for keyword in ['assumption', 'if', 'might', 'uncertain', 'risk']):
                founder_assumptions.append(message.content.strip())

        clarify = ' '.join(grouped_answers[InterviewPhase.CLARIFY]).strip() or project.idea_one_liner
        icp = ' '.join(grouped_answers[InterviewPhase.ICP]).strip()
        pain = ' '.join(grouped_answers[InterviewPhase.PAIN]).strip() or project.raw_description[:300]
        alternatives = grouped_answers[InterviewPhase.ALTERNATIVES]
        monetization = ' '.join(grouped_answers[InterviewPhase.MONETIZATION]).strip()
        acquisition = ' '.join(grouped_answers[InterviewPhase.ACQUISITION]).strip()
        edge_text = ' '.join(grouped_answers[InterviewPhase.EDGE]).strip()
        review = ' '.join(grouped_answers[InterviewPhase.REVIEW]).strip()
        founder_edge, constraints = ProfileExtractionService._split_edge_constraints(edge_text)

        profile = {
            'idea_summary': ProfileExtractionService._sentence(clean=clarify or project.idea_one_liner),
            'icp': ProfileExtractionService._sentence(clean=icp),
            'problem_statement': ProfileExtractionService._sentence(clean=pain),
            'alternatives': alternatives,
            'value_prop': ProfileExtractionService._derive_value_prop(project.idea_one_liner, clarify, pain),
            'monetization_hypothesis': ProfileExtractionService._sentence(clean=monetization),
            'acquisition_hypothesis': ProfileExtractionService._sentence(clean=acquisition),
            'founder_edge': founder_edge,
            'constraints': constraints,
            'founder_assumptions': founder_assumptions + ([review] if review else []),
            'raw_phase_answers': {phase: answers for phase, answers in grouped_answers.items()},
        }
        latest = project.snapshots.first()
        version = latest.version + 1 if latest else 1
        snapshot = StartupProfileSnapshot.objects.create(
            project=project,
            version=version,
            summary=profile['idea_summary'],
            icp=profile['icp'],
            problem_statement=profile['problem_statement'],
            alternatives=profile['alternatives'],
            value_prop=profile['value_prop'],
            monetization_hypothesis=profile['monetization_hypothesis'],
            acquisition_hypothesis=profile['acquisition_hypothesis'],
            founder_edge=profile['founder_edge'],
            constraints=profile['constraints'],
            structured_json=profile,
        )
        project.latest_structured_model_snapshot = profile
        project.save(update_fields=['latest_structured_model_snapshot', 'updated_at'])
        Assumption.objects.filter(project=project, snapshot=snapshot).delete()
        for category, statement in ProfileExtractionService._extract_assumptions(profile):
            Assumption.objects.create(
                project=project,
                snapshot=snapshot,
                category=category,
                statement=statement,
                confidence=0.45 if category in {'ICP', 'MONETIZATION', 'ACQUISITION'} else 0.6,
                evidence_status='PENDING_RESEARCH',
            )
        return snapshot

    @staticmethod
    def _extract_assumptions(profile: dict) -> list[tuple[str, str]]:
        assumptions = []
        mappings = {
            'ICP': profile.get('icp'),
            'PROBLEM': profile.get('problem_statement'),
            'MONETIZATION': profile.get('monetization_hypothesis'),
            'ACQUISITION': profile.get('acquisition_hypothesis'),
            'EDGE': profile.get('founder_edge'),
        }
        for category, statement in mappings.items():
            if statement:
                assumptions.append((category, statement))
        for item in profile.get('founder_assumptions', []):
            if item:
                assumptions.append(('REVIEW', item))
        return assumptions

    @staticmethod
    def phase_confidence(snapshot: StartupProfileSnapshot, phase: str) -> float:
        data = snapshot.structured_json
        fields = PHASE_FIELD_MAP.get(phase, ())
        values = []
        for field in fields:
            value = data.get(field)
            if isinstance(value, list):
                values.append(1.0 if value else 0.0)
            else:
                values.append(min(1.0, len((value or '').split()) / 12))
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    @staticmethod
    def _derive_value_prop(one_liner: str, clarify: str, pain: str) -> str:
        if clarify:
            return ProfileExtractionService._sentence(clean=clarify)
        return ProfileExtractionService._sentence(clean=f'{one_liner}. Solves: {pain}')

    @staticmethod
    def _split_edge_constraints(text: str) -> tuple[str, str]:
        if not text:
            return '', ''
        parts = re.split(r'\bbut\b|\bhowever\b|\bconstraint\b|\brisk\b', text, maxsplit=1, flags=re.I)
        edge = ProfileExtractionService._sentence(clean=parts[0])
        constraint = ProfileExtractionService._sentence(clean=parts[1]) if len(parts) > 1 else ''
        return edge, constraint

    @staticmethod
    def _sentence(clean: str) -> str:
        clean = re.sub(r'\s+', ' ', (clean or '').strip())
        return clean[:1000]
