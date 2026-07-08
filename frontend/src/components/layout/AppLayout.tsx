import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import type { PageId } from '../../utils/constants';

type AppLayoutProps = {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
  children: ReactNode;
};

export function AppLayout({
  currentPage,
  onNavigate,
  children,
}: AppLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
      <main className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto px-8 py-8">
          <div className="mx-auto w-full max-w-console">{children}</div>
        </div>
      </main>
    </div>
  );
}
