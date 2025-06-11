import gym
from gym import spaces

from game_state import GameState
from constants import ROWS, COLUMNS

class GridsEnv(gym.Env):
    """Gym-compatible environment wrapping :class:`GameState`."""

    metadata = {"render_modes": ["human"]}

    def __init__(self, render_mode=None, animate=False):
        super().__init__()
        self.render_mode = render_mode
        self.animate = animate
        self.state = GameState()
        self.action_space = spaces.Tuple(
            (
                spaces.Discrete(20),  # unit index
                spaces.Discrete(ROWS),
                spaces.Discrete(COLUMNS),
            )
        )
        self.observation_space = spaces.Dict(
            {
                "current_player": spaces.Discrete(3),
                "action_points": spaces.Discrete(100),
            }
        )

    # ------------------------------------------------------------------
    def _get_obs(self):
        return {
            "current_player": self.state.current_player,
            "action_points": self.state.current_action_points,
        }

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.state = GameState()
        return self._get_obs(), {}

    def step(self, action):
        unit_idx, row, col = action
        if unit_idx >= len(self.state.units):
            return self._get_obs(), -1.0, True, False, {}
        unit = self.state.units[unit_idx]
        ok = self.state.move_unit(unit, row, col, animate=self.animate)
        reward = 1.0 if ok else -1.0
        terminated = False
        truncated = False
        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        if self.render_mode == "human":
            # For brevity no visualization is implemented here.
            print(self._get_obs())
