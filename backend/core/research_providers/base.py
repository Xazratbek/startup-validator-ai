from dataclasses import dataclass
from typing import Protocol

@dataclass
class ResearchDocument:
    title: str
    source_name: str
    url: str
    snippet: str
    category: str
    confidence: float
    claim: str
    citation_metadata: dict
    published_at: str | None = None

@dataclass
class ResearchQuery:
    query: str
    category: str

class ResearchProvider(Protocol):
    def collect(self, project_title: str, profile: dict, queries: list[ResearchQuery]) -> list[ResearchDocument]: ...
