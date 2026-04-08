import gymnasium as gym
from gymnasium import spaces
import numpy as np
from environment import DecisionEnv

class GymDecisionEnv(gym.Env):
    def __init__(self, task_id=1):
        self.env = DecisionEnv(task_id=task_id)
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(20,), dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        obs = self.env.reset()
        return obs, {}

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        return obs, reward, done, False, info