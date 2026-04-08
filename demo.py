"""
demo.py – Step-by-Step Demo Runner for DecisionEnv
Runs all three tasks with the RuleBasedAgent and prints detailed results.
"""

from environment import DecisionEnv, ACTIONS
from agent import RuleBasedAgent, RandomAgent
from grader import Grader, GradeReport


SEPARATOR = "─" * 70


def run_task(task_id: int, seed: int = 42, verbose: bool = True) -> GradeReport:
    """Run a single task episode and return the grade report."""
    print(f"\n{'═'*70}")
    task_labels = {1: "EASY  – Task Prioritization",
                   2: "MEDIUM – Resource Allocation",
                   3: "HARD   – Complex Crisis Management"}
    print(f"  TASK {task_id} | {task_labels[task_id]}")
    print(f"{'═'*70}")

    env = DecisionEnv(task_id=task_id, seed=seed)
    agent = RuleBasedAgent(task_id=task_id)
    grader = Grader()

    obs = env.reset()
    agent.reset()
    done = False
    total_reward = 0.0
    step = 0

    if verbose:
        print("\n[Initial State]")
        print(env.render())
        print()

    while not done:
        step += 1
        action = agent.act(obs, env.state())
        action_name = ACTIONS[action]

        obs, reward, done, info = env.step(action)
        total_reward += reward

        if verbose:
            tr = info["task_result"]
            print(f"  Step {step:02d} │ Action: {action_name:<12} │ "
                  f"Reward: {reward:+.4f} │ "
                  f"Correct: {tr.get('correctness',0):.2f} │ "
                  f"Done: {done}")
            if tr.get("task_completed"):
                completed_id = tr.get("completed_task_id", "?")
                print(f"           ✓ Completed task {completed_id}")
            if tr.get("deadline_missed"):
                print(f"           ⚠ Deadline missed!")
            if tr.get("is_risky"):
                print(f"           ⚡ Risky decision detected (risk_level={info['risk_level']:.2f})")

    print(f"\n{SEPARATOR}")
    print(f"  Episode Complete in {step} steps | Total Reward: {total_reward:+.4f}")
    print(SEPARATOR)

    # Grade the episode
    report = grader.grade(task_id, env.get_history(), env.get_summary())

    print(f"\n  📊 GRADE REPORT")
    print(f"  {'Correctness':20s}: {report.correctness_score:.4f}")
    print(f"  {'Efficiency':20s}: {report.efficiency_score:.4f}")
    print(f"  {'Decision Quality':20s}: {report.quality_score:.4f}")
    print(f"  {'Risk Management':20s}: {report.risk_score:.4f}")
    print(f"  {'─'*38}")
    print(f"  {'FINAL SCORE':20s}: {report.final_score:.4f}  [{report.letter_grade}]")
    print()

    return report


def compare_agents(task_id: int, seed: int = 42):
    """Compare RuleBasedAgent vs RandomAgent on the same task."""
    print(f"\n{'═'*70}")
    print(f"  AGENT COMPARISON | Task {task_id}")
    print(f"{'═'*70}")

    grader = Grader()

    for AgentClass, label in [(RuleBasedAgent, "RuleBasedAgent"), (RandomAgent, "RandomAgent  ")]:
        env = DecisionEnv(task_id=task_id, seed=seed)
        agent = AgentClass(task_id=task_id)
        obs = env.reset()
        done = False

        while not done:
            action = agent.act(obs, env.state())
            obs, reward, done, info = env.step(action)

        report = grader.grade(task_id, env.get_history(), env.get_summary())
        summary = env.get_summary()
        print(f"  {label} │ Score: {report.final_score:.4f} [{report.letter_grade}] │ "
              f"Steps: {summary['steps_taken']} │ "
              f"Completed: {summary['tasks_completed']} │ "
              f"Reward: {summary['total_reward']:+.2f}")


def main():
    print("\n" + "★" * 70)
    print("  DecisionEnv — Multi-Domain AI Decision-Making Benchmark")
    print("  Meta + Hugging Face OpenEnv Hackathon")
    print("★" * 70)

    reports = []
    for task_id in (1, 2, 3):
        report = run_task(task_id=task_id, seed=42, verbose=True)
        reports.append(report)

    # ── Overall summary ────────────────────────────────────────────────────
    print(f"\n{'═'*70}")
    print("  OVERALL BENCHMARK SUMMARY")
    print(f"{'═'*70}")
    overall = sum(r.final_score for r in reports) / len(reports)
    for r in reports:
        label = {1: "Task 1 – Prioritization",
                 2: "Task 2 – Allocation    ",
                 3: "Task 3 – Crisis Mgmt   "}[r.task_id]
        bar = "█" * int(r.final_score * 30)
        print(f"  {label} │ {bar:<30} {r.final_score:.4f} [{r.letter_grade}]")

    print(f"\n  {'Overall Average':25s}: {overall:.4f}  [{_letter(overall)}]")
    print()

    # ── Agent comparison on Task 3 ─────────────────────────────────────────
    compare_agents(task_id=3, seed=42)
    print()


def _letter(score: float) -> str:
    from grader import GRADE_THRESHOLDS
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


if __name__ == "__main__":
    main()
