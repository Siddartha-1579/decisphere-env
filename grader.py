"""
grader.py – Deterministic Scoring System for DecisionEnv
Returns scores in [0.0, 1.0] for correctness, efficiency, and decision quality.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class GradeReport:
    task_id: int
    correctness_score: float    # How correct the decisions were
    efficiency_score: float     # Steps used vs minimum required
    quality_score: float        # Overall decision quality
    risk_score: float           # Risk management rating
    final_score: float          # Weighted composite [0.0–1.0]
    letter_grade: str
    breakdown: Dict


GRADE_THRESHOLDS = [
    (0.90, "A+"), (0.85, "A"), (0.80, "A−"),
    (0.75, "B+"), (0.70, "B"), (0.65, "B−"),
    (0.60, "C+"), (0.55, "C"), (0.50, "C−"),
    (0.40, "D"),  (0.00, "F"),
]

# Minimum steps for each task (lower bound for perfect efficiency)
MIN_STEPS = {1: 6, 2: 5, 3: 5}
# Weights per task for final score
WEIGHTS = {
    1: {"correctness": 0.50, "efficiency": 0.25, "quality": 0.15, "risk": 0.10},
    2: {"correctness": 0.40, "efficiency": 0.20, "quality": 0.25, "risk": 0.15},
    3: {"correctness": 0.35, "efficiency": 0.15, "quality": 0.30, "risk": 0.20},
}


class Grader:
    """
    Evaluates a completed episode and returns a structured grade report.
    All scores are in [0.0, 1.0] and deterministic given the same history.
    """

    def grade(self, task_id: int, history: List[Dict], summary: Dict) -> GradeReport:
        """
        Args:
            task_id: 1, 2, or 3
            history: list of step dicts from env.get_history()
            summary: dict from env.get_summary()

        Returns:
            GradeReport with per-dimension scores and a final composite.
        """
        correctness = self._score_correctness(history)
        efficiency  = self._score_efficiency(task_id, summary)
        quality     = self._score_quality(task_id, history, summary)
        risk        = self._score_risk(history, summary)

        w = WEIGHTS[task_id]
        final = (
            correctness * w["correctness"] +
            efficiency  * w["efficiency"]  +
            quality     * w["quality"]     +
            risk        * w["risk"]
        )
        final = round(min(1.0, max(0.0, final)), 4)

        return GradeReport(
            task_id=task_id,
            correctness_score=correctness,
            efficiency_score=efficiency,
            quality_score=quality,
            risk_score=risk,
            final_score=final,
            letter_grade=self._letter(final),
            breakdown={
                "total_steps": summary.get("steps_taken", 0),
                "tasks_completed": summary.get("tasks_completed", 0),
                "missed_deadlines": summary.get("missed_deadlines", 0),
                "escalations_used": summary.get("escalations_used", 0),
                "budget_used": summary.get("budget_used", 0),
                "total_reward": summary.get("total_reward", 0),
                "risk_level_final": summary.get("risk_level_final", 0),
                "weights_used": w,
            }
        )

    # ── Per-dimension scoring ─────────────────────────────────────────────────

    def _score_correctness(self, history: List[Dict]) -> float:
        """Average correctness across all steps."""
        if not history:
            return 0.0
        values = [h["task_result"].get("correctness", 0) for h in history]
        return round(sum(values) / len(values), 4)

    def _score_efficiency(self, task_id: int, summary: Dict) -> float:
        """
        Score based on how close to the minimum steps the agent operated.
        efficiency = min_steps / steps_taken  (capped at 1.0)
        """
        steps = summary.get("steps_taken", 1)
        min_s = MIN_STEPS.get(task_id, 5)
        if steps <= min_s:
            return 1.0
        return round(min(1.0, min_s / steps), 4)

    def _score_quality(self, task_id: int, history: List[Dict], summary: Dict) -> float:
        """
        Task-specific quality metrics:
          Task 1: Fraction of tasks completed without delays or ignores on urgent items
          Task 2: Allocation score from domain state
          Task 3: Crisis resolution score from domain state
        """
        if not history:
            return 0.0

        if task_id == 1:
            bad_actions = sum(
                1 for h in history
                if h["action"] in ("ignore", "delay")
                and h["task_result"].get("task_urgent", False)
            )
            quality = max(0.0, 1.0 - (bad_actions / max(1, len(history))))

        elif task_id == 2:
            last = history[-1]
            domain = last["task_result"].get("domain_state", {})
            quality = domain.get("allocation_score", 0.5)

        elif task_id == 3:
            last = history[-1]
            domain = last["task_result"].get("domain_state", {})
            quality = domain.get("resolution_score", 0.5)

        else:
            quality = 0.5

        return round(float(quality), 4)

    def _score_risk(self, history: List[Dict], summary: Dict) -> float:
        """
        Lower final risk and fewer missed deadlines = higher risk score.
        risk_score = 1 - risk_level_final - 0.1 × missed_deadlines
        """
        final_risk = summary.get("risk_level_final", 0.5)
        missed     = summary.get("missed_deadlines", 0)
        penalty    = min(0.5, missed * 0.1)
        score = max(0.0, 1.0 - final_risk - penalty)
        return round(score, 4)

    @staticmethod
    def _letter(score: float) -> str:
        for threshold, grade in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"


# ── Batch grader for multi-run evaluation ────────────────────────────────────

def run_evaluation(env_class, agent_class, task_id: int,
                   n_episodes: int = 5, seed: int = 42) -> Dict:
    """
    Run multiple episodes and return aggregate statistics.
    Useful for benchmarking agents deterministically.
    """
    grader = Grader()
    reports = []

    for ep in range(n_episodes):
        env = env_class(task_id=task_id, seed=seed + ep)
        agent = agent_class(task_id=task_id)
        obs = env.reset()
        done = False

        while not done:
            action = agent.act(obs, env.state())
            obs, reward, done, info = env.step(action)

        report = grader.grade(task_id, env.get_history(), env.get_summary())
        reports.append(report)

    scores = [r.final_score for r in reports]
    return {
        "task_id": task_id,
        "n_episodes": n_episodes,
        "mean_score": round(sum(scores) / len(scores), 4),
        "min_score":  round(min(scores), 4),
        "max_score":  round(max(scores), 4),
        "grade_distribution": {r.letter_grade for r in reports},
        "reports": reports,
    }
