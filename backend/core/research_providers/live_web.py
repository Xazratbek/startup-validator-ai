from __future__ import annotations

import re
from collections import defaultdict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from core.research_providers.base import ResearchDocument, ResearchQuery

USER_AGENT = 'FounderValidationOS/1.0 (+https://localhost)'

CATEGORY_HINTS = {
    'COMPETITOR': ['alternative', 'software', 'platform', 'tool'],
    'MARKET': ['market', 'industry', 'growth', 'trend'],
    'PAIN': ['pain', 'complaint', 'workflow', 'problem'],
    'PRICING': ['pricing', 'price', 'plans'],
    'SEARCH': ['search', 'trend', 'keyword', 'demand'],
    'RISK': ['regulation', 'compliance', 'risk', 'security'],
}

class LiveWebResearchProvider:
    search_url = 'https://html.duckduckgo.com/html/'

    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def collect(self, project_title: str, profile: dict, queries: list[ResearchQuery]) -> list[ResearchDocument]:
        documents: list[ResearchDocument] = []
        seen_urls: set[str] = set()
        for query in queries:
            for result in self._search(query.query)[:4]:
                if result['url'] in seen_urls:
                    continue
                seen_urls.add(result['url'])
                page = self._fetch_page(result['url'])
                snippet = page.get('snippet') or result['snippet']
                claim = self._build_claim(query.category, profile, result['title'], snippet)
                confidence = self._score_confidence(result['url'], snippet)
                documents.append(
                    ResearchDocument(
                        title=result['title'],
                        source_name=result['source_name'],
                        url=result['url'],
                        snippet=snippet[:600],
                        category=query.category,
                        confidence=confidence,
                        claim=claim,
                        citation_metadata={
                            'query': query.query,
                            'matched_terms': self._matched_terms(query.category, snippet),
                            'excerpt': snippet[:220],
                        },
                    )
                )
        return self._dedupe(documents)

    def _search(self, query: str) -> list[dict]:
        response = self.session.post(self.search_url, data={'q': query}, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('.result'):
            link = item.select_one('.result__a')
            snippet = item.select_one('.result__snippet')
            if not link or not link.get('href'):
                continue
            url = link['href']
            results.append({
                'title': link.get_text(' ', strip=True),
                'url': url,
                'snippet': snippet.get_text(' ', strip=True) if snippet else '',
                'source_name': urlparse(url).netloc or 'web',
            })
        return results

    def _fetch_page(self, url: str) -> dict:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = [p.get_text(' ', strip=True) for p in soup.select('p')[:8]]
            title = soup.title.get_text(' ', strip=True) if soup.title else url
            return {'title': title, 'snippet': ' '.join(paragraphs)[:1200]}
        except Exception:
            return {'title': url, 'snippet': ''}

    def _build_claim(self, category: str, profile: dict, title: str, snippet: str) -> str:
        icp = profile.get('icp') or 'target users'
        problem = profile.get('problem_statement') or profile.get('idea_summary') or 'the workflow problem'
        short = snippet[:220] or title
        templates = {
            'COMPETITOR': f'The market already contains active alternatives serving {icp}; differentiation must be explicit. Evidence: {short}',
            'MARKET': f'Market signals indicate ongoing activity relevant to {problem}. Evidence: {short}',
            'PAIN': f'Users discussing {problem} show recurring pain or friction. Evidence: {short}',
            'PRICING': f'Pricing references suggest buyers expect paid solutions in this category. Evidence: {short}',
            'SEARCH': f'Search-visible content suggests discoverable intent around {problem}. Evidence: {short}',
            'RISK': f'Operational or regulatory constraints may affect delivery for {problem}. Evidence: {short}',
        }
        return templates.get(category, short)

    def _score_confidence(self, url: str, snippet: str) -> float:
        domain = urlparse(url).netloc
        authority_bonus = 0.15 if any(domain.endswith(tld) for tld in ['.gov', '.edu', '.org']) else 0.0
        length_bonus = min(0.2, len(snippet) / 1500)
        return round(min(0.95, 0.45 + authority_bonus + length_bonus), 2)

    def _matched_terms(self, category: str, snippet: str) -> list[str]:
        text = snippet.lower()
        return [term for term in CATEGORY_HINTS.get(category, []) if term in text]

    def _dedupe(self, documents: list[ResearchDocument]) -> list[ResearchDocument]:
        grouped: dict[tuple[str, str], ResearchDocument] = {}
        for doc in documents:
            key = (doc.category, re.sub(r'^www\.', '', urlparse(doc.url).netloc))
            if key not in grouped or grouped[key].confidence < doc.confidence:
                grouped[key] = doc
        return list(grouped.values())
