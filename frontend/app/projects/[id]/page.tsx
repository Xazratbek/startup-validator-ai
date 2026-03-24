'use client';

import { useEffect, useState } from 'react';
import { AppSidebar } from '@/components/AppSidebar';
import { ProjectHeader } from '@/components/ProjectHeader';
import { InterviewPhaseStepper } from '@/components/InterviewPhaseStepper';
import { InterviewChat } from '@/components/InterviewChat';
import { EvidenceTable } from '@/components/EvidenceTable';
import { CompetitorGrid } from '@/components/CompetitorGrid';
import { RiskFlagList } from '@/components/RiskFlagList';
import { RecommendationPanel } from '@/components/RecommendationPanel';
import { ArtifactTabs } from '@/components/ArtifactTabs';
import { VersionComparePanel } from '@/components/VersionComparePanel';
import { JobStatusBanner } from '@/components/JobStatusBanner';
import { ScoreCard } from '@/components/ScoreCard';
import { CitationList } from '@/components/CitationList';
import { apiFetch } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

export default function ProjectPage({ params }: { params: { id:string } }) {
  const [data, setData] = useState<any | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setError('Please log in first.');
      return;
    }
    Promise.all([
      apiFetch(`/projects/${params.id}`, { headers: { Authorization: `Bearer ${token}` } }),
      apiFetch(`/projects/${params.id}/interview`, { headers: { Authorization: `Bearer ${token}` } }),
      apiFetch(`/projects/${params.id}/research/latest`, { headers: { Authorization: `Bearer ${token}` } }),
      apiFetch(`/projects/${params.id}/scores/latest`, { headers: { Authorization: `Bearer ${token}` } }),
      apiFetch(`/projects/${params.id}/recommendation/latest`, { headers: { Authorization: `Bearer ${token}` } }),
      apiFetch(`/projects/${params.id}/artifacts`, { headers: { Authorization: `Bearer ${token}` } }),
      apiFetch(`/projects/${params.id}/history`, { headers: { Authorization: `Bearer ${token}` } }),
    ]).then(([project, interview, research, score, recommendation, artifacts, history]) => {
      setData({ project, interview, research, score, recommendation, artifacts, history });
    }).catch((err) => setError(err.message));
  }, [params.id]);

  if (error) return <div><AppSidebar /><main className="main"><div className="card">{error}</div></main></div>;
  if (!data) return <div><AppSidebar /><main className="main"><div className="card">Loading workspace...</div></main></div>;
  const scoreEntries = Object.entries(data.score.dimension_scores_json || {});
  return <div><AppSidebar /><main className="main stack"><ProjectHeader project={data.project} /><JobStatusBanner status={data.research.status} /><InterviewPhaseStepper current={data.interview.current_phase} /><div className="three-col">{scoreEntries.map(([key, value]: any)=><ScoreCard key={key} title={key} score={value.score} explanation={value.explanation} />)}</div><RiskFlagList risks={data.score.risk_flags_json || []} /><RecommendationPanel recommendation={data.recommendation} /><EvidenceTable items={data.research.evidence_items || []} /><CitationList items={data.research.evidence_items || []} /><CompetitorGrid competitors={data.research.competitors || []} /><ArtifactTabs artifacts={data.artifacts} /><InterviewChat session={data.interview} /><VersionComparePanel history={data.history.history || []} /></main></div>;
}
