import { SimState } from '@/lib/simulation';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const PIE_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#a855f7'];

type ActionItem = {
  name: string;
  value: number;
};

type AgentItem = SimState['agents'][number];

export default function RewardAnalysis({
  state,
}: {
  state: SimState | null;
}) {
  if (!state) return null;

  const rewardHistory = state.rewardHistory || [];
  const actionDistribution: ActionItem[] = state.actionDistribution || [];
  const agents: AgentItem[] = state.agents || [];

  const totalActions = actionDistribution.reduce(
    (sum, item) => sum + item.value,
    0
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.25 }}
      className="ds-card p-5 flex flex-col gap-4"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-display font-bold text-sm text-foreground">
          Reward Analysis
        </h3>
        <span className="text-xs text-muted-foreground">
          Action Distribution: {totalActions}
        </span>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 h-40">
          <div className="text-[10px] text-muted-foreground mb-1">
            Reward Over Time
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={rewardHistory}>
              <defs>
                <linearGradient id="rewardGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="step" tick={false} axisLine={false} />
              <YAxis tick={{ fontSize: 9 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
              <Area
                type="monotone"
                dataKey="reward"
                stroke="#3b82f6"
                fill="url(#rewardGrad)"
                strokeWidth={2}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="w-36 h-40 flex flex-col items-center justify-center">
          <ResponsiveContainer width="100%" height="80%">
            <PieChart>
              <Pie
                data={actionDistribution}
                dataKey="value"
                cx="50%"
                cy="50%"
                outerRadius={45}
                innerRadius={20}
              >
                {actionDistribution.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>

          <div className="flex flex-wrap gap-x-2 gap-y-0.5 justify-center">
            {actionDistribution.map((a, i) => (
              <div key={a.name} className="flex items-center gap-1">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: PIE_COLORS[i % PIE_COLORS.length],
                  }}
                />
                <span className="text-[8px] text-muted-foreground">
                  {a.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <tbody>
            {agents.map((agent) => (
              <tr key={agent.name}>
                <td>{agent.name}</td>
                <td>{agent.avgReward}</td>
                <td>{agent.efficiency}</td>
                <td>{agent.riskMgmt}</td>
                <td>{agent.grade}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}