const links = [
  ['Dashboard / Boshqaruv','/dashboard'],['Yangi loyiha / New Project','/projects/new'],['Sozlamalar / Settings','/settings']
];
export function AppSidebar(){return <aside className="sidebar"><div className="stack"><h2 style={{fontFamily:'Unbounded'}}>Founder Validation OS</h2><p className="muted">Startup qaror tizimi · Decision workspace</p>{links.map(([label,href])=><a key={href} href={href} className="card" style={{display:'block'}}>{label}</a>)}</div></aside>}
