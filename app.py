"""
app.py – Streamlit Frontend for DecisionEnv
Interactive demo for the Meta + HuggingFace OpenEnv Hackathon submission.
"""

import streamlit as st
import numpy as np
import pandas as pd
import json
import time

from environment import DecisionEnv, ACTIONS, ACTION_NAMES
from agent import RuleBasedAgent, RandomAgent
from grader import Grader


# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="DecisionEnv | AI Benchmark",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a3e 50%, #0d2137 100%);
    border: 1px solid #2a2a5a;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.hero h1 { color: #a78bfa; font-size: 2.2rem; margin: 0; }
.hero p  { color: #94a3b8; margin: 0.5rem 0 0; font-size: 1rem; }

.metric-card {
    background: #12121f;
    border: 1px solid #2a2a5a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-card .label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
.metric-card .value { color: #e2e8f0; font-size: 1.8rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; }

.step-row {
    background: #0f0f1a;
    border-left: 3px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 0.5rem 1rem;
    margin: 0.3rem 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #cbd5e1;
}
.step-row.good  { border-left-color: #22c55e; }
.step-row.bad   { border-left-color: #ef4444; }
.step-row.warn  { border-left-color: #f59e0b; }

.score-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
}
.grade-A { background: #14532d; color: #4ade80; }
.grade-B { background: #1e3a5f; color: #60a5fa; }
.grade-C { background: #78350f; color: #fbbf24; }
.grade-D { background: #450a0a; color: #f87171; }
.grade-F { background: #1f1f1f; color: #6b7280; }

.task-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.easy   { background: #14532d22; color: #4ade80; border: 1px solid #22c55e55; }
.medium { background: #78350f22; color: #fbbf24; border: 1px solid #f59e0b55; }
.hard   { background: #450a0a22; color: #f87171; border: 1px solid #ef444455; }

.sidebar-section { margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    task_id = st.selectbox(
        "Domain Task",
        options=[1, 2, 3],
        format_func=lambda x: {
            1: "🟢 Task 1 – Prioritization (Easy)",
            2: "🟡 Task 2 – Resource Allocation (Medium)",
            3: "🔴 Task 3 – Crisis Management (Hard)",
        }[x],
    )

    agent_type = st.selectbox(
        "Agent",
        options=["Rule-Based", "Random"],
        help="Rule-Based uses logical heuristics; Random selects uniformly.",
    )

    seed = st.number_input("Random Seed", min_value=0, max_value=9999, value=42)

    st.markdown("---")
    st.markdown("### 🎮 Actions")
    action_descriptions = {
        "prioritize": "Elevate task to top priority",
        "delay":      "Defer task to later",
        "allocate":   "Assign resources to task",
        "ignore":     "Skip / discard task",
        "escalate":   "Escalate for more resources",
    }
    for a, desc in action_descriptions.items():
        st.markdown(f"**{a}** – {desc}")

    st.markdown("---")
    st.caption("Meta + HuggingFace OpenEnv Hackathon · DecisionEnv v1.0")

# ─────────────────────────────────────────────────────────────────────────────
# Hero header
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <h1>🧠 DecisionEnv</h1>
  <p>Multi-Domain AI Decision-Making Benchmark &mdash; Meta + HuggingFace OpenEnv Hackathon</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Run episode
# ─────────────────────────────────────────────────────────────────────────────

col_run, col_all = st.columns([1, 3])

with col_run:
    run_single = st.button("▶ Run Episode", use_container_width=True, type="primary")
with col_all:
    run_all = st.button("⚡ Benchmark All Tasks", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = None
if "all_results" not in st.session_state:
    st.session_state.all_results = None


def run_episode(task_id, agent_type, seed):
    env = DecisionEnv(task_id=task_id, seed=int(seed))
    AgentClass = RuleBasedAgent if agent_type == "Rule-Based" else RandomAgent
    agent = AgentClass(task_id=task_id)
    grader = Grader()

    obs = env.reset()
    done = False
    steps = []

    while not done:
        action = agent.act(obs, env.state())
        obs, reward, done, info = env.step(action)
        steps.append({
            "step":        info["step"],
            "action":      info["action"],
            "reward":      reward,
            "correctness": info["task_result"].get("correctness", 0),
            "completed":   info["task_result"].get("task_completed", False),
            "deadline_missed": info["task_result"].get("deadline_missed", False),
            "is_risky":    info["task_result"].get("is_risky", False),
            "budget":      info["budget_remaining"],
            "risk":        info["risk_level"],
        })

    report = grader.grade(task_id, env.get_history(), env.get_summary())
    summary = env.get_summary()
    return steps, report, summary


if run_single:
    with st.spinner("Running episode..."):
        steps, report, summary = run_episode(task_id, agent_type, seed)
        st.session_state.results = (task_id, steps, report, summary)

if run_all:
    with st.spinner("Running all 3 tasks..."):
        all_res = []
        for tid in [1, 2, 3]:
            s, r, sm = run_episode(tid, agent_type, seed)
            all_res.append((tid, s, r, sm))
        st.session_state.all_results = all_res

# ─────────────────────────────────────────────────────────────────────────────
# Display single episode
# ─────────────────────────────────────────────────────────────────────────────

def display_results(task_id, steps, report, summary):
    task_labels = {1: ("Prioritization", "easy"),
                   2: ("Resource Allocation", "medium"),
                   3: ("Crisis Management", "hard")}
    label, cls = task_labels[task_id]

    st.markdown(f"""
    <div style="margin: 1rem 0;">
      <span class="task-badge {cls}">Task {task_id}</span>
      <strong style="margin-left: 0.5rem; color: #e2e8f0;">{label}</strong>
    </div>
    """, unsafe_allow_html=True)

    # ── Top metrics ─────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)

    grade_cls = (
        "grade-A" if report.letter_grade.startswith("A") else
        "grade-B" if report.letter_grade.startswith("B") else
        "grade-C" if report.letter_grade.startswith("C") else
        "grade-D" if report.letter_grade.startswith("D") else "grade-F"
    )

    with m1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Final Score</div>
          <div class="value">{report.final_score:.3f}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Grade</div>
          <div class="value"><span class="score-badge {grade_cls}">{report.letter_grade}</span></div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Steps</div>
          <div class="value">{summary['steps_taken']}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Completed</div>
          <div class="value">{summary['tasks_completed']}</div>
        </div>""", unsafe_allow_html=True)
    with m5:
        total_reward = summary["total_reward"]
        color = "#4ade80" if total_reward >= 0 else "#f87171"
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Total Reward</div>
          <div class="value" style="color:{color};">{total_reward:+.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋 Step Log", "📊 Score Breakdown", "📈 Reward Chart"])

    with tab1:
        for s in steps:
            cls = "good" if s["reward"] > 0 else ("bad" if s["reward"] < -0.5 else "")
            flags = []
            if s["completed"]:      flags.append("✅ Completed")
            if s["deadline_missed"]: flags.append("⚠️ Deadline missed")
            if s["is_risky"]:        flags.append("⚡ Risky")
            flag_str = "  ".join(flags)
            st.markdown(f"""
            <div class="step-row {cls}">
              <b>Step {s['step']:02d}</b> &nbsp;│&nbsp;
              <b>{s['action']:<12}</b> &nbsp;│&nbsp;
              Reward: <b>{s['reward']:+.4f}</b> &nbsp;│&nbsp;
              Correct: {s['correctness']:.2f} &nbsp;│&nbsp;
              Budget: ${s['budget']:.0f} &nbsp;│&nbsp;
              Risk: {s['risk']:.2f}
              {"&nbsp;&nbsp;" + flag_str if flag_str else ""}
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        dims = {
            "Correctness":        report.correctness_score,
            "Efficiency":         report.efficiency_score,
            "Decision Quality":   report.quality_score,
            "Risk Management":    report.risk_score,
        }
        for dim, val in dims.items():
            color = "#22c55e" if val >= 0.7 else ("#f59e0b" if val >= 0.4 else "#ef4444")
            st.markdown(f"**{dim}**: `{val:.4f}`")
            st.progress(val)

        st.markdown("---")
        bd = report.breakdown
        df = pd.DataFrame({
            "Metric": ["Missed Deadlines", "Escalations Used", "Budget Used ($)", "Final Risk Level"],
            "Value":  [bd["missed_deadlines"], bd["escalations_used"],
                       f"{bd['budget_used']:.1f}", f"{bd['risk_level_final']:.3f}"],
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        if steps:
            rewards = [s["reward"] for s in steps]
            cumulative = [sum(rewards[:i+1]) for i in range(len(rewards))]
            chart_df = pd.DataFrame({
                "Step": list(range(1, len(steps)+1)),
                "Reward":            rewards,
                "Cumulative Reward": cumulative,
            }).set_index("Step")
            st.line_chart(chart_df)


if st.session_state.results:
    task_id, steps, report, summary = st.session_state.results
    st.markdown("---")
    display_results(task_id, steps, report, summary)

# ─────────────────────────────────────────────────────────────────────────────
# All-tasks benchmark
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.all_results:
    st.markdown("---")
    st.markdown("## ⚡ Full Benchmark Results")

    cols = st.columns(3)
    for i, (tid, steps, report, summary) in enumerate(st.session_state.all_results):
        with cols[i]:
            display_results(tid, steps, report, summary)

    # Overall score
    scores = [r.final_score for _, _, r, _ in st.session_state.all_results]
    overall = sum(scores) / len(scores)
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem; background: #0f0f1a;
                border: 1px solid #6366f1; border-radius: 12px; margin-top: 1rem;">
      <div style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase;
                  letter-spacing: 2px; margin-bottom: 0.5rem;">Overall Benchmark Score</div>
      <div style="color: #a78bfa; font-size: 3rem; font-weight: 700;
                  font-family: 'IBM Plex Mono', monospace;">{overall:.4f}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<br><hr>
<div style="text-align:center; color:#475569; font-size:0.8rem;">
  DecisionEnv v1.0 · Meta + HuggingFace OpenEnv Hackathon ·
  <a href="https://huggingface.co" style="color:#6366f1;">Hugging Face</a>
</div>
""", unsafe_allow_html=True)
