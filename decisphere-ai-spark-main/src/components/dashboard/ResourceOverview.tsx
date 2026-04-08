import { SimState } from '@/lib/simulation';
import { motion } from 'framer-motion';

function RadialProgress({ value, label, color, size = 48 }: { value: number; label: string; color: string; size?: number }) {
  const r = (size - 8) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (value / 100) * c;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg viewBox={`0 0 ${size} ${size}`} className="w-full h-full -rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="hsl(220 13% 91%)" strokeWidth="4" />
        <motion.circle
          cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="4"
          strokeLinecap="round" strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.8 }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-[9px] font-bold text-foreground">{value}%</span>
      </div>
    </div>
  );
}

export default function ResourceOverview({ state }: { state: SimState }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="ds-card p-5 flex flex-col gap-4"
    >
      <h3 className="font-display font-bold text-sm text-foreground">Resource Overview</h3>

      <div className="flex items-center gap-4">
        <RadialProgress value={state.computeUsage} label="Compute" color="#22c55e" />
        <div>
          <div className="text-lg font-bold font-display">{state.activeStaff}</div>
          <div className="text-[10px] text-muted-foreground">Active Staff</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <RadialProgress value={Math.min(100, Math.round((state.budgetLeft / 60000) * 100))} label="Budget" color="#3b82f6" />
        <div>
          <div className="text-lg font-bold font-display">${(state.budgetLeft / 1000).toFixed(1)}K</div>
          <div className="text-[10px] text-muted-foreground">Budget Left</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
          <span className="text-xs font-bold text-foreground">{state.timeRemaining}</span>
        </div>
        <div>
          <div className="text-sm font-semibold">{state.timeRemaining}</div>
          <div className="text-[10px] text-muted-foreground">Time Remaining</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <RadialProgress value={Math.min(100, state.escalations * 15)} label="Escalations" color="#a855f7" />
        <div>
          <div className="text-lg font-bold font-display">{state.escalations}</div>
          <div className="text-[10px] text-muted-foreground">Escalations</div>
        </div>
      </div>
    </motion.div>
  );
}
