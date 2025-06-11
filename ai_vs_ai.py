import time
import arcade
from game import GridsGame
from grids_env import GridsEnv
from agents import RandomAgent
from dqn_agent import DQNAgent

class AIVsAI(GridsGame):
    """Visualize two AI agents playing against each other."""
    def __init__(self, agent1, agent2, step_delay: float = 0.5):
        self.env = GridsEnv(animate=True)
        self.agent1 = agent1
        self.agent2 = agent2
        self.step_delay = step_delay
        super().__init__()
        # replace the state created by ``GridsGame`` with the environment state
        self.state = self.env.state
        self.sync_hands()
        self.units = self.state.units
        self.obstacles = self.state.obstacles
        self.last_step = time.time()

    def on_update(self, delta_time):
        super().on_update(delta_time)
        if self.state.winner:
            return
        if time.time() - self.last_step < self.step_delay:
            return
        obs = self.env._get_obs()
        player = self.state.current_player
        agent = self.agent1 if player == 1 else self.agent2
        if hasattr(agent, "select_action"):
            action = agent.select_action(obs)
        else:
            action = agent.act(self.env)
        self.env.step(action)
        self.last_step = time.time()
        self.units = self.state.units
        self.sync_hands()


def main():
    # Start with two random agents. Trained models can be loaded by
    # replacing the agents below with ``DQNAgent`` instances and calling
    # ``load`` with a saved weight file.
    agent1 = RandomAgent()
    agent2 = RandomAgent()
    window = AIVsAI(agent1, agent2)
    arcade.run()


if __name__ == "__main__":
    main()
