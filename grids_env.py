import gym
from gym import spaces
import numpy as np

from game_state import GameState
from actions import ActionType
from constants import ROWS, COLUMNS, HAND_CAPACITY
from units import Warrior, Archer, Healer, Trebuchet, Viking
from cards import Fireball, Freeze, StrengthUp, MeteoriteStrike, ActionBlock, Teleport

# Reward multiplier for damage dealt to the opposing commander.
# Increased to provide a greater incentive for targeting the enemy leader.
DAMAGE_REWARD_SCALE = 0.2
# Bonus reward when successfully deploying a unit.
UNIT_DEPLOY_REWARD = 0.2
# Bonus reward when successfully playing a card.
ITEM_USE_REWARD = 0.2
# Bonus reward when successfully attacking an enemy unit.
ATTACK_REWARD = 0.2
# Bonus reward when drawing a card.
DRAW_CARD_REWARD = 0.1

# Map unit and spell types to integer IDs for observation encoding.
UNIT_TYPES = [Warrior, Archer, Healer, Trebuchet, Viking]
UNIT_TYPE_TO_ID = {cls: i + 1 for i, cls in enumerate(UNIT_TYPES)}
SPELL_TYPES = [Fireball, Freeze, StrengthUp, MeteoriteStrike, ActionBlock, Teleport]
SPELL_TYPE_TO_ID = {cls: i + 1 for i, cls in enumerate(SPELL_TYPES)}

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
                spaces.Discrete(len(ActionType)),  # action type
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
                "unit_hand": spaces.MultiDiscrete([len(UNIT_TYPES) + 1] * HAND_CAPACITY),
                "spell_hand": spaces.MultiDiscrete([len(SPELL_TYPES) + 1] * HAND_CAPACITY),
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
        unit_hand = np.zeros(HAND_CAPACITY, dtype=np.int8)
        for i, unit_cls in enumerate(self.state.unit_hand[:HAND_CAPACITY]):
            unit_hand[i] = UNIT_TYPE_TO_ID.get(unit_cls, 0)
        spell_hand = np.zeros(HAND_CAPACITY, dtype=np.int8)
        for i, card in enumerate(self.state.spell_hand[:HAND_CAPACITY]):
            spell_hand[i] = SPELL_TYPE_TO_ID.get(card.__class__, 0)
        return {
            "current_player": self.state.current_player,
            "action_points": self.state.current_action_points,
            "board_owner": board_owner,
            "board_health": board_health,
            "opponent_hand": len(self.state.hands[opponent]),
            "unit_hand": unit_hand,
            "spell_hand": spell_hand,
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
        action_type = ActionType(action_type)

        opponent = 2 if self.state.current_player == 1 else 1
        pre_health = self._commander_health(opponent)

        if action_type == ActionType.MOVE:
            if idx >= len(self.state.units):
                return self._get_obs(), -1.0, True, False, {}
            unit = self.state.units[idx]
            ok = self.state.move_unit(unit, row, col, animate=self.animate)
            reward = 0.0 if ok else -1.0
        elif action_type == ActionType.DEPLOY:
            if idx >= len(self.state.unit_hand):
                return self._get_obs(), -1.0, True, False, {}
            unit_cls = self.state.unit_hand[idx]
            if (row, col) not in self.state.get_valid_deploy_squares():
                return self._get_obs(), -1.0, True, False, {}
            unit = self.state.place_unit(unit_cls, row, col)
            reward = 0.0 if unit else -1.0
            if unit:
                reward += UNIT_DEPLOY_REWARD
        elif action_type == ActionType.PLAY_CARD:
            if idx >= len(self.state.spell_hand):
                return self._get_obs(), -1.0, True, False, {}
            card = self.state.spell_hand[idx]
            ok = self.state.play_card(card, (row, col))
            reward = 0.0 if ok else -1.0
            if ok:
                reward += ITEM_USE_REWARD
        elif action_type == ActionType.ATTACK:
            if idx >= len(self.state.units):
                return self._get_obs(), -1.0, True, False, {}
            attacker = self.state.units[idx]
            target = next((u for u in self.state.units if u.row == row and u.col == col), None)
            if target is None:
                return self._get_obs(), -1.0, True, False, {}
            ok = self.state.attack_unit(attacker, target)
            reward = 0.0 if ok else -1.0
            if ok:
                reward += ATTACK_REWARD
        elif action_type == ActionType.DRAW_SPELL:
            before = len(self.state.spell_hand)
            ok = self.state.draw_cards(
                self.state.spell_deck, self.state.current_player, num=1, ap_cost=1
            )
            reward = 0.0 if ok else -1.0
            if ok and len(self.state.spell_hand) > before:
                reward += DRAW_CARD_REWARD
        elif action_type == ActionType.DRAW_UNIT:
            before = len(self.state.unit_hand)
            ok = self.state.draw_cards(
                self.state.unit_deck, self.state.current_player, num=1, ap_cost=1
            )
            reward = 0.0 if ok else -1.0
            if ok and len(self.state.unit_hand) > before:
                reward += DRAW_CARD_REWARD
        elif action_type == ActionType.END_TURN:
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
                actions.append((ActionType.MOVE, idx, r, c))
            for target in self.state.get_attackable_units(unit):
                actions.append((ActionType.ATTACK, idx, target.row, target.col))
        for idx, unit_cls in enumerate(self.state.unit_hands[player]):
            for r, c in self.state.get_valid_deploy_squares(player):
                actions.append((ActionType.DEPLOY, idx, r, c))
        for idx, card in enumerate(self.state.spell_hands[player]):
            target_cells = set()
            for u in self.state.units:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        r, c = u.row + dr, u.col + dc
                        if 0 <= r < ROWS and 0 <= c < COLUMNS:
                            target_cells.add((r, c))
            for r, c in target_cells:
                actions.append((ActionType.PLAY_CARD, idx, r, c))

        # drawing cards costs 1 action point and is only available when
        # the player has remaining AP and space in hand
        if (
            self.state.spell_decks[player]
            and len(self.state.spell_hands[player]) < HAND_CAPACITY
            and self.state.current_action_points > 0
        ):
            actions.append((ActionType.DRAW_SPELL, 0, 0, 0))
        if (
            self.state.unit_decks[player]
            and len(self.state.unit_hands[player]) < HAND_CAPACITY
            and self.state.current_action_points > 0
        ):
            actions.append((ActionType.DRAW_UNIT, 0, 0, 0))

        # Only allow ending the turn early if no other actions are available or
        # the player has exhausted their action points. This encourages the AI
        # to use all actions each turn.
        if not actions or self.state.current_action_points <= 0:
            actions.append((ActionType.END_TURN, 0, 0, 0))

        return actions

    def render(self):
        if self.render_mode == "human":
            # For brevity no visualization is implemented here.
            print(self._get_obs())
