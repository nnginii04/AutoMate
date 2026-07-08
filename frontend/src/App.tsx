import { useState } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { AgentPage } from './pages/AgentPage';
import { LogsPage } from './pages/LogsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { ScenarioRunnerPage } from './pages/ScenarioRunnerPage';
import { PAGE_IDS, type PageId } from './utils/constants';

function renderPage(page: PageId) {
  switch (page) {
    case PAGE_IDS.AGENT:
      return <AgentPage />;
    case PAGE_IDS.LOGS:
      return <LogsPage />;
    case PAGE_IDS.EVALUATION:
      return <EvaluationPage />;
    case PAGE_IDS.SCENARIOS:
      return <ScenarioRunnerPage />;
    default:
      return <AgentPage />;
  }
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageId>(PAGE_IDS.AGENT);

  return (
    <AppLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderPage(currentPage)}
    </AppLayout>
  );
}
