import gym
from gym import spaces
import numpy as np

class LGOEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(LGOEnv, self).__init__()
        
        # Define action and observation space
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=np.array([-1.0]), high=np.array([1.0]), dtype=np.float32)
        
        # Initialize state
        self.state = 0.0

    def reset(self):
        self.state = np.random.uniform(low=-0.1, high=0.1)
        return np.array([self.state], dtype=np.float32)

    def step(self, action):
        if action == 0:
            self.state -= 0.1
        elif action == 1:
            self.state += 0.1

        done = bool(self.state < -1.0 or self.state > 1.0)
        reward = -1.0 if done else 1.0 - abs(self.state)

        return np.array([self.state], dtype=np.float32), reward, done, {}

    def render(self, mode='human'):
        print(f"State: {self.state}")

    def close(self):
        pass
