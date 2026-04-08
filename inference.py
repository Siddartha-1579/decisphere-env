import os
import json
import asyncio
import httpx
from openai import AsyncOpenAI
from typing import List, Dict, Any

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
API_KEY = os.environ.get("HF_TOKEN", os.environ.get("OPENAI_API_KEY", ""))

ENV_URL = "http://localhost:7860"

def log_start(**kwargs):
    print("[START]")
    print(json.dumps(kwargs), flush=True)

def log_step(**kwargs):
    print("[STEP]")
    print(json.dumps(kwargs), flush=True)

def log_end(**kwargs):
    print("[END]")
    print(json.dumps(kwargs), flush=True)

async def get_model_message(client: AsyncOpenAI, step: int, env_state: Dict[str, Any]) -> str:
    user_prompt = f"Step: {step}. The current environment state is: {json.dumps(env_state)}. \
Evaluate the situation and choose ONE action. \
Available actions: 0=prioritize, 1=delay, 2=allocate, 3=ignore, 4=escalate. \
Reply ONLY with a single digit representing your chosen action."
    
    try:
        completion = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an AI decision-making agent optimizing business resources and minimizing risk. Return only a single integer 0-4."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=10,
        )
        text = (completion.choices[0].message.content or "").strip()
        # Extract first digit found
        for char in text:
            if char in "01234":
                return char
        return "2" # default
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "2" # default allocate


async def main() -> None:
    client = AsyncOpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task="Decision_Task", env="DecisionEnv", model=MODEL_NAME)

    try:
        async with httpx.AsyncClient() as http_client:
            # Reset Env
            resp = await http_client.post(f"{ENV_URL}/reset")
            resp.raise_for_status()
            result = resp.json()
            
            obs = result.get("observation", {})
            last_reward = 0.0
            done = obs.get("done", False)

            for step in range(1, 51):
                if done:
                    break

                # Get Env State for LLM context
                state_resp = await http_client.get(f"{ENV_URL}/state")
                state_resp.raise_for_status()
                env_state = state_resp.json().get("state", {})

                # Call Model
                message = await get_model_message(client, step, env_state)
                action = int(message)

                # Step Env
                step_resp = await http_client.post(f"{ENV_URL}/step/{action}")
                step_resp.raise_for_status()
                step_result = step_resp.json()
                
                obs = step_result.get("observation", {})
                reward = step_result.get("reward", 0.0)
                done = step_result.get("done", False)
                
                rewards.append(reward)
                steps_taken = step
                last_reward = reward

                log_step(step=step, action=message, reward=reward, done=done, error=None)
                
                history.append(f"Step {step}: Action {message} -> reward {reward:+.2f}")

            # Calculate total continuous score
            MAX_TOTAL_REWARD = 50.0  # typical max for 50 steps
            score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
            score = min(max(score, 0.0), 1.0)
            success = score >= 0.5

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())