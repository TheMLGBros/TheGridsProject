import random
from grids_env import GridsEnv

class RandomAgent:
    """Agent that selects a random valid action."""
    def act(self, env: GridsEnv):
        actions = env.valid_actions()
        return random.choice(actions) if actions else (2,0,0,0)
