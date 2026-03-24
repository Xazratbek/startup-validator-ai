export function DecisionBadge({ decision }: { decision?: string }) { return <span className="badge">{decision || 'IN_PROGRESS'}</span>; }
