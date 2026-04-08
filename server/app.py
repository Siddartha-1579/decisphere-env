# server/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# allow importing environment.py from parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from environment import DecisionEnv
from .models import DecisionObservation, ResetResponse, StepResponse, StateResponse

# -----------------------------
# FastAPI app setup
# -----------------------------
app = FastAPI(title="DeciSphere AI Backend")

# ✅ CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Global environment instance
# -----------------------------
env = DecisionEnv()

# Reward tracking
reward_history = []
current_total_reward = 0

# -----------------------------
# Endpoints
# -----------------------------

@app.get("/")
def root():
    return {"message": "DeciSphere backend running"}


@app.post("/reset", response_model=ResetResponse)
@app.get("/reset", response_model=ResetResponse)
def reset():
    global env, reward_history, current_total_reward

    env.reset()
    reward_history = []
    current_total_reward = 0

    env_state = env.state()

    obs = DecisionObservation(
        step=0,
        max_steps=50,
        total_reward=0,
        risk_level=env_state.risk_level,
        budget_remaining=env_state.budget_remaining,
        correctness=0.9999,
        escalations_used=env_state.escalation_count,
        reward_history=[],
        action_distribution=[],
        task_name="DecisionEnv Reset",
        done=False,
    )
    return ResetResponse(observation=obs)


@app.post("/step/{action}", response_model=StepResponse)
@app.get("/step/{action}", response_model=StepResponse)
def step(action: int):
    global current_total_reward, reward_history

    # Take a step in DecisionEnv
    result = env.step(action)
    env_state = env.state()

    # Get reward and clamp strictly between 0 and 1
    reward = result.get("reward", 0.5) if isinstance(result, dict) else 0.5
    reward = max(0.0001, min(0.9999, reward))

    # -----------------------------
    # ✅ Debug log for Step 1: print reward
    # -----------------------------
    print(f"Step {len(reward_history)+1} - reward: {reward}")

    # Update total reward
    current_total_reward += reward

    # Track reward history
    reward_history.append(
        {
            "step": len(reward_history) + 1,
            "reward": reward,
        }
    )

    obs = DecisionObservation(
        step=len(reward_history),
        max_steps=50,
        total_reward=current_total_reward,
        risk_level=env_state.risk_level,
        budget_remaining=env_state.budget_remaining,
        correctness=max(0.0001, min(0.9999, 1 - env_state.risk_level)),
        escalations_used=env_state.escalation_count,
        reward_history=reward_history,
        action_distribution=[
            {
                "name": f"Action {action}",
                "value": 1,
            }
        ],
        task_name=f"Decision Action {action}",
        done=len(reward_history) >= 50,
    )

    return StepResponse(
        observation=obs,
        reward=reward,
        done=obs.done,
        info={"action": action, "risk_level": env_state.risk_level}
    )

@app.get("/state", response_model=StateResponse)
def state():
    env_state = env.state()
    return StateResponse(
        state={
            "risk_level": env_state.risk_level if env_state else 0,
            "budget_remaining": env_state.budget_remaining if env_state else 0,
            "escalation_count": env_state.escalation_count if env_state else 0,
        }
    )