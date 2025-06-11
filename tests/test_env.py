import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import gym
from grids_env import GridsEnv


def test_deploy_action():
    env = GridsEnv()
    assert env.state.unit_hand
    square = env.state.get_valid_deploy_squares()[0]
    action = (1, 0, square[0], square[1])
    obs, reward, term, trunc, _ = env.step(action)
    assert reward == 1.0
    assert any(u.row == square[0] and u.col == square[1] for u in env.state.units)
    assert not term and not trunc
