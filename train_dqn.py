"""Simple DQN self-play training loop for GridsEnv.

After training completes a progress graph and some statistics are
displayed. The learned weights of ``agent1`` are saved to ``dqn_model.pth``.
"""

from typing import List, Optional

import numpy as np
import matplotlib.pyplot as plt

from grids_env import GridsEnv
from dqn_agent import DQNAgent


def _print_table(rows: List[List[str]], title: str) -> None:
    """Utility to print a simple two column table."""
    print(f"\n{title}\n" + "-" * len(title))
    col_width = max(len(str(r[0])) for r in rows) + 2
    for name, value in rows:
        print(f"{name:<{col_width}}{value}")


def train(num_episodes: int = 50, max_steps: int = 50) -> None:
    env = GridsEnv()
    agent1 = DQNAgent(env)
    agent2 = DQNAgent(env)

    episode_rewards: List[float] = []
    episode_lengths: List[int] = []
    winners: List[Optional[int]] = []

    for ep in range(num_episodes):
        obs, _ = env.reset()
        total_reward = 0.0
        step_count = 0
        winner: Optional[int] = None

        for step in range(max_steps):
            current = env.state.current_player
            agent = agent1 if current == 1 else agent2
            action = agent.select_action(obs)
            next_obs, reward, term, trunc, _ = env.step(action)
            agent.store(obs, action, reward, next_obs, term or trunc)
            agent.update()
            obs = next_obs
            total_reward += reward
            step_count += 1
            if term or trunc:
                winner = env.state.winner
                break

        episode_rewards.append(total_reward)
        episode_lengths.append(step_count)
        winners.append(winner)

        agent1.decay_epsilon()
        agent2.decay_epsilon()
        print(f"Episode {ep+1}: reward={total_reward:.2f}")

    # persist the learned policy for later use
    agent1.save("dqn_model.pth")
    print("Model saved to dqn_model.pth")

    # ------------------------------------------------------------------
    # Display progress graph
    episodes = np.arange(1, num_episodes + 1)
    plt.figure(figsize=(8, 4))
    plt.plot(episodes, episode_rewards, label="Episode reward")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.title("Training Progress")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("training_progress.png")
    plt.show()

    # Calculate stats
    avg_reward = float(np.mean(episode_rewards))
    max_reward = float(np.max(episode_rewards))
    min_reward = float(np.min(episode_rewards))
    avg_length = float(np.mean(episode_lengths))
    a1_wins = sum(1 for w in winners if w == 1)
    a2_wins = sum(1 for w in winners if w == 2)
    draws = sum(1 for w in winners if w is None)

    stats_rows = [
        ["Average Reward", f"{avg_reward:.2f}"],
        ["Max Reward", f"{max_reward:.2f}"],
        ["Min Reward", f"{min_reward:.2f}"],
        ["Average Episode Length", f"{avg_length:.2f}"],
        ["Agent1 Wins", a1_wins],
        ["Agent2 Wins", a2_wins],
        ["Draws", draws],
    ]
    _print_table(stats_rows, "Training Statistics")

    # Fun statistics
    highest_ep = int(np.argmax(episode_rewards)) + 1
    total_steps = sum(episode_lengths)
    fun_rows = [
        ["Episode with Highest Reward", highest_ep],
        ["Final Epsilon (Agent1)", f"{agent1.epsilon:.2f}"],
        ["Final Epsilon (Agent2)", f"{agent2.epsilon:.2f}"],
        ["Total Steps", total_steps],
    ]
    _print_table(fun_rows, "Fun Statistics")


if __name__ == "__main__":
    train()
