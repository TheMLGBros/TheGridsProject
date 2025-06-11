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
                spaces.Discrete(2),  # 0=move unit, 1=deploy unit
                spaces.Discrete(20),  # unit or hand index
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
        action_type, idx, row, col = action

        if action_type == 0:  # move existing unit
            if idx >= len(self.state.units):
                return self._get_obs(), -1.0, True, False, {}
            unit = self.state.units[idx]
            ok = self.state.move_unit(unit, row, col, animate=self.animate)
            reward = 1.0 if ok else -1.0
        elif action_type == 1:  # deploy unit from hand
            if idx >= len(self.state.unit_hand):
                return self._get_obs(), -1.0, True, False, {}
            unit_cls = self.state.unit_hand[idx]
            if (row, col) not in self.state.get_valid_deploy_squares():
                return self._get_obs(), -1.0, True, False, {}
            unit = self.state.place_unit(unit_cls, row, col)
            reward = 1.0 if unit else -1.0
        else:
            # unsupported action type
            return self._get_obs(), -1.0, True, False, {}

        terminated = False
        truncated = False
        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        if self.render_mode == "human":
            # For brevity no visualization is implemented here.
            print(self._get_obs())
