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
        if hasattr(self.agent1, "env"):
            self.agent1.env = self.env
        if hasattr(self.agent2, "env"):
            self.agent2.env = self.env
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
            if not hasattr(self, "_winner_announced"):
                if self.state.winner:
                    print(f"Player {self.state.winner} wins!")
                else:
                    print("Draw")
                self._winner_announced = True
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
        # keep UI state in sync with the underlying environment after the
        # action is executed
        self.current_action_points = self.state.current_action_points
        self.current_player = self.state.current_player
        self.last_step = time.time()
        self.units = self.state.units
        self.sync_hands()


def main():
    # Load the trained model for both players by default.
    agent1 = DQNAgent(GridsEnv())
    agent1.load("dqn_model.pth")
    agent1.epsilon = 0.0
    agent2 = DQNAgent(GridsEnv())
    agent2.load("dqn_model.pth")
    agent2.epsilon = 0.0
    window = AIVsAI(agent1, agent2)
    arcade.run()


if __name__ == "__main__":
    main()
