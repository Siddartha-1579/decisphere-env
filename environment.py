"""
DecisionEnv: Core RL Environment for Multi-Domain AI Decision-Making Benchmark
Meta + Hugging Face OpenEnv Hackathon
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from domain_tasks import TaskPrioritization, ResourceAllocation, ComplexDecision, EmailTriage, CodeReview


@dataclass
class EnvState:
    """Represents the full environment state at any timestep."""
    task_id: int                        # Which domain task is active (1, 2, 3)
    step_count: int                     # Steps taken in current episode
    resources: Dict[str, float]         # Available resources
    task_queue: List[Dict]              # Pending tasks with metadata
    risk_level: float                   # Global risk level (0–1)
    budget_remaining: float             # Financial budget
    time_remaining: float               # Time budget
    completed_tasks: List[str]          # Task IDs completed
    missed_deadlines: int               # Number of missed deadlines
    escalation_count: int               # Times escalation was used
    domain_specific: Dict               # Task-specific state data
    episode_done: bool = False

    def to_vector(self) -> np.ndarray:
        """Flatten state to numeric observation vector."""
        task_urgencies = [t.get("urgency", 0) for t in self.task_queue[:5]]
        task_importances = [t.get("importance", 0) for t in self.task_queue[:5]]
        while len(task_urgencies) < 5:
            task_urgencies.append(0)
            task_importances.append(0)

        return np.array([
            self.task_id / 3.0,
            self.step_count / 50.0,
            self.resources.get("compute", 0) / 100.0,
            self.resources.get("staff", 0) / 10.0,
            self.risk_level,
            self.budget_remaining / 1000.0,
            self.time_remaining / 100.0,
            self.missed_deadlines / 10.0,
            self.escalation_count / 5.0,
            len(self.completed_tasks) / 10.0,
            *task_urgencies,
            *task_importances,
        ], dtype=np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# Action Space
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    0: "prioritize",    # Elevate a task to top priority
    1: "delay",         # Defer a task to later
    2: "allocate",      # Assign resources to a task
    3: "ignore",        # Skip / discard a task
    4: "escalate",      # Escalate to higher authority / more resources
}

ACTION_NAMES = list(ACTIONS.values())


# ─────────────────────────────────────────────────────────────────────────────
# Main Environment
# ─────────────────────────────────────────────────────────────────────────────

class DecisionEnv:
    """
    Multi-Domain AI Decision-Making Benchmark Environment.

    Three domain tasks of increasing complexity:
      Task 1 (Easy)   – Task Prioritization
      Task 2 (Medium) – Resource Allocation
      Task 3 (Hard)   – Complex Multi-Step Decision-Making
    """

    metadata = {"version": "1.0.0", "hackathon": "Meta + HuggingFace OpenEnv"}

    # Episode config
    MAX_STEPS = 30
    MAX_ESCALATIONS = 3

    def __init__(self, task_id: int = 1, seed: Optional[int] = None):
        """
        Args:
            task_id: 1 = Easy, 2 = Medium, 3 = Hard
            seed:    Random seed for reproducibility
        """
        assert task_id in (1, 2, 3), "task_id must be 1, 2, or 3"
        self.task_id = task_id
        self.seed = seed
        self._rng = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)

        # Instantiate domain task handlers
        self._tasks = {
            1: TaskPrioritization(rng=self._rng),
            2: ResourceAllocation(rng=self._rng),
            3: ComplexDecision(rng=self._rng),
            4: EmailTriage(rng=self._rng),
            5: CodeReview(rng=self._rng),
        }
        self._current_task = self._tasks[task_id]
        self._state: Optional[EnvState] = None
        self._history: List[Dict] = []

    # ── Gym-style API ─────────────────────────────────────────────────────────

    def reset(self) -> np.ndarray:
        """Reset the environment and return the initial observation."""
        domain_state = self._current_task.reset()

        self._state = EnvState(
            task_id=self.task_id,
            step_count=0,
            resources={
                "compute": self._rng.uniform(40, 100),
                "staff": self._rng.randint(3, 10),
            },
            task_queue=domain_state.get("task_queue", []),
            risk_level=self._rng.uniform(0.1, 0.4),
            budget_remaining=self._rng.uniform(500, 1000),
            time_remaining=self._rng.uniform(50, 100),
            completed_tasks=[],
            missed_deadlines=0,
            escalation_count=0,
            domain_specific=domain_state,
        )
        self._history = []
        return self._state.to_vector()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Apply action to the environment.

        Returns:
            observation: np.ndarray
            reward:      float
            done:        bool
            info:        Dict with diagnostics
        """
        assert self._state is not None, "Call reset() before step()"
        assert action in ACTIONS, f"Invalid action {action}"

        action_name = ACTIONS[action]
        self._state.step_count += 1

        # Delegate to domain task
        task_result = self._current_task.step(action_name, self._state)

        # ── Compute reward ────────────────────────────────────────────────────
        reward = self._compute_reward(action_name, task_result)

        # ── Update global state ───────────────────────────────────────────────
        self._apply_state_updates(action_name, task_result)

        # ── Check termination ─────────────────────────────────────────────────
        done = self._check_done(task_result)
        self._state.episode_done = done

        info = {
            "action": action_name,
            "task_id": self.task_id,
            "step": self._state.step_count,
            "reward": reward,
            "task_result": task_result,
            "resources": dict(self._state.resources),
            "risk_level": self._state.risk_level,
            "budget_remaining": self._state.budget_remaining,
            "missed_deadlines": self._state.missed_deadlines,
        }

        self._history.append({**info, "state_vec": self._state.to_vector().tolist()})
        return self._state.to_vector(), reward, done, info

    def state(self) -> EnvState:
        """Return the current environment state object."""
        return self._state

    def render(self) -> str:
        """Human-readable state summary."""
        s = self._state
        lines = [
            f"═══ DecisionEnv | Task {s.task_id} | Step {s.step_count}/{self.MAX_STEPS} ═══",
            f"  Budget Remaining : ${s.budget_remaining:.1f}",
            f"  Time Remaining   : {s.time_remaining:.1f}h",
            f"  Risk Level       : {s.risk_level:.2f}",
            f"  Compute          : {s.resources['compute']:.1f}%",
            f"  Staff            : {s.resources['staff']} people",
            f"  Tasks Completed  : {len(s.completed_tasks)}",
            f"  Missed Deadlines : {s.missed_deadlines}",
            f"  Escalations Used : {s.escalation_count}/{self.MAX_ESCALATIONS}",
        ]
        if s.task_queue:
            lines.append("  Task Queue:")
            for t in s.task_queue[:4]:
                lines.append(
                    f"    [{t.get('id','?')}] {t.get('name','?')} "
                    f"U={t.get('urgency',0):.1f} I={t.get('importance',0):.1f}"
                )
        return "\n".join(lines)

    @property
    def action_space_size(self) -> int:
        return len(ACTIONS)

    @property
    def observation_space_size(self) -> int:
        dummy = EnvState(
            task_id=1, step_count=0,
            resources={"compute": 0, "staff": 0},
            task_queue=[], risk_level=0,
            budget_remaining=0, time_remaining=0,
            completed_tasks=[], missed_deadlines=0,
            escalation_count=0, domain_specific={}
        )
        return len(dummy.to_vector())

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _compute_reward(self, action_name: str, task_result: Dict) -> float:
        """
        Sophisticated reward function:
          +base     for correct decisions
          +partial  for partially correct decisions
          +efficiency bonus for speed
          −penalty  for poor/risky decisions
          −deadline penalty for missed urgent tasks
        """
        reward = 0.0

        correctness = task_result.get("correctness", 0.5)   # 0–1
        is_risky    = task_result.get("is_risky", False)
        is_urgent   = task_result.get("task_urgent", False)
        task_done   = task_result.get("task_completed", False)

        # ① Base correctness reward (−1 to +2)
        reward += (correctness * 2.0) - 1.0

        # ② Task completion bonus
        if task_done:
            reward += 1.5

        # ③ Efficiency bonus: fewer steps = better
        steps_used = self._state.step_count
        efficiency = max(0.0, 1.0 - (steps_used / self.MAX_STEPS))
        reward += efficiency * 0.5

        # ④ Risk penalty
        if is_risky:
            reward -= 0.8 * self._state.risk_level

        # ⑤ Delayed important task penalty
        if action_name == "delay" and is_urgent:
            reward -= 1.2

        # ⑥ Ignore penalty for high-importance tasks
        if action_name == "ignore":
            importance = task_result.get("task_importance", 0.5)
            reward -= importance * 1.0

        # ⑦ Escalation overuse penalty
        if action_name == "escalate":
            if self._state.escalation_count >= self.MAX_ESCALATIONS:
                reward -= 1.0
            else:
                reward += 0.2  # small bonus for appropriate escalation

        # ⑧ Domain-specific reward modifier
        reward += task_result.get("domain_reward_modifier", 0.0)

        return round(float(np.clip(reward, -3.0, 3.0)), 4)

    def _apply_state_updates(self, action_name: str, task_result: Dict) -> None:
        s = self._state

        # Consume resources
        cost = task_result.get("resource_cost", 0)
        s.budget_remaining = max(0, s.budget_remaining - cost)
        s.time_remaining   = max(0, s.time_remaining - task_result.get("time_cost", 1))
        s.resources["compute"] = max(0, s.resources["compute"] - task_result.get("compute_cost", 0))

        # Track escalations
        if action_name == "escalate":
            s.escalation_count += 1

        # Track missed deadlines
        if task_result.get("deadline_missed", False):
            s.missed_deadlines += 1

        # Track completions
        completed_id = task_result.get("completed_task_id")
        if completed_id and completed_id not in s.completed_tasks:
            s.completed_tasks.append(completed_id)

        # Update risk dynamically
        risk_delta = task_result.get("risk_delta", 0.0)
        s.risk_level = float(np.clip(s.risk_level + risk_delta, 0.0, 1.0))

        # Update task queue from domain task
        if "updated_task_queue" in task_result:
            s.task_queue = task_result["updated_task_queue"]

        # Mirror domain-specific state
        s.domain_specific = task_result.get("domain_state", s.domain_specific)

    def _check_done(self, task_result: Dict) -> bool:
        s = self._state
        if s.step_count >= self.MAX_STEPS:
            return True
        if s.budget_remaining <= 0:
            return True
        if s.time_remaining <= 0:
            return True
        if task_result.get("episode_complete", False):
            return True
        if self._current_task.is_complete(s):
            return True
        return False

    def get_history(self) -> List[Dict]:
        return self._history

    def get_summary(self) -> Dict:
        if not self._state:
            return {}
        return {
            "task_id": self.task_id,
            "steps_taken": self._state.step_count,
            "tasks_completed": len(self._state.completed_tasks),
            "missed_deadlines": self._state.missed_deadlines,
            "budget_used": round(1000 - self._state.budget_remaining, 2),
            "risk_level_final": round(self._state.risk_level, 3),
            "escalations_used": self._state.escalation_count,
            "total_reward": round(sum(h["reward"] for h in self._history), 4),
        }
