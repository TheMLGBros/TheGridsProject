import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import gym
from grids_env import GridsEnv
from game_state import GameState


def test_deploy_action():
    env = GridsEnv()
    assert env.state.unit_hand
    square = env.state.get_valid_deploy_squares()[0]
    action = (1, 0, square[0], square[1])
    obs, reward, term, trunc, _ = env.step(action)
    assert reward == 1.0
    assert any(u.row == square[0] and u.col == square[1] for u in env.state.units)
    assert not term and not trunc


def test_game_winner_set_on_commander_death():
    state = GameState()
    attacker = next(u for u in state.units if u.owner == 1 and u.unit_type != "Commander")
    commander = next(u for u in state.units if u.owner == 2 and u.unit_type == "Commander")
    commander.health = 1
    state.attack_unit(attacker, commander)
    assert state.winner == 1


def test_env_terminates_when_commander_dies():
    env = GridsEnv()
    attacker = next(u for u in env.state.units if u.owner == 1 and u.unit_type != "Commander")
    commander = next(u for u in env.state.units if u.owner == 2 and u.unit_type == "Commander")
    commander.health = 1
    env.state.attack_unit(attacker, commander)
    obs, reward, term, trunc, _ = env.step((2, 0, 0, 0))
    assert term
    assert env.state.winner == 1
