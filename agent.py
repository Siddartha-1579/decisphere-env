"""
agent.py – Rule-Based Baseline Agent for DecisionEnv
Handles all three domain tasks with logical heuristics.
"""

from typing import Optional
import numpy as np
from environment import EnvState, ACTIONS


class RuleBasedAgent:
    """
    A deterministic rule-based agent that makes decisions based on
    human-readable heuristics for each of the three domain tasks.

    This serves as a strong baseline for comparing RL-trained agents.
    """

    def __init__(self, task_id: int):
        assert task_id in (1, 2, 3)
        self.task_id = task_id
        self._step = 0

    def reset(self):
        self._step = 0

    def act(self, observation: np.ndarray, state: EnvState) -> int:
        """
        Choose an action (int 0–4) given the current observation and state.

        Returns:
            int: Action index (see ACTIONS in environment.py)
        """
        self._step += 1

        if self.task_id == 1:
            return self._task1_policy(state)
        elif self.task_id == 2:
            return self._task2_policy(state)
        elif self.task_id == 3:
            return self._task3_policy(state)
        return 0  # default: prioritize

    # ── Task 1: Task Prioritization ───────────────────────────────────────────

    def _task1_policy(self, state: EnvState) -> int:
        """
        Heuristic: Always prioritize the highest urgency × importance task.
        Escalate if budget is very low and urgent task exists.
        Delay only truly low-importance tasks.
        """
        if not state.task_queue:
            return 0  # prioritize (no-op)

        top = max(state.task_queue, key=lambda t: t["urgency"] * t["importance"])
        ps = top["urgency"] * top["importance"]

        # High priority: always act
        if ps > 0.6:
            if state.budget_remaining < 50:
                return 4  # escalate to get more resources
            return 0  # prioritize

        # Medium priority: allocate
        if ps > 0.3:
            return 2  # allocate

        # Low priority: delay
        return 1  # delay

    # ── Task 2: Resource Allocation ───────────────────────────────────────────

    def _task2_policy(self, state: EnvState) -> int:
        """
        Heuristic: Allocate when there's sufficient budget and time.
        Escalate once to get a budget boost if tight.
        Delay low-urgency projects when resources are scarce.
        """
        domain = state.domain_specific
        spent_budget = domain.get("spent_budget", 0)
        budget_remaining = state.budget_remaining
        time_remaining   = state.time_remaining

        if not state.task_queue:
            return 2  # allocate

        top = max(state.task_queue, key=lambda t: t["urgency"] * t["importance"])
        affordable = budget_remaining > 80 and time_remaining > 3

        if affordable:
            return 2  # allocate

        # If budget is tight and haven't escalated much
        if state.escalation_count == 0 and budget_remaining < 120:
            return 4  # escalate for budget boost

        # Delay low-urgency projects
        if top.get("urgency", 0.5) < 0.5:
            return 1  # delay

        return 2  # allocate anyway (take calculated risk)

    # ── Task 3: Complex Multi-Step Crisis ─────────────────────────────────────

    def _task3_policy(self, state: EnvState) -> int:
        """
        Heuristic: Handle highest-risk crisis items first.
        Escalate for critical severity (risk > 0.8).
        Never ignore. Only delay the lowest-urgency items.
        """
        domain = state.domain_specific
        global_risk = domain.get("global_risk", 0.5)

        if not state.task_queue:
            return 0

        # Sort by urgency × importance (proxy for risk priority)
        top = max(state.task_queue, key=lambda t: t["urgency"] * t["importance"])
        u = top.get("urgency", 0.5)

        # Critical items: escalate
        if u >= 0.9 and state.escalation_count < 3:
            return 4  # escalate

        # High urgency: prioritize first, then allocate next step
        if u >= 0.7:
            if self._step % 2 == 1:
                return 0  # prioritize
            return 2  # allocate

        # Medium urgency: allocate
        if u >= 0.4:
            return 2  # allocate

        # Low urgency: delay temporarily
        return 1  # delay

    def describe(self) -> str:
        return (
            f"RuleBasedAgent(task={self.task_id}) | "
            f"Steps taken: {self._step} | "
            f"Policy: Heuristic urgency×importance ranking"
        )


# ── Random agent for comparison ───────────────────────────────────────────────

class RandomAgent:
    """Baseline random agent for benchmarking."""

    def __init__(self, task_id: int, seed: int = 0):
        self.task_id = task_id
        import random
        self._rng = random.Random(seed)

    def reset(self):
        pass

    def act(self, observation: np.ndarray, state: EnvState) -> int:
        return self._rng.randint(0, len(ACTIONS) - 1)
