import { useSimulation } from '@/hooks/useSimulation';
import Header from '@/components/dashboard/Header';
import KPIStrip from '@/components/dashboard/KPIStrip';
import TaskQueue from '@/components/dashboard/TaskQueue';
import EpisodeSimulation from '@/components/dashboard/EpisodeSimulation';
import RiskCenter from '@/components/dashboard/RiskCenter';
import ResourceOverview from '@/components/dashboard/ResourceOverview';
import RewardAnalysis from '@/components/dashboard/RewardAnalysis';
import BenchmarkLeaderboard from '@/components/dashboard/BenchmarkLeaderboard';

export default function Index() {
  const {
    state,
    performAction,
    resetSimulation,
    loading,
  } = useSimulation();

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* KPI Strip */}
      <div className="mt-2">
        <KPIStrip state={state} />
      </div>

      {/* Main workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr_280px] gap-4 px-8 mt-6">
        <TaskQueue state={state} />

        <EpisodeSimulation
          state={state}
          onAction={performAction}
          onReset={resetSimulation}
          isLoading={loading}
          isBackendConnected={true}
        />

        <RiskCenter state={state} />
      </div>

      {/* Bottom analytics */}
      <div
        id="benchmark-section"
        className="grid grid-cols-1 md:grid-cols-3 gap-4 px-8 mt-6 pb-8"
      >
        <ResourceOverview state={state} />
        <RewardAnalysis state={state} />
        <BenchmarkLeaderboard state={state} />
      </div>
    </div>
  );
}