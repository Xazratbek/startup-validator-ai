export function JobStatusBanner({ status }: { status?: string }) { return <div className="card">Research job status: <strong>{status || 'IDLE'}</strong></div>; }
