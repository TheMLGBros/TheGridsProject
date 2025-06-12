import gym
from gym import spaces
import numpy as np

from game_state import GameState
from constants import ROWS, COLUMNS

# Reward multiplier for damage dealt to the opposing commander.
DAMAGE_REWARD_SCALE = 0.1
# Bonus reward when successfully deploying a unit.
UNIT_DEPLOY_REWARD = 0.2
# Bonus reward when successfully playing a card.
ITEM_USE_REWARD = 0.2

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
                spaces.Discrete(4),  # 0=move, 1=deploy, 2=play card, 3=end turn
                spaces.Discrete(20),  # unit or hand index
                spaces.Discrete(ROWS),
                spaces.Discrete(COLUMNS),
            )
        )
        self.observation_space = spaces.Dict(
            {
                "current_player": spaces.Discrete(3),
                "action_points": spaces.Discrete(100),
                "board_owner": spaces.Box(0, 2, (ROWS, COLUMNS), dtype=np.int8),
                "board_health": spaces.Box(0, 500, (ROWS, COLUMNS), dtype=np.int16),
                "opponent_hand": spaces.Discrete(11),
            }
        )

    # ------------------------------------------------------------------
    def _get_obs(self):
        board_owner = np.zeros((ROWS, COLUMNS), dtype=np.int8)
        board_health = np.zeros((ROWS, COLUMNS), dtype=np.int16)
        for unit in self.state.units:
            board_owner[unit.row, unit.col] = unit.owner
            board_health[unit.row, unit.col] = unit.health
        opponent = 2 if self.state.current_player == 1 else 1
        return {
            "current_player": self.state.current_player,
            "action_points": self.state.current_action_points,
            "board_owner": board_owner,
            "board_health": board_health,
            "opponent_hand": len(self.state.hands[opponent]),
        }

    def _commander_health(self, player: int) -> int:
        """Return the current health of ``player``'s commander."""
        for unit in self.state.units:
            if unit.owner == player and unit.unit_type == "Commander":
                return unit.health
        return 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.state = GameState()
        return self._get_obs(), {}

    def step(self, action):
        action_type, idx, row, col = action

        opponent = 2 if self.state.current_player == 1 else 1
        pre_health = self._commander_health(opponent)

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
            if unit:
                reward += UNIT_DEPLOY_REWARD
        elif action_type == 2:  # play card from hand
            if idx >= len(self.state.spell_hand):
                return self._get_obs(), -1.0, True, False, {}
            card = self.state.spell_hand[idx]
            ok = self.state.play_card(card, (row, col))
            reward = 1.0 if ok else -1.0
            if ok:
                reward += ITEM_USE_REWARD
        elif action_type == 3:  # end turn
            self.state.end_turn()
            reward = 0.0
        else:
            # unsupported action type
            return self._get_obs(), -1.0, True, False, {}

        if self.state.current_action_points <= 0:
            self.state.end_turn()

        post_health = self._commander_health(opponent)
        damage = max(0, pre_health - post_health)
        if damage:
            reward += damage * DAMAGE_REWARD_SCALE

        terminated = self.state.winner is not None
        truncated = False
        return self._get_obs(), reward, terminated, truncated, {}

    def valid_actions(self):
        actions = []
        player = self.state.current_player
        for idx, unit in enumerate(self.state.units):
            if unit.owner != player:
                continue
            for r, c in self.state.get_valid_move_squares(unit):
                actions.append((0, idx, r, c))
        for idx, unit_cls in enumerate(self.state.unit_hands[player]):
            for r, c in self.state.get_valid_deploy_squares(player):
                actions.append((1, idx, r, c))
        for idx, card in enumerate(self.state.spell_hands[player]):
            for r in range(ROWS):
                for c in range(COLUMNS):
                    actions.append((2, idx, r, c))
        actions.append((3, 0, 0, 0))
        return actions

    def render(self):
        if self.render_mode == "human":
            # For brevity no visualization is implemented here.
            print(self._get_obs())
