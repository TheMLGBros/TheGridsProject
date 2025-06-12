import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import gym
from grids_env import (
    GridsEnv,
    UNIT_DEPLOY_REWARD,
    ATTACK_REWARD,
    DRAW_CARD_REWARD,
    ITEM_USE_REWARD,
)
from actions import ActionType
from game_state import GameState
from units import Warrior


def test_observation_contains_hand_info():
    env = GridsEnv()
    obs, _ = env.reset()
    assert "unit_hand" in obs and "spell_hand" in obs
    assert len(obs["unit_hand"]) == 10
    assert len(obs["spell_hand"]) == 10


def test_deploy_action():
    env = GridsEnv()
    assert env.state.unit_hand
    square = env.state.get_valid_deploy_squares()[0]
    action = (ActionType.DEPLOY, 0, square[0], square[1])
    obs, reward, term, trunc, _ = env.step(action)
    assert reward == UNIT_DEPLOY_REWARD
    assert any(u.row == square[0] and u.col == square[1] for u in env.state.units)
    assert not term and not trunc


def test_game_winner_set_on_commander_death():
    state = GameState()
    commander = next(u for u in state.units if u.owner == 2 and u.unit_type == "Commander")
    attacker = Warrior(commander.row, commander.col - 1, owner=1)
    state.units.append(attacker)
    commander.health = 1
    state.attack_unit(attacker, commander)
    assert state.winner == 1


def test_env_terminates_when_commander_dies():
    env = GridsEnv()
    commander = next(u for u in env.state.units if u.owner == 2 and u.unit_type == "Commander")
    attacker = Warrior(commander.row, commander.col - 1, owner=1)
    env.state.units.append(attacker)
    commander.health = 1
    env.state.attack_unit(attacker, commander)
    obs, reward, term, trunc, _ = env.step((ActionType.END_TURN, 0, 0, 0))
    assert term
    assert env.state.winner == 1


def test_play_card_action():
    env = GridsEnv()
    assert env.state.spell_hand
    action = (ActionType.PLAY_CARD, 0, 0, 0)
    obs, reward, term, trunc, _ = env.step(action)
    assert reward >= ITEM_USE_REWARD


def test_attack_action():
    env = GridsEnv()
    # Replace initial units with two adjacent warriors for a deterministic test
    attacker = Warrior(0, 0, owner=1)
    target = Warrior(0, 1, owner=2)
    env.state.units = [attacker, target]
    env.state.current_player = 1
    action = (ActionType.ATTACK, 0, target.row, target.col)
    obs, reward, term, trunc, _ = env.step(action)
    assert reward == ATTACK_REWARD
    assert target.health < target.max_health


def test_draw_spell_action():
    env = GridsEnv()
    hand_before = len(env.state.spell_hand)
    ap_before = env.state.current_action_points
    action = (ActionType.DRAW_SPELL, 0, 0, 0)
    obs, reward, term, trunc, _ = env.step(action)
    assert len(env.state.spell_hand) == hand_before + 1
    assert env.state.current_action_points == ap_before - 1
    assert reward == DRAW_CARD_REWARD

