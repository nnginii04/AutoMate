import { Bot, BarChart3, FileText, FlaskConical } from 'lucide-react';
import { NAV_ITEMS, PAGE_IDS, type PageId } from '../../utils/constants';

type SidebarProps = {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
};

const NAV_ICONS: Record<PageId, typeof Bot> = {
  [PAGE_IDS.AGENT]: Bot,
  [PAGE_IDS.LOGS]: FileText,
  [PAGE_IDS.EVALUATION]: BarChart3,
  [PAGE_IDS.SCENARIOS]: FlaskConical,
};

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-border bg-surface">
      <div className="border-b border-border px-5 py-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-graphite text-sm font-bold text-white">
            A
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-foreground">
              AutoMate
            </h1>
            <p className="text-[11px] text-muted">Vehicle AI Console</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 p-3">
        {NAV_ITEMS.map((item) => {
          const isActive = currentPage === item.id;
          const Icon = NAV_ICONS[item.id];
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`flex w-full items-center gap-2.5 rounded-lg border-l-[3px] px-2.5 py-2.5 text-left text-sm transition-colors ${
                isActive
                  ? 'border-l-primary bg-primary-soft text-primary'
                  : 'border-l-transparent text-secondary hover:bg-surface-soft hover:text-foreground'
              }`}
            >
              <Icon className="h-4 w-4 shrink-0" strokeWidth={2} />
              <div className="min-w-0">
                <div className="font-semibold leading-tight">{item.label}</div>
                <div className="truncate text-[11px] opacity-75">
                  {item.description}
                </div>
              </div>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-border px-5 py-4">
        <p className="text-[10px] text-muted">AutoMate Prototype · v0.1</p>
      </div>
    </aside>
  );
}
