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
    <div className="flex h-screen overflow-hidden bg-app text-foreground">
      <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
      <main className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto px-6 py-8 lg:px-10 lg:py-10">
          {children}
        </div>
      </main>
    </div>
  );
}
