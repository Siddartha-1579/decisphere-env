// src/lib/simulation.ts
// DeciSphere AI → frontend + FastAPI backend hybrid simulation engine

export interface Task {
  id: string;
  name: string;
  priority: "Critical" | "High" | "Low";
  tags: string[];
  deadline?: string;
  riskLevel?: "Risk" | "Dependency";
}

export interface Agent {
  name: string;
  badge?: string;
  avgReward: number;
  efficiency: string;
  riskMgmt: string;
  grade: string;
  status: string;
}

export interface ApiStatus {
  name: string;
  status: "connected" | "verified" | "ready" | "active";
  detail?: string;
}

export interface SimState {
  step: number;
  maxSteps: number;
  totalReward: number;
  riskScore: number;
  budgetHealth: number;
  taskEfficiency: number;
  resourceLoad: number;
  escalations: number;
  computeUsage: number;
  activeStaff: number;
  budgetLeft: number;
  timeRemaining: string;
  episode: string;
  status: "In Progress" | "Completed" | "Failed";
  tasks: Task[];
  rewardHistory: { step: number; reward: number }[];
  actionDistribution: { name: string; value: number }[];
  agents: Agent[];
  apiHealth: ApiStatus[];
}

export type Action =
  | "prioritize"
  | "delay"
  | "allocate"
  | "ignore"
  | "escalate";

type BackendResponse = Record<string, unknown>;

const API_BASE = "http://127.0.0.1:7860";

// -------------------------------------
// Mock initial state
// -------------------------------------
const INITIAL_TASKS: Task[] = [
  { id: "1", name: "Urgent Shipment", priority: "High", tags: [] },
  {
    id: "2",
    name: "Supplier Approval",
    priority: "High",
    tags: ["Dependency"],
  },
  { id: "3", name: "System Update", priority: "Low", tags: ["Planning"] },
  { id: "4", name: "Budget Review", priority: "Critical", tags: [] },
  { id: "5", name: "Client Escalation", priority: "High", tags: [] },
];

export function createInitialState(): SimState {
  return {
    step: 0,
    maxSteps: 50,
    totalReward: 0,
    riskScore: 50,
    budgetHealth: 80,
    taskEfficiency: 70,
    resourceLoad: 60,
    escalations: 0,
    computeUsage: 50,
    activeStaff: 24,
    budgetLeft: 50000,
    timeRemaining: "05:00",
    episode: "Operations Management",
    status: "In Progress",
    tasks: [...INITIAL_TASKS],
    rewardHistory: [],
    actionDistribution: [],
    agents: [
      {
        name: "RuleBasedAgent",
        badge: "RLHF",
        avgReward: 1120,
        efficiency: "78%",
        riskMgmt: "B+",
        grade: "Active",
        status: "Active",
      },
    ],
    apiHealth: [
      { name: "FastAPI Connected", status: "connected" },
      { name: "OpenEnv Verified", status: "verified" },
    ],
  };
}

// -------------------------------------
// Convert backend response → frontend state
// -------------------------------------
function mapBackendToFrontend(data: BackendResponse): SimState {
  const step = typeof data.step === "number" ? data.step : 0;
  const maxSteps =
    typeof data.max_steps === "number" ? data.max_steps : 50;
  const totalReward =
    typeof data.total_reward === "number" ? data.total_reward : 0;
  const riskLevel =
    typeof data.risk_level === "number" ? data.risk_level : 0.5;
  const budgetRemaining =
    typeof data.budget_remaining === "number"
      ? data.budget_remaining
      : 50000;
  const correctness =
    typeof data.correctness === "number" ? data.correctness : 0.7;
  const escalationsUsed =
    typeof data.escalations_used === "number"
      ? data.escalations_used
      : 0;
  const taskName =
    typeof data.task_name === "string"
      ? data.task_name
      : "DecisionEnv Live";
  const done = typeof data.done === "boolean" ? data.done : false;

  const rewardHistory = Array.isArray(data.reward_history)
    ? (data.reward_history as { step: number; reward: number }[])
    : [];

  const actionDistribution = Array.isArray(data.action_distribution)
    ? (data.action_distribution as { name: string; value: number }[])
    : [];

  return {
    step,
    maxSteps,
    totalReward,
    riskScore: Math.round(riskLevel * 100),
    budgetHealth: Math.max(
      0,
      Math.min(100, (budgetRemaining / 50000) * 100)
    ),
    taskEfficiency: Math.round(correctness * 100),
    resourceLoad: 65,
    escalations: escalationsUsed,
    computeUsage: 60,
    activeStaff: 24,
    budgetLeft: budgetRemaining,
    timeRemaining: "04:30",
    episode: taskName,
    status: done ? "Completed" : "In Progress",
    tasks: [...INITIAL_TASKS],
    rewardHistory,
    actionDistribution,
    agents: [
      {
        name: "DecisionEnv Agent",
        badge: "LIVE",
        avgReward: totalReward,
        efficiency: `${Math.round(correctness * 100)}%`,
        riskMgmt: "A",
        grade: "Connected",
        status: "Live",
      },
    ],
    apiHealth: [
      { name: "FastAPI Connected", status: "connected" },
      { name: "Backend Live", status: "active" },
      { name: "OpenEnv Verified", status: "verified" },
      { name: "Latency: Live", status: "ready" },
    ],
  };
}

// -------------------------------------
// Backend calls with numeric action mapping
// -------------------------------------
export async function tryBackendStep(
  action: Action
): Promise<SimState | null> {
  const actionMap: Record<Action, number> = {
    prioritize: 0,
    delay: 1,
    allocate: 2,
    ignore: 3,
    escalate: 4,
  };

  try {
    const backendAction = actionMap[action];
    const res = await fetch(`${API_BASE}/step/${backendAction}`);

    if (!res.ok) return null;

    const data: BackendResponse = await res.json();
    return mapBackendToFrontend(data);
  } catch {
    return null;
  }
}

export async function tryBackendReset(): Promise<SimState | null> {
  try {
    const res = await fetch(`${API_BASE}/reset`);

    if (!res.ok) return null;

    const data: BackendResponse = await res.json();
    return mapBackendToFrontend(data);
  } catch {
    return null;
  }
}

export async function tryBackendStatus(): Promise<SimState | null> {
  try {
    const res = await fetch(`${API_BASE}/`);

    if (!res.ok) return null;

    const data: BackendResponse = await res.json();
    return mapBackendToFrontend(data);
  } catch {
    return null;
  }
}

// -------------------------------------
// Mock fallback local simulation
// -------------------------------------
export function stepSimulation(state: SimState, action: Action): SimState {
  const rewardGain = Math.floor(20 + Math.random() * 50);
  const newStep = state.step + 1;

  return {
    ...state,
    step: newStep,
    totalReward: state.totalReward + rewardGain,
    riskScore: Math.max(0, state.riskScore - 2),
    budgetLeft: state.budgetLeft - 1000,
    rewardHistory: [
      ...state.rewardHistory,
      { step: newStep, reward: rewardGain },
    ],
    actionDistribution: [
      ...state.actionDistribution,
      {
        name: action.charAt(0).toUpperCase() + action.slice(1),
        value: 1,
      },
    ],
    status: newStep >= state.maxSteps ? "Completed" : "In Progress",
  };
}

export function resetSimulation(): SimState {
  return createInitialState();
}