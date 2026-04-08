import { SimState } from '@/lib/simulation';
import { motion } from 'framer-motion';
import { CheckCircle2 } from 'lucide-react';

export default function BenchmarkLeaderboard({ state }: { state: SimState }) {
  if (!state) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="ds-card p-5 flex flex-col gap-4"
    >
      <h3 className="font-display font-bold text-sm text-foreground">Benchmark Leaderboard</h3>

      <div className="flex flex-col gap-3">
        {state?.apiHealth?.map((api) => (
          <div key={api.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={16} className="text-ds-success" />
              <span className="text-sm text-foreground font-medium">{api.name}</span>
            </div>
            <CheckCircle2 size={16} className="text-ds-success" />
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2 pt-2 border-t border-border">
        <div className="w-2 h-2 rounded-full bg-ds-success animate-pulse" />
        <span className="text-[11px] text-muted-foreground">Synced: 1 min ago</span>
      </div>
    </motion.div>
  );
}
