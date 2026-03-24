from django.db import models

class ProjectStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    INTERVIEWING = 'INTERVIEWING', 'Interviewing'
    RESEARCHING = 'RESEARCHING', 'Researching'
    SCORED = 'SCORED', 'Scored'
    DECIDED = 'DECIDED', 'Decided'

class DecisionType(models.TextChoices):
    BUILD_NOW = 'BUILD_NOW', 'Build now'
    RUN_VALIDATION_FIRST = 'RUN_VALIDATION_FIRST', 'Run validation first'
    NARROW_NICHE = 'NARROW_NICHE', 'Narrow niche'
    PIVOT = 'PIVOT', 'Pivot'
    KILL = 'KILL', 'Kill'

class InterviewPhase(models.TextChoices):
    CLARIFY = 'CLARIFY', 'Clarify the idea'
    ICP = 'ICP', 'Identify target user'
    PAIN = 'PAIN', 'Pain intensity'
    ALTERNATIVES = 'ALTERNATIVES', 'Existing alternatives'
    MONETIZATION = 'MONETIZATION', 'Willingness to pay'
    ACQUISITION = 'ACQUISITION', 'Distribution'
    EDGE = 'EDGE', 'Founder edge'
    REVIEW = 'REVIEW', 'Assumption review'
    COMPLETE = 'COMPLETE', 'Complete'

class InterviewRole(models.TextChoices):
    SYSTEM = 'SYSTEM', 'System'
    ASSISTANT = 'ASSISTANT', 'Assistant'
    USER = 'USER', 'User'

class ResearchRunStatus(models.TextChoices):
    QUEUED = 'QUEUED', 'Queued'
    RUNNING = 'RUNNING', 'Running'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'

class ArtifactType(models.TextChoices):
    INTERVIEW_SCRIPT = 'INTERVIEW_SCRIPT', 'Customer interview script'
    OUTREACH_DM = 'OUTREACH_DM', 'Cold outreach DM'
    OUTREACH_EMAIL = 'OUTREACH_EMAIL', 'Cold outreach email'
    LANDING_PAGE = 'LANDING_PAGE', 'Landing page copy'
    MVP_SCOPE = 'MVP_SCOPE', 'MVP scope'
    VALIDATION_PLAN = 'VALIDATION_PLAN', '7-day validation plan'
    CHECKLIST = 'CHECKLIST', 'Experiment checklist'
    METRICS = 'METRICS', 'Success metrics'

class EvidenceType(models.TextChoices):
    COMPETITOR = 'COMPETITOR', 'Competitor'
    MARKET = 'MARKET', 'Market signal'
    PAIN = 'PAIN', 'Pain signal'
    PRICING = 'PRICING', 'Pricing'
    SEARCH = 'SEARCH', 'Search demand'
    RISK = 'RISK', 'Risk'
