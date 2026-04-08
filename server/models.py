from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class DecisionObservation(BaseModel):
    step: int
    max_steps: int
    total_reward: float
    risk_level: float
    budget_remaining: float
    correctness: float
    escalations_used: int
    reward_history: List[Dict[str, Any]]
    action_distribution: List[Dict[str, Any]]
    task_name: str
    done: bool

class ResetResponse(BaseModel):
    observation: DecisionObservation

class StepResponse(BaseModel):
    observation: DecisionObservation
    reward: float
    done: bool
    info: Dict[str, Any] = {}

class StateResponse(BaseModel):
    state: Dict[str, Any]
