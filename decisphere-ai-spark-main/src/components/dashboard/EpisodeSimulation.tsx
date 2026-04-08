import { SimState, Action } from '@/lib/simulation';
import { motion } from 'framer-motion';

interface Props {
  state: SimState;
  onAction: (action: Action) => void;
  onReset: () => void;
  isLoading: boolean;
  isBackendConnected: boolean;
}

const ACTIONS: { label: string; value: Action }[] = [
  { label: 'Prioritize', value: 'prioritize' },
  { label: 'Delay', value: 'delay' },
  { label: 'Allocate', value: 'allocate' },
  { label: 'Ignore', value: 'ignore' },
  { label: 'Escalate', value: 'escalate' },
];

export default function EpisodeSimulation({
  state,
  onAction,
  onReset,
  isLoading,
  isBackendConnected,
}: Props) {
  const progress =
    state.maxSteps > 0 ? (state.step / state.maxSteps) * 100 : 0;

  const latestReward =
    state.rewardHistory.length > 0
      ? state.rewardHistory[state.rewardHistory.length - 1].reward
      : 0;

  const handleStartSimulation = () => {
    if (state.status !== 'Completed') {
      onAction('prioritize');
    }
  };

  const handleViewBenchmarks = () => {
    const section = document.getElementById('benchmark-section');
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="ds-card p-6 flex flex-col gap-5 h-full"
    >
      {/* Top controls */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <span className="text-xs text-muted-foreground font-medium">
            Current Episode:{' '}
          </span>
          <span className="text-sm font-semibold text-foreground">
            {state.episode}
          </span>
        </div>

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={handleStartSimulation}
            disabled={isLoading || state.status === 'Completed'}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold text-primary-foreground ds-gradient-bg transition-all hover:opacity-90 disabled:opacity-50"
            style={{ background: 'var(--ds-gradient-primary)' }}
          >
            {isLoading ? 'Running...' : 'Start Simulation'}
          </button>

          <button
            onClick={onReset}
            disabled={isLoading}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold border border-border text-foreground hover:bg-muted transition-colors disabled:opacity-50"
          >
            Reset Episode
          </button>

          <button
            onClick={handleViewBenchmarks}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold border border-border text-foreground hover:bg-muted transition-colors"
          >
            View Benchmarks
          </button>
        </div>
      </div>

      {/* Episode card */}
      <div className="ds-card-elevated p-6 flex flex-col items-center gap-4">
        <h2 className="font-display text-lg font-bold text-foreground">
          Current Episode: {state.episode}
        </h2>

        <div className="flex items-center gap-8 text-sm flex-wrap justify-center">
          <div>
            <span className="text-muted-foreground">Step: </span>
            <span className="font-bold font-display">
              {state.step} / {state.maxSteps}
            </span>
          </div>

          <div>
            <span className="text-muted-foreground">Total Reward: </span>
            <span className="font-bold font-display">
              {state.totalReward}
            </span>
            <span className="ml-2 text-xs text-ds-success">
              (+{latestReward})
            </span>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-bold ${
              state.status === 'In Progress'
                ? 'text-primary-foreground'
                : state.status === 'Completed'
                ? 'bg-ds-success/20 text-ds-success'
                : 'bg-ds-critical/20 text-ds-critical'
            }`}
            style={
              state.status === 'In Progress'
                ? {
                    background:
                      'linear-gradient(135deg, hsl(187 100% 50%), hsl(217 91% 60%))',
                  }
                : {}
            }
          >
            {state.status}
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'var(--ds-gradient-primary)' }}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>

        {/* Action buttons */}
        <div className="flex gap-3 flex-wrap justify-center">
          {ACTIONS.map((action, i) => (
            <button
              key={action.value}
              disabled={isLoading || state.status === 'Completed'}
              onClick={() => onAction(action.value)}
              className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-40 ${
                i === 0
                  ? 'text-primary-foreground shadow-md hover:shadow-lg'
                  : 'bg-card border border-border text-foreground hover:bg-muted'
              }`}
              style={
                i === 0
                  ? { background: 'var(--ds-gradient-primary)' }
                  : {}
              }
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Connection status */}
      <div className="flex items-center gap-2 justify-center">
        <div
          className={`w-2 h-2 rounded-full ${
            isBackendConnected ? 'bg-ds-success' : 'bg-ds-warning'
          }`}
        />
        <span className="text-[11px] text-muted-foreground">
          {isBackendConnected
            ? 'Backend Connected'
            : 'Mock Simulation Mode'}
        </span>
      </div>
    </motion.div>
  );
}