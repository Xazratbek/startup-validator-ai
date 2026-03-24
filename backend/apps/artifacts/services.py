from __future__ import annotations

from core.common.enums import ArtifactType
from .models import GeneratedArtifact

class ArtifactService:
    @staticmethod
    def generate_all(project, snapshot, recommendation):
        GeneratedArtifact.objects.filter(project=project).delete()
        profile = snapshot.structured_json if snapshot else {}
        icp = profile.get('icp') or 'target customers'
        problem = profile.get('problem_statement') or project.idea_one_liner
        value_prop = profile.get('value_prop') or project.idea_one_liner
        monetization = profile.get('monetization_hypothesis') or 'an ROI-backed subscription model'
        channel = profile.get('acquisition_hypothesis') or 'direct founder-led outreach'
        conditions = recommendation.conditions_json or []
        artifacts = {
            ArtifactType.INTERVIEW_SCRIPT: (
                f'1. Walk me through how {icp} handle {problem} today.\n'
                f'2. When was the last time this problem caused measurable pain?\n'
                f'3. What have you already tried instead?\n'
                f'4. What would make {value_prop} trustworthy enough to test?\n'
                f'5. What budget or approval path would a purchase require?'
            ),
            ArtifactType.OUTREACH_DM: (
                f'Hey — I\'m researching how {icp} currently deal with {problem}. '
                f'I\'m exploring {value_prop} and would love 15 minutes to learn how you handle it today.'
            ),
            ArtifactType.OUTREACH_EMAIL: (
                f'Subject: quick research on {problem}\n\n'
                f'I\'m speaking with {icp} teams about how they currently manage {problem}. '
                f'I\'m evaluating a new approach: {value_prop}. Could I ask you 5 questions in a 15-minute call this week?'
            ),
            ArtifactType.LANDING_PAGE: (
                f'Headline: {value_prop}\n'
                f'Subheadline: Built for {icp} dealing with {problem}.\n'
                f'Why now: Replace current alternatives with a faster, clearer workflow.\n'
                f'Primary CTA: Join the pilot / Book a discovery call.'
            ),
            ArtifactType.MVP_SCOPE: (
                f'- ICP-specific onboarding for {icp}\n'
                f'- Capture the current workflow/problem state\n'
                f'- Core value loop delivering {value_prop}\n'
                f'- Manual review/admin tooling to ensure quality before automation\n'
                f'- Basic analytics proving ROI against {monetization}'
            ),
            ArtifactType.VALIDATION_PLAN: (
                f'Day 1: build ICP list and offer hypothesis.\n'
                f'Day 2-3: run {channel}.\n'
                f'Day 4-5: conduct 8-10 interviews using the script.\n'
                f'Day 6: test willingness to pay and objections.\n'
                f'Day 7: review evidence and decide whether to {recommendation.decision.lower()}.'
            ),
            ArtifactType.CHECKLIST: (
                '- Define the assumption under test.\n'
                '- Identify the smallest real-world experiment.\n'
                '- Set success and failure thresholds.\n'
                '- Run outreach / interviews.\n'
                '- Log objections, urgency, and budget evidence.\n'
                '- Decide next action immediately after evidence review.'
            ),
            ArtifactType.METRICS: (
                f'Success thresholds:\n- 5+ qualified conversations with {icp}.\n'
                f'- At least 3 prospects confirm urgent pain around {problem}.\n'
                f'- At least 2 prospects accept a next-step offer or pilot.\n\n'
                f'Kill criteria:\n- No urgency signal after 10 interviews.\n'
                f'- No believable budget path for {monetization}.\n'
                f'- Core conditions remain untrue: {"; ".join(conditions[:2])}'
            ),
        }
        created = []
        for artifact_type, content in artifacts.items():
            created.append(
                GeneratedArtifact.objects.create(
                    project=project,
                    snapshot=snapshot,
                    artifact_type=artifact_type,
                    title=artifact_type.replace('_', ' ').title(),
                    content=content,
                    metadata_json={'decision': recommendation.decision, 'icp': icp},
                )
            )
        return created
