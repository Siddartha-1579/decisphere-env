import { SimState } from '@/lib/simulation';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

export default function RiskCenter({ state }: { state: SimState }) {
  const riskLevel = state.riskScore >= 70 ? 'High Risk' : state.riskScore >= 40 ? 'Medium Risk' : 'Low Risk';
  const circumference = 2 * Math.PI * 52;
  const dashoffset = circumference - (state.riskScore / 100) * circumference;

  // Mini node positions for dependency graph
  const nodes = [
    { x: 120, y: 30, r: 6, color: '#3b82f6' },
    { x: 170, y: 60, r: 4, color: '#a855f7' },
    { x: 145, y: 100, r: 5, color: '#00d4ff' },
    { x: 95, y: 90, r: 4, color: '#a855f7' },
    { x: 75, y: 50, r: 5, color: '#3b82f6' },
    { x: 170, y: 110, r: 3, color: '#ef4444' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="ds-card p-5 flex flex-col gap-4 h-full"
    >
      <h3 className="font-display font-bold text-sm text-foreground">Global Risk Center</h3>

      {/* Circular gauge */}
      <div className="flex justify-center">
        <div className="relative w-32 h-32">
          <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
            <defs>
              <linearGradient id="riskGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#00d4ff" />
                <stop offset="50%" stopColor="#a855f7" />
                <stop offset="100%" stopColor="#ec4899" />
              </linearGradient>
            </defs>
            <circle cx="60" cy="60" r="52" fill="none" stroke="hsl(220 13% 91%)" strokeWidth="8" />
            <motion.circle
              cx="60" cy="60" r="52" fill="none" stroke="url(#riskGrad)" strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: dashoffset }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-[10px] text-muted-foreground font-medium">{riskLevel}</span>
            <span className="text-3xl font-display font-bold text-foreground">{state.riskScore}</span>
          </div>
        </div>
      </div>

      {/* Dependency node mini viz */}
      <div className="relative h-28 w-full">
        <svg viewBox="0 0 220 130" className="w-full h-full">
          {/* Lines between nodes */}
          {nodes.slice(0, -1).map((n, i) => (
            <line key={i} x1={n.x} y1={n.y} x2={nodes[i + 1].x} y2={nodes[i + 1].y}
              stroke="hsl(220 13% 85%)" strokeWidth="1" />
          ))}
          {nodes.map((n, i) => (
            <motion.circle key={i} cx={n.x} cy={n.y} r={n.r} fill={n.color}
              initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.3 + i * 0.1 }}
            />
          ))}
        </svg>
        <div className="absolute bottom-1 left-0 flex items-center gap-1 text-[10px] text-muted-foreground">
          <span>📊</span> Deadline Breaches
          <div className="flex gap-0.5 ml-1">
            {['#ef4444', '#f59e0b', '#ef4444', '#f59e0b', '#3b82f6'].map((c, i) => (
              <div key={i} className="w-3 h-3 rounded-sm" style={{ backgroundColor: c }} />
            ))}
          </div>
        </div>
      </div>

      {/* Alert */}
      <div className="flex items-center gap-2 p-2 rounded-lg bg-red-50 border border-red-100">
        <AlertTriangle size={14} className="text-ds-critical" />
        <span className="text-xs font-medium text-foreground">Immediate Action Required</span>
        <span className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-ds-critical">Critical</span>
      </div>
    </motion.div>
  );
}
