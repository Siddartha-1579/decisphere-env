"""
tasks.py – Domain Task Handlers for DecisionEnv
Three tasks of increasing complexity for the AI Decision-Making Benchmark.
"""

import random
import math
from typing import Dict, List, Optional, Any


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

TASK_NAMES = [
    "Deploy security patch",
    "Prepare quarterly report",
    "Resolve customer escalation",
    "Migrate database",
    "Onboard new team",
    "Fix production bug",
    "Update compliance docs",
    "Plan product roadmap",
    "Conduct performance reviews",
    "Launch marketing campaign",
    "Audit infrastructure costs",
    "Train new ML model",
    "Review legal contracts",
    "Organize team offsite",
    "Reduce technical debt",
]


def _make_task(rng: random.Random, task_id: str = None) -> Dict:
    """Generate a randomized task with urgency, importance, deadline, and cost."""
    name = rng.choice(TASK_NAMES)
    urgency = round(rng.uniform(0.1, 1.0), 2)
    importance = round(rng.uniform(0.1, 1.0), 2)
    deadline = rng.randint(1, 10)          # steps until deadline
    cost = round(rng.uniform(10, 150), 1)  # budget cost
    time_cost = round(rng.uniform(1, 10), 1)
    risk = round(rng.uniform(0.0, 0.6), 2)

    return {
        "id": task_id or f"T{rng.randint(100,999)}",
        "name": name,
        "urgency": urgency,
        "importance": importance,
        "deadline": deadline,
        "cost": cost,
        "time_cost": time_cost,
        "risk": risk,
        "priority_score": round((urgency * 0.6) + (importance * 0.4), 3),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Task 1 – Task Prioritization  (Easy)
# ─────────────────────────────────────────────────────────────────────────────

class TaskPrioritization:
    """
    Task 1 (Easy): The agent receives a queue of tasks and must prioritize
    them by correctly choosing the highest-priority task first.

    Correctness is measured by how well the agent's chosen action aligns
    with the Eisenhower Matrix (urgency × importance).
    """

    N_TASKS = 6

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.queue: List[Dict] = []
        self.ideal_order: List[str] = []
        self.step_count = 0

    def reset(self) -> Dict:
        self.queue = [
            _make_task(self.rng, task_id=f"T{i+1}") for i in range(self.N_TASKS)
        ]
        # Ideal ranking: descending by priority_score
        self.ideal_order = [
            t["id"] for t in sorted(self.queue, key=lambda x: -x["priority_score"])
        ]
        self.step_count = 0
        return {"task_queue": list(self.queue), "ideal_order": self.ideal_order}

    def step(self, action_name: str, env_state: Any) -> Dict:
        self.step_count += 1
        if not self.queue:
            return {"task_completed": False, "episode_complete": True,
                    "correctness": 1.0, "domain_state": self._domain_state()}

        # Current top-priority task according to ideal order
        current_task = self._get_top_task()
        is_urgent = current_task["urgency"] > 0.7
        is_important = current_task["importance"] > 0.7

        correctness, domain_reward, risk_delta, completed = \
            self._evaluate_action(action_name, current_task)

        result = {
            "correctness":          correctness,
            "task_completed":       completed,
            "task_urgent":          is_urgent,
            "task_importance":      current_task["importance"],
            "is_risky":             action_name == "ignore" and is_important,
            "resource_cost":        current_task["cost"] if completed else 0,
            "time_cost":            current_task["time_cost"] if completed else 1,
            "compute_cost":         5 if action_name == "prioritize" else 0,
            "deadline_missed":      action_name == "delay" and current_task["deadline"] <= 1,
            "risk_delta":           risk_delta,
            "domain_reward_modifier": domain_reward,
            "domain_state":         self._domain_state(),
            "updated_task_queue":   list(self.queue),
            "current_task":         current_task,
        }

        if completed:
            result["completed_task_id"] = current_task["id"]

        # Episode ends when queue is cleared or too many steps
        result["episode_complete"] = len(self.queue) == 0 or self.step_count >= 12
        return result

    def is_complete(self, env_state: Any) -> bool:
        return len(self.queue) == 0

    def _get_top_task(self) -> Dict:
        return max(self.queue, key=lambda x: x["priority_score"])

    def _evaluate_action(self, action: str, task: Dict):
        """Return (correctness, domain_reward, risk_delta, completed)."""
        u, imp = task["urgency"], task["importance"]
        ps = task["priority_score"]

        if action == "prioritize":
            # Correct for high-urgency or high-importance tasks
            correctness = 0.5 + (ps * 0.5)
            domain_reward = 0.3 if ps > 0.6 else -0.1
            risk_delta = -0.05
            completed = True
            self.queue.remove(task)

        elif action == "delay":
            # Only ok for low-urgency tasks
            correctness = max(0.0, 1.0 - u)
            domain_reward = -0.2 if u > 0.6 else 0.1
            risk_delta = 0.05 * u
            completed = False
            task["deadline"] -= 1

        elif action == "allocate":
            # Good universal middle ground
            correctness = 0.5 + (imp * 0.3)
            domain_reward = 0.1
            risk_delta = 0.0
            completed = self.rng.random() < ps
            if completed:
                self.queue.remove(task)

        elif action == "ignore":
            # Very bad for important tasks
            correctness = max(0.0, 1.0 - imp)
            domain_reward = -0.4 * imp
            risk_delta = 0.1
            completed = False

        elif action == "escalate":
            # Appropriate only when really stuck
            correctness = 0.4
            domain_reward = 0.0
            risk_delta = -0.02
            completed = False

        else:
            correctness, domain_reward, risk_delta, completed = 0.0, 0.0, 0.0, False

        return round(correctness, 3), round(domain_reward, 3), round(risk_delta, 3), completed

    def _domain_state(self) -> Dict:
        return {"queue_length": len(self.queue), "ideal_order": self.ideal_order}


# ─────────────────────────────────────────────────────────────────────────────
# Task 2 – Resource Allocation  (Medium)
# ─────────────────────────────────────────────────────────────────────────────

class ResourceAllocation:
    """
    Task 2 (Medium): Agent must allocate a limited budget and time pool
    across competing projects to maximise total value delivered.

    Budget and time are consumed with each allocation. The agent must
    decide which tasks to fund and when to stop spending.
    """

    N_PROJECTS = 5

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.projects: List[Dict] = []
        self.total_budget = 0.0
        self.total_time = 0.0
        self.spent_budget = 0.0
        self.spent_time = 0.0
        self.funded: List[str] = []
        self.step_count = 0

    def reset(self) -> Dict:
        self.total_budget = self.rng.uniform(300, 600)
        self.total_time = self.rng.uniform(20, 40)
        self.spent_budget = 0.0
        self.spent_time = 0.0
        self.funded = []
        self.step_count = 0

        self.projects = []
        for i in range(self.N_PROJECTS):
            cost = round(self.rng.uniform(50, 200), 1)
            time_req = round(self.rng.uniform(3, 12), 1)
            value = round(self.rng.uniform(50, 300), 1)
            roi = round(value / (cost + 1e-6), 3)
            self.projects.append({
                "id": f"P{i+1}",
                "name": f"Project {chr(65+i)}",
                "cost": cost,
                "time_required": time_req,
                "value": value,
                "roi": roi,
                "urgency": round(self.rng.uniform(0.2, 1.0), 2),
                "importance": round(self.rng.uniform(0.2, 1.0), 2),
                "funded": False,
            })

        # Ideal allocation: greedy knapsack by ROI
        self._ideal_funded = self._greedy_knapsack()

        task_queue = [
            {"id": p["id"], "name": p["name"],
             "urgency": p["urgency"], "importance": p["importance"]}
            for p in self.projects
        ]
        return {
            "task_queue": task_queue,
            "projects": list(self.projects),
            "total_budget": self.total_budget,
            "total_time": self.total_time,
            "ideal_funded": self._ideal_funded,
        }

    def step(self, action_name: str, env_state: Any) -> Dict:
        self.step_count += 1
        unfunded = [p for p in self.projects if not p["funded"]]

        if not unfunded:
            return {"task_completed": True, "episode_complete": True,
                    "correctness": self._allocation_score(),
                    "domain_state": self._domain_state(),
                    "domain_reward_modifier": 0.5}

        # Pick the best-ROI unfunded project as the target
        target = max(unfunded, key=lambda p: p["roi"])

        correctness, domain_reward, completed, risk_delta = \
            self._evaluate_action(action_name, target, env_state)

        can_afford = (self.total_budget - self.spent_budget) >= target["cost"]
        has_time   = (self.total_time   - self.spent_time)   >= target["time_required"]

        result = {
            "correctness":          correctness,
            "task_completed":       completed,
            "task_urgent":          target["urgency"] > 0.7,
            "task_importance":      target["importance"],
            "is_risky":             not can_afford and action_name == "allocate",
            "resource_cost":        target["cost"] if completed else 0,
            "time_cost":            target["time_required"] if completed else 0.5,
            "compute_cost":         0,
            "deadline_missed":      not can_afford and target["urgency"] > 0.8,
            "risk_delta":           risk_delta,
            "domain_reward_modifier": domain_reward,
            "domain_state":         self._domain_state(),
            "updated_task_queue": [
                {"id": p["id"], "name": p["name"],
                 "urgency": p["urgency"], "importance": p["importance"]}
                for p in self.projects if not p["funded"]
            ],
        }

        budget_gone  = (self.total_budget - self.spent_budget) < 20
        time_gone    = (self.total_time   - self.spent_time)   < 1
        all_funded   = all(p["funded"] for p in self.projects)
        result["episode_complete"] = budget_gone or time_gone or all_funded or self.step_count >= 15

        if completed:
            result["completed_task_id"] = target["id"]

        return result

    def is_complete(self, env_state: Any) -> bool:
        return all(p["funded"] for p in self.projects)

    def _evaluate_action(self, action: str, project: Dict, env_state: Any):
        budget_left = self.total_budget - self.spent_budget
        time_left   = self.total_time   - self.spent_time
        can_afford  = budget_left >= project["cost"]
        has_time    = time_left   >= project["time_required"]
        in_ideal    = project["id"] in self._ideal_funded

        if action == "allocate":
            if can_afford and has_time:
                project["funded"] = True
                self.spent_budget += project["cost"]
                self.spent_time   += project["time_required"]
                correctness = 0.7 + (0.3 * float(in_ideal))
                domain_reward = 0.4 if in_ideal else 0.1
                completed = True
                risk_delta = -0.03
            else:
                correctness = 0.1
                domain_reward = -0.3
                completed = False
                risk_delta = 0.1

        elif action == "prioritize":
            # Re-order but not commit budget
            correctness = 0.4
            domain_reward = 0.0
            completed = False
            risk_delta = 0.0

        elif action == "delay":
            correctness = max(0.0, 1.0 - project["urgency"])
            domain_reward = -0.1 if project["urgency"] > 0.6 else 0.05
            completed = False
            risk_delta = 0.02

        elif action == "ignore":
            if in_ideal:
                correctness = 0.0
                domain_reward = -0.5
            else:
                correctness = 0.6
                domain_reward = 0.1
            completed = False
            risk_delta = 0.05

        elif action == "escalate":
            # Escalation adds 10% to available budget (one-time boost)
            boost = self.total_budget * 0.10
            self.total_budget += boost
            correctness = 0.5
            domain_reward = 0.1
            completed = False
            risk_delta = 0.0

        else:
            correctness, domain_reward, completed, risk_delta = 0.0, 0.0, False, 0.0

        return round(correctness, 3), round(domain_reward, 3), completed, round(risk_delta, 3)

    def _allocation_score(self) -> float:
        """Ratio of ideal value captured vs maximum possible value."""
        funded_ids = {p["id"] for p in self.projects if p["funded"]}
        ideal_ids  = set(self._ideal_funded)
        if not ideal_ids:
            return 1.0
        overlap = len(funded_ids & ideal_ids)
        return round(overlap / len(ideal_ids), 3)

    def _greedy_knapsack(self) -> List[str]:
        """Greedy selection by ROI within budget and time constraints."""
        sorted_p = sorted(self.projects, key=lambda x: -x["roi"])
        b, t, selected = self.total_budget, self.total_time, []
        for p in sorted_p:
            if b >= p["cost"] and t >= p["time_required"]:
                selected.append(p["id"])
                b -= p["cost"]
                t -= p["time_required"]
        return selected

    def _domain_state(self) -> Dict:
        return {
            "spent_budget": round(self.spent_budget, 2),
            "spent_time":   round(self.spent_time, 2),
            "funded":       [p["id"] for p in self.projects if p["funded"]],
            "ideal_funded": self._ideal_funded,
            "allocation_score": self._allocation_score(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Task 3 – Complex Multi-Step Decision-Making  (Hard)
# ─────────────────────────────────────────────────────────────────────────────

class ComplexDecision:
    """
    Task 3 (Hard): The agent faces a crisis scenario with cascading trade-offs,
    resource constraints, and compounding risk. Correct multi-step sequencing
    is required to resolve all sub-problems while minimising global risk.

    Scenario: "Product Launch Crisis" – several interconnected issues must
    be resolved in the right order with limited staff, budget, and time.
    """

    CRISIS_STAGES = [
        {
            "id": "C1",
            "name": "Critical security vulnerability discovered",
            "urgency": 1.0, "importance": 1.0, "risk": 0.9,
            "cost": 120, "time_cost": 5, "requires": [],
        },
        {
            "id": "C2",
            "name": "Customer data possibly exposed",
            "urgency": 0.9, "importance": 0.95, "risk": 0.85,
            "cost": 80, "time_cost": 4, "requires": ["C1"],
        },
        {
            "id": "C3",
            "name": "Regulatory authority requesting report",
            "urgency": 0.8, "importance": 0.9, "risk": 0.7,
            "cost": 60, "time_cost": 3, "requires": ["C2"],
        },
        {
            "id": "C4",
            "name": "Press inquiries mounting",
            "urgency": 0.7, "importance": 0.75, "risk": 0.5,
            "cost": 40, "time_cost": 2, "requires": [],
        },
        {
            "id": "C5",
            "name": "Staff morale and overwork",
            "urgency": 0.5, "importance": 0.6, "risk": 0.3,
            "cost": 30, "time_cost": 2, "requires": [],
        },
    ]

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.stages: List[Dict] = []
        self.resolved: List[str] = []
        self.step_count = 0
        self.global_risk = 0.8

    def reset(self) -> Dict:
        import copy
        self.stages = copy.deepcopy(self.CRISIS_STAGES)
        # Randomise costs/urgency slightly for variety
        for s in self.stages:
            s["cost"] = round(s["cost"] * self.rng.uniform(0.8, 1.2), 1)
            s["urgency"] = round(min(1.0, s["urgency"] * self.rng.uniform(0.9, 1.1)), 2)
        self.resolved = []
        self.step_count = 0
        self.global_risk = 0.8

        task_queue = [
            {"id": s["id"], "name": s["name"],
             "urgency": s["urgency"], "importance": s["importance"]}
            for s in self.stages
        ]
        return {"task_queue": task_queue, "crisis_stages": list(self.stages),
                "global_risk": self.global_risk}

    def step(self, action_name: str, env_state: Any) -> Dict:
        self.step_count += 1
        available = self._get_available_stages()

        if not available:
            return {
                "task_completed": True, "episode_complete": True,
                "correctness": self._crisis_resolution_score(),
                "domain_state": self._domain_state(),
                "domain_reward_modifier": 1.0 if not self.resolved else 0.5,
            }

        # Current top crisis (highest urgency × risk)
        target = max(available, key=lambda s: s["urgency"] * s["risk"])

        correctness, domain_reward, resolved, risk_delta = \
            self._evaluate_action(action_name, target, env_state)

        task_queue = [
            {"id": s["id"], "name": s["name"],
             "urgency": s["urgency"], "importance": s["importance"]}
            for s in self.stages if s["id"] not in self.resolved
        ]

        result = {
            "correctness":          correctness,
            "task_completed":       resolved,
            "task_urgent":          target["urgency"] > 0.7,
            "task_importance":      target["importance"],
            "is_risky":             self.global_risk > 0.6,
            "resource_cost":        target["cost"] if resolved else 0,
            "time_cost":            target["time_cost"] if resolved else 1,
            "compute_cost":         10 if action_name == "escalate" else 0,
            "deadline_missed":      action_name in ("delay", "ignore") and target["urgency"] > 0.85,
            "risk_delta":           risk_delta,
            "domain_reward_modifier": domain_reward,
            "domain_state":         self._domain_state(),
            "updated_task_queue":   task_queue,
        }

        if resolved:
            result["completed_task_id"] = target["id"]

        result["episode_complete"] = (
            len(self.resolved) == len(self.stages) or self.step_count >= 20
        )
        return result

    def is_complete(self, env_state: Any) -> bool:
        return len(self.resolved) == len(self.stages)

    def _get_available_stages(self) -> List[Dict]:
        """Stages whose prerequisites are already resolved."""
        return [
            s for s in self.stages
            if s["id"] not in self.resolved
            and all(req in self.resolved for req in s["requires"])
        ]

    def _evaluate_action(self, action: str, stage: Dict, env_state: Any):
        u, imp, risk = stage["urgency"], stage["importance"], stage["risk"]

        if action == "prioritize":
            # Best for high-urgency, high-risk items
            correctness = 0.5 + (u * 0.3) + (risk * 0.2)
            domain_reward = 0.4 if u > 0.8 else 0.1
            resolved = False   # prioritize doesn't resolve by itself
            risk_delta = -0.05

        elif action == "allocate":
            # Actually commits resources → resolves the crisis item
            correctness = 0.6 + (imp * 0.2) + (risk * 0.2)
            domain_reward = 0.5
            resolved = True
            self.resolved.append(stage["id"])
            risk_delta = -(risk * 0.2)

        elif action == "escalate":
            # Appropriate for critical C1/C2
            if risk > 0.8:
                correctness = 0.85
                domain_reward = 0.6
                resolved = True
                self.resolved.append(stage["id"])
                risk_delta = -(risk * 0.3)
            else:
                # Over-escalation is wasteful
                correctness = 0.3
                domain_reward = -0.2
                resolved = False
                risk_delta = 0.0

        elif action == "delay":
            correctness = max(0.0, 1.0 - u) * 0.5
            domain_reward = -0.3 if u > 0.7 else 0.0
            resolved = False
            risk_delta = risk * 0.1

        elif action == "ignore":
            correctness = 0.0
            domain_reward = -0.8
            resolved = False
            risk_delta = risk * 0.2

        else:
            correctness, domain_reward, resolved, risk_delta = 0.0, 0.0, False, 0.0

        # Update global risk
        self.global_risk = round(max(0.0, min(1.0, self.global_risk + risk_delta)), 3)

        return round(correctness, 3), round(domain_reward, 3), resolved, round(risk_delta, 3)

    def _crisis_resolution_score(self) -> float:
        """Fraction of crisis stages resolved weighted by importance."""
        total_weight = sum(s["importance"] for s in self.stages)
        resolved_weight = sum(
            s["importance"] for s in self.stages if s["id"] in self.resolved
        )
        return round(resolved_weight / (total_weight + 1e-9), 3)

    def _domain_state(self) -> Dict:
        return {
            "resolved": list(self.resolved),
            "pending": [s["id"] for s in self.stages if s["id"] not in self.resolved],
            "global_risk": self.global_risk,
            "resolution_score": self._crisis_resolution_score(),
        }
