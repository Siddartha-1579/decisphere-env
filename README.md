---
title: DecisionEnv
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# 🧠 DecisionEnv — Multi-Domain AI Decision-Making Benchmark

> **Meta + Hugging Face OpenEnv Hackathon Submission**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

---

## 📖 Project Overview

**DecisionEnv** is a production-quality reinforcement learning environment that evaluates how well an AI agent makes decisions across real-world human scenarios. Unlike game-based benchmarks, DecisionEnv simulates authentic workplace situations where trade-offs, constraints, and cascading consequences are the norm.

It is designed to be used by companies and researchers to **test, compare, and benchmark** decision-making intelligence in AI systems.

---

## 🎯 Problem Statement

Current AI benchmarks focus heavily on language understanding or narrow game environments. There is a gap in evaluating **real-world operational decision-making**:

- Which task should I handle first?
- How do I allocate limited resources optimally?
- How do I manage a crisis with cascading dependencies?

DecisionEnv fills this gap with three progressively harder domains, a sophisticated reward system, and a reproducible grader — all in a clean, hackathon-ready package.

---

## 🏗️ Environment Design

### Core Class

```python
class DecisionEnv:
    def reset(self) -> np.ndarray        # Initialize state, return observation
    def step(self, action: int)          # Apply action → (obs, reward, done, info)
    def state(self) -> EnvState          # Return full state object
    def render(self) -> str              # Human-readable state dump
    def get_history(self) -> List[Dict]  # Full episode history
    def get_summary(self) -> Dict        # Episode summary statistics
```

### State Space (20-dimensional vector)

| Component | Description |
|---|---|
| `task_id` | Active domain (1–3) |
| `step_count` | Steps elapsed this episode |
| `resources` | Compute (%) and Staff (#) |
| `risk_level` | Global risk float [0–1] |
| `budget_remaining` | Financial budget left |
| `time_remaining` | Time budget left |
| `task_queue[:5]` | Top-5 task urgency and importance scores |

### Action Space (Discrete, n=5)

| ID | Action | Description |
|---|---|---|
| 0 | `prioritize` | Elevate task to top priority |
| 1 | `delay` | Defer task to later |
| 2 | `allocate` | Assign resources to a task |
| 3 | `ignore` | Skip / discard a task |
| 4 | `escalate` | Escalate for more resources / authority |

---

## 🗂️ Multi-Domain Tasks

### Task 1 — Task Prioritization (Easy)

**Scenario**: Six tasks arrive simultaneously, each with urgency and importance scores. The agent must decide which to prioritize, delay, or ignore.

**Input**: Task queue with `{urgency, importance, deadline, cost, risk}`
**Output**: Sequence of `prioritize / delay / ignore / allocate / escalate` decisions
**Evaluation**: How closely decisions match the Eisenhower Matrix optimal ordering

### Task 2 — Resource Allocation (Medium)

**Scenario**: Five projects compete for limited budget and time. Each project has a cost, time requirement, ROI, and urgency. The agent must decide which to fund.

**Input**: Projects with `{cost, time_required, value, roi, urgency}`
**Output**: Allocation decisions that maximise total value within constraints
**Evaluation**: Overlap with greedy-knapsack optimal solution

### Task 3 — Complex Crisis Management (Hard)

**Scenario**: A product launch crisis unfolds with five interconnected issues (security breach → data exposure → regulator → press → morale). Issues have dependency chains — some cannot be resolved until predecessors are handled.

**Input**: Crisis stages with `{urgency, risk, dependency chain}`
**Output**: Correct sequenced resolution decisions
**Evaluation**: Weighted resolution score accounting for dependency satisfaction and global risk reduction

---

## 💰 Reward Design

The reward function has **eight components** and returns values in `[-3.0, +3.0]`:

```
reward = correctness_reward      (+2.0 to -1.0 range)
       + completion_bonus        (+1.5 for successful task resolution)
       + efficiency_bonus        (+0.5 × % steps saved vs max)
       - risk_penalty            (−0.8 × risk_level for risky actions)
       - delay_penalty           (−1.2 if delaying an urgent task)
       - ignore_penalty          (−importance × 1.0 for ignoring high-value tasks)
       ± escalation_modifier     (+0.2 appropriate / −1.0 overuse)
       + domain_modifier         (task-specific bonus/penalty)
```

**Key design principles:**
- Partial rewards prevent sparse gradients for RL training
- Efficiency bonus rewards agents that solve problems quickly
- Risk-compounding means bad early decisions cascade into worse outcomes
- Escalation has diminishing returns (only 3 allowed per episode)

---

## 📊 Grader System

Each episode produces a `GradeReport` with four dimensions:

| Dimension | Description | Weight (Task 1/2/3) |
|---|---|---|
| Correctness | Average decision correctness | 50% / 40% / 35% |
| Efficiency | Steps used vs optimal | 25% / 20% / 15% |
| Decision Quality | Domain-specific metric | 15% / 25% / 30% |
| Risk Management | Final risk + missed deadlines | 10% / 15% / 20% |

**Letter grades**: A+ (≥0.90) → F (< 0.40)

All grades are **deterministic** given the same seed — reproducible for fair comparison.

---

## 🤖 Baseline Agents

### RuleBasedAgent
A logical heuristic agent that:
- Task 1: Prioritizes by urgency × importance (Eisenhower)
- Task 2: Allocates greedily when budget allows; escalates once if tight
- Task 3: Escalates critical items (risk > 0.8), allocates high-urgency, delays low-urgency

### RandomAgent
Selects actions uniformly at random — provides a performance floor for comparison.

---

## 🚀 How to Run Locally

### Prerequisites
```bash
python >= 3.10
```

### Install
```bash
git clone https://github.com/your-repo/decision-env
cd decision-env
pip install -r requirements.txt
```

### Run the CLI demo
```bash
python demo.py
```
Outputs a step-by-step log for all three tasks plus an agent comparison.

### Run the Streamlit UI
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

---

## 🐳 How to Deploy (Hugging Face Spaces)

### Option 1: Docker (Spaces)
1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select **Docker** as the SDK
3. Push this repository — the `Dockerfile` handles everything

### Option 2: Streamlit SDK
1. Create a Space with **Streamlit** SDK
2. Set `app_file: app.py` in `README.md` metadata
3. Push — HF Spaces auto-installs `requirements.txt`

```yaml
---
title: DecisionEnv
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: true
---
```

---

## 📁 File Structure

```
decision-env/
├── environment.py    # Core DecisionEnv class and EnvState
├── tasks.py          # Three domain task handlers
├── grader.py         # Scoring system (0.0–1.0 per episode)
├── agent.py          # RuleBasedAgent + RandomAgent
├── demo.py           # CLI demo runner
├── app.py            # Streamlit web UI
├── openenv.yaml      # OpenEnv specification
├── requirements.txt  # Python dependencies
├── Dockerfile        # HF Spaces Docker config
└── README.md         # This file
```

---

## 🔬 Extending DecisionEnv

- **Add a Task**: Subclass a new domain handler with `reset()`, `step()`, and `is_complete()` methods, register it in `DecisionEnv.__init__`.
- **Train an RL Agent**: The environment is gym-compatible. Drop in any `stable-baselines3` or custom PPO/DQN agent.
- **Custom Reward**: Override `_compute_reward()` in `DecisionEnv` without touching domain logic.

---

## 📜 License

Apache 2.0 — See [LICENSE](LICENSE)

---

*Built for the Meta + Hugging Face OpenEnv Hackathon.*
#   d e c i s p h e r e - e n v  
 