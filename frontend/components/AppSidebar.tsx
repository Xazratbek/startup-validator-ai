const links = [
  ['Dashboard','/dashboard'],['New Project','/projects/new'],['Settings','/settings']
];
export function AppSidebar(){return <aside className="sidebar"><div className="stack"><h2>Founder Validation OS</h2><p className="muted">Decision system for startup ideas</p>{links.map(([label,href])=><a key={href} href={href} className="card" style={{display:'block'}}>{label}</a>)}</div></aside>}
