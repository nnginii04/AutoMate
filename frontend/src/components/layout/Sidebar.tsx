import { NAV_ITEMS, type PageId } from '../../utils/constants';

type SidebarProps = {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
};

const navIcons: Record<PageId, string> = {
  agent: '⚡',
  logs: '📋',
  evaluation: '📊',
};

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-border bg-surface shadow-card">
      <div className="border-b border-border px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-lg">
            🚗
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-foreground">
              AutoMate
            </h1>
            <p className="text-xs text-secondary">Mobility AI Agent</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {NAV_ITEMS.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`flex w-full items-center gap-3 rounded-xl border-l-[3px] px-3 py-3 text-left text-sm transition-all ${
                isActive
                  ? 'border-l-primary bg-primary-soft text-primary'
                  : 'border-l-transparent text-secondary hover:bg-surface-soft hover:text-foreground'
              }`}
            >
              <span className="text-base" aria-hidden>
                {navIcons[item.id]}
              </span>
              <div>
                <div className="font-semibold">{item.label}</div>
                <div className="text-xs opacity-80">{item.description}</div>
              </div>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-border px-6 py-5">
        <p className="text-xs font-medium text-secondary">Connected Vehicle AI</p>
        <p className="text-xs text-muted">Prototype v0.1.0</p>
      </div>
    </aside>
  );
}
