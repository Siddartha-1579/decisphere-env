import { SimState } from '@/lib/simulation';
import {
  BarChart3,
  ShieldAlert,
  Heart,
  Zap,
  Server,
  AlertTriangle,
} from 'lucide-react';
import { Area, AreaChart, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

interface KPICardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  delta: string;
  deltaType: 'up' | 'down';
  sparkData: number[];
  sparkColor: string;
  index: number;
}

function KPICard({
  icon,
  label,
  value,
  delta,
  deltaType,
  sparkData,
  sparkColor,
  index,
}: KPICardProps) {
  const data = sparkData.map((v, i) => ({ i, v }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.4 }}
      className="ds-card px-5 py-4 flex flex-col gap-2 min-w-[180px] flex-1"
    >
      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wider">
          {label}
        </span>
      </div>

      <div className="flex items-end gap-3">
        <span className="text-2xl font-bold font-display text-foreground">
          {value}
        </span>
        <span
          className={`text-xs font-semibold ${
            deltaType === 'up' ? 'text-ds-success' : 'text-ds-critical'
          }`}
        >
          {deltaType === 'up' ? '▲' : '▼'} {delta}
        </span>
      </div>

      <div className="h-8 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient
                id={`spark-${label}`}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="0%" stopColor={sparkColor} stopOpacity={0.3} />
                <stop offset="100%" stopColor={sparkColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={sparkColor}
              fill={`url(#spark-${label})`}
              strokeWidth={2}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export default function KPIStrip({
  state,
}: {
  state: SimState | null | undefined;
}) {
  // ✅ Prevent white screen crash
  if (!state) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 px-8">
        <div className="col-span-full text-center text-muted-foreground py-10">
          Loading dashboard KPIs...
        </div>
      </div>
    );
  }

  const rewardHistory =
    state.rewardHistory?.slice(-8).map((r) => r.reward) ?? [0];

  const cards: Omit<KPICardProps, 'index'>[] = [
    {
      icon: <BarChart3 size={16} />,
      label: 'Live Reward',
      value: `$${(state.totalReward ?? 0).toLocaleString()}`,
      delta: '12%',
      deltaType: 'up',
      sparkData: rewardHistory,
      sparkColor: '#00d4ff',
    },
    {
      icon: <ShieldAlert size={16} />,
      label: 'Risk Score',
      value: String(state.riskScore ?? 0),
      delta: '8%',
      deltaType: 'down',
      sparkData: [80, 76, 74, 72, 75, 70, 72, state.riskScore ?? 0],
      sparkColor: '#ef4444',
    },
    {
      icon: <Heart size={16} />,
      label: 'Budget Health',
      value: `${state.budgetHealth ?? 0}%`,
      delta: '5%',
      deltaType: 'up',
      sparkData: [80, 82, 83, 85, 84, 86, 85, state.budgetHealth ?? 0],
      sparkColor: '#3b82f6',
    },
    {
      icon: <Zap size={16} />,
      label: 'Task Efficiency',
      value: `${state.taskEfficiency ?? 0}%`,
      delta: '10%',
      deltaType: 'up',
      sparkData: [85, 87, 88, 90, 89, 91, 90, state.taskEfficiency ?? 0],
      sparkColor: '#22c55e',
    },
    {
      icon: <Server size={16} />,
      label: 'Resource Load',
      value: `${state.resourceLoad ?? 0}%`,
      delta: '3%',
      deltaType: 'up',
      sparkData: [60, 62, 64, 65, 66, 67, 68, state.resourceLoad ?? 0],
      sparkColor: '#f59e0b',
    },
    {
      icon: <AlertTriangle size={16} />,
      label: 'Escalations',
      value: String(state.escalations ?? 0),
      delta: `${state.escalations ?? 0} Incidents`,
      deltaType: 'down',
      sparkData: [2, 3, 3, 4, 3, 4, 4, state.escalations ?? 0],
      sparkColor: '#a855f7',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 px-8">
      {cards.map((c, i) => (
        <KPICard key={c.label} {...c} index={i} />
      ))}
    </div>
  );
}