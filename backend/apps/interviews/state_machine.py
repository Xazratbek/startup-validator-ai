from core.common.enums import InterviewPhase

PHASES = [
    InterviewPhase.CLARIFY,
    InterviewPhase.ICP,
    InterviewPhase.PAIN,
    InterviewPhase.ALTERNATIVES,
    InterviewPhase.MONETIZATION,
    InterviewPhase.ACQUISITION,
    InterviewPhase.EDGE,
    InterviewPhase.REVIEW,
]

QUESTION_BANK = {
    InterviewPhase.CLARIFY: [
        'Describe the product in one sentence: who is it for, what job does it do, and what outcome changes?',
        'What specific workflow or decision becomes meaningfully better if this product exists?',
    ],
    InterviewPhase.ICP: [
        'Who is the narrowest believable initial customer profile you could target first?',
        'Which buyer or user feels this most acutely, and what role or context are they in?',
    ],
    InterviewPhase.PAIN: [
        'How often does this problem happen, and what concrete cost does it create each week or month?',
        'What happens if they do nothing for the next 90 days?',
    ],
    InterviewPhase.ALTERNATIVES: [
        'What are they using instead today, including spreadsheets, agencies, or manual workarounds?',
        'Why are existing alternatives insufficient for this specific ICP?',
    ],
    InterviewPhase.MONETIZATION: [
        'Who signs off on budget, and why would paying for this outrank other priorities?',
        'What price range feels plausible based on ROI or current spend?',
    ],
    InterviewPhase.ACQUISITION: [
        'What repeatable channel could realistically deliver your first 25 customers?',
        'Where does this ICP already gather, search, or evaluate tools like this?',
    ],
    InterviewPhase.EDGE: [
        'What unique founder insight, access, expertise, or distribution edge do you have here?',
        'What major constraint could slow execution: regulation, trust, integrations, or domain credibility?',
    ],
    InterviewPhase.REVIEW: [
        'Which assumption is most dangerous to be wrong about before building, and how would you test it in 7 days?',
    ],
}

PHASE_FIELD_MAP = {
    InterviewPhase.CLARIFY: ('value_prop', 'idea_summary'),
    InterviewPhase.ICP: ('icp',),
    InterviewPhase.PAIN: ('problem_statement',),
    InterviewPhase.ALTERNATIVES: ('alternatives',),
    InterviewPhase.MONETIZATION: ('monetization_hypothesis',),
    InterviewPhase.ACQUISITION: ('acquisition_hypothesis',),
    InterviewPhase.EDGE: ('founder_edge', 'constraints'),
    InterviewPhase.REVIEW: ('founder_assumptions',),
}

def get_question(phase: str, answer_count: int = 0) -> str:
    variants = QUESTION_BANK[phase]
    return variants[min(answer_count, len(variants) - 1)]

def phase_completion_index(phase: str) -> int:
    if phase == InterviewPhase.COMPLETE:
        return 100
    return int(((PHASES.index(phase) + 1) / len(PHASES)) * 100)
