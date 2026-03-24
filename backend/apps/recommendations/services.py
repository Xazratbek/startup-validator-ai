from __future__ import annotations

from core.common.enums import DecisionType
from .models import Recommendation

class RecommendationEngine:
    @staticmethod
    def generate(project, snapshot, scoring_result):
        score = scoring_result.total_score
        risks = scoring_result.risk_flags_json
        profile = snapshot.structured_json if snapshot else {}
        if score >= 78 and len(risks) <= 2:
            decision = DecisionType.BUILD_NOW
        elif 'vague ICP' in risks and score >= 58:
            decision = DecisionType.NARROW_NICHE
        elif score >= 58:
            decision = DecisionType.RUN_VALIDATION_FIRST
        elif score >= 42 and ('weak differentiation' in risks or 'weak monetization' in risks):
            decision = DecisionType.PIVOT
        else:
            decision = DecisionType.KILL
        strengths = RecommendationEngine._strengths(scoring_result)
        weaknesses = RecommendationEngine._weaknesses(scoring_result)
        blockers = RecommendationEngine._blockers(profile, risks)
        conditions = RecommendationEngine._conditions(profile)
        reasoning = (
            f'Total score is {score}/100. Highest-confidence strengths are {", ".join(strengths[:2])}. '
            f'Primary weaknesses are {", ".join(weaknesses[:2])}. '
            f'Decision: {decision}.'
        )
        return Recommendation.objects.create(
            project=project,
            snapshot=snapshot,
            scoring_result=scoring_result,
            decision=decision,
            reasoning=reasoning,
            strengths_json=strengths,
            weaknesses_json=weaknesses,
            blockers_json=blockers,
            conditions_json=conditions,
        )

    @staticmethod
    def _strengths(scoring_result):
        ranked = sorted(scoring_result.dimension_scores_json.items(), key=lambda item: item[1]['score'], reverse=True)
        return [f"{name.replace('_', ' ')} scored {payload['score']}/10" for name, payload in ranked[:3]]

    @staticmethod
    def _weaknesses(scoring_result):
        ranked = sorted(scoring_result.dimension_scores_json.items(), key=lambda item: item[1]['score'])
        return [f"{name.replace('_', ' ')} scored {payload['score']}/10" for name, payload in ranked[:3]]

    @staticmethod
    def _blockers(profile, risks):
        blockers = []
        if 'vague ICP' in risks:
            blockers.append('Define a narrower initial ICP before building broad product scope.')
        if 'weak monetization' in risks:
            blockers.append('Get direct willingness-to-pay signals from target buyers.')
        if 'no clear channel' in risks:
            blockers.append('Prove one repeatable acquisition path with real outreach.')
        if 'regulatory risk' in risks:
            blockers.append('Assess compliance obligations before promising delivery timelines.')
        return blockers or ['Run customer interviews and pricing tests before major build investment.']

    @staticmethod
    def _conditions(profile):
        icp = profile.get('icp') or 'your ICP'
        return [
            f'{icp} must acknowledge this problem as urgent enough to change behavior now.',
            'At least one outreach channel must produce repeatable conversations or signups.',
            'The value proposition must outperform current alternatives on speed, cost, or outcomes.',
        ]
