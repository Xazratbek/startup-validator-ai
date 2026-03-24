from __future__ import annotations

from .models import ScoringResult

WEIGHTS = {
    'problem_urgency': 0.14,
    'pain_frequency': 0.1,
    'clarity_of_icp': 0.1,
    'willingness_to_pay_likelihood': 0.12,
    'market_crowding': 0.08,
    'differentiation_strength': 0.1,
    'distribution_feasibility': 0.1,
    'technical_feasibility': 0.08,
    'founder_advantage': 0.1,
    'evidence_quality': 0.08,
}

class ScoringEngine:
    @staticmethod
    def compute(project, snapshot, research_run):
        profile = snapshot.structured_json if snapshot else {}
        evidence = list(research_run.evidence_items.all()) if research_run else []
        category_counts = {category: len([item for item in evidence if item.category == category]) for category in ['PAIN', 'PRICING', 'COMPETITOR', 'MARKET', 'SEARCH', 'RISK']}
        competitor_count = research_run.competitors.count() if research_run else 0

        problem_words = len((profile.get('problem_statement') or '').split())
        icp_words = len((profile.get('icp') or '').split())
        monetization_words = len((profile.get('monetization_hypothesis') or '').split())
        acquisition_words = len((profile.get('acquisition_hypothesis') or '').split())
        founder_words = len((profile.get('founder_edge') or '').split())

        dimensions = {
            'problem_urgency': ScoringEngine._dimension(min(9, 3 + problem_words // 4 + category_counts['PAIN']), 'Based on stated cost/frequency and observed pain evidence.'),
            'pain_frequency': ScoringEngine._dimension(min(9, 3 + category_counts['PAIN'] + (1 if 'weekly' in (profile.get('problem_statement') or '').lower() else 0)), 'Higher when repeated workflow pain appears in interview and research evidence.'),
            'clarity_of_icp': ScoringEngine._dimension(min(9, 2 + icp_words // 3), 'Specific ICP language increases score; broad labels reduce it.'),
            'willingness_to_pay_likelihood': ScoringEngine._dimension(min(9, 2 + monetization_words // 4 + category_counts['PRICING']), 'Driven by explicit budget logic and pricing evidence.'),
            'market_crowding': ScoringEngine._dimension(max(2, 8 - competitor_count), 'More visible competitors lower this score because the market looks crowded.'),
            'differentiation_strength': ScoringEngine._dimension(min(9, 2 + len((profile.get('value_prop') or '').split()) // 4 + founder_words // 6), 'Differentiation improves when the offer and founder angle are concrete.'),
            'distribution_feasibility': ScoringEngine._dimension(min(9, 2 + acquisition_words // 4 + category_counts['SEARCH']), 'Stronger when a repeatable early channel is named and discoverability exists.'),
            'technical_feasibility': ScoringEngine._dimension(6 if 'integration' in (profile.get('constraints') or '').lower() else 7, 'Defaults to moderate unless constraints point to significant complexity.'),
            'founder_advantage': ScoringEngine._dimension(min(9, 2 + founder_words // 4), 'Founder edge improves with direct domain access, experience, or credibility.'),
            'evidence_quality': ScoringEngine._dimension(min(9, 2 + len(evidence)), 'Quality rises with multi-category cited evidence, not just opinion.'),
        }
        total = round(sum(v['score'] * 10 * WEIGHTS[k] for k, v in dimensions.items()), 1)
        risks = []
        if dimensions['clarity_of_icp']['score'] <= 4:
            risks.append('vague ICP')
        if dimensions['willingness_to_pay_likelihood']['score'] <= 4:
            risks.append('weak monetization')
        if dimensions['market_crowding']['score'] <= 4:
            risks.append('crowded market')
        if dimensions['distribution_feasibility']['score'] <= 4:
            risks.append('no clear channel')
        if dimensions['differentiation_strength']['score'] <= 4:
            risks.append('weak differentiation')
        if dimensions['evidence_quality']['score'] <= 4:
            risks.append('low evidence confidence')
        if 'regulation' in (profile.get('constraints') or '').lower() or category_counts['RISK'] > 0:
            risks.append('regulatory risk')
        if dimensions['founder_advantage']['score'] <= 4:
            risks.append('founder has no edge')
        rationale = {
            'confidence_label': 'HIGH' if total >= 75 else 'MEDIUM' if total >= 55 else 'LOW',
            'category_counts': category_counts,
            'competitor_count': competitor_count,
        }
        return ScoringResult.objects.create(
            project=project,
            snapshot=snapshot,
            research_run=research_run,
            total_score=total,
            dimension_scores_json=dimensions,
            weights_json=WEIGHTS,
            risk_flags_json=risks,
            rationale_json=rationale,
        )

    @staticmethod
    def _dimension(score: int, explanation: str) -> dict:
        return {'score': max(0, min(10, int(score))), 'explanation': explanation}
