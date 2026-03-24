'use client';

import { useEffect, useState } from 'react';
import { AppSidebar } from '@/components/AppSidebar';
import { DecisionBadge } from '@/components/DecisionBadge';
import { apiFetch } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

export default function Dashboard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setError('Please log in first.');
      return;
    }
    apiFetch('/projects', { headers: { Authorization: `Bearer ${token}` } })
      .then(setProjects)
      .catch((err) => setError(err.message));
  }, []);

  return <div><AppSidebar /><main className="main stack"><h1>Dashboard</h1>{error ? <div className="card">{error}</div> : null}<div className="three-col">{projects.map(project=><a key={project.id} href={`/projects/${project.id}`} className="card"><div style={{display:'flex',justifyContent:'space-between'}}><strong>{project.title}</strong><DecisionBadge decision={project.current_decision} /></div><p className="muted">{project.idea_one_liner}</p></a>)}</div></main></div>;
}
