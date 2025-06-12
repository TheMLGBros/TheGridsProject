from grids_env import GridsEnv
from agents import RandomAgent


def self_play(num_episodes=5, max_steps=50):
    env = GridsEnv()
    agents = {1: RandomAgent(), 2: RandomAgent()}
    for ep in range(num_episodes):
        obs, _ = env.reset()
        for step in range(max_steps):
            player = env.state.current_player
            action = agents[player].act(env)
            obs, reward, term, trunc, _ = env.step(action)
            if term or trunc:
                break
        if env.state.winner:
            print(f"Episode {ep+1} finished - Player {env.state.winner} wins")
        else:
            print(f"Episode {ep+1} finished - Draw")


if __name__ == "__main__":
    self_play()
