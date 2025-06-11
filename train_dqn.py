"""Simple DQN self-play training loop for GridsEnv."""

from grids_env import GridsEnv
from dqn_agent import DQNAgent


def train(num_episodes: int = 50, max_steps: int = 50):
    env = GridsEnv()
    agent1 = DQNAgent(env)
    agent2 = DQNAgent(env)
    for ep in range(num_episodes):
        obs, _ = env.reset()
        total_reward = 0.0
        for step in range(max_steps):
            current = env.state.current_player
            agent = agent1 if current == 1 else agent2
            action = agent.select_action(obs)
            next_obs, reward, term, trunc, _ = env.step(action)
            agent.store(obs, action, reward, next_obs, term or trunc)
            agent.update()
            obs = next_obs
            total_reward += reward
            if term or trunc:
                break
        agent1.decay_epsilon()
        agent2.decay_epsilon()
        print(f"Episode {ep+1}: reward={total_reward:.2f}")


if __name__ == "__main__":
    train()
