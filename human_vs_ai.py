import time
import arcade
from game import GridsGame
from grids_env import GridsEnv
from agents import RandomAgent
from dqn_agent import DQNAgent


class HumanVsAI(GridsGame):
    """Play against an AI opponent using the regular GUI."""

    def __init__(self, agent, ai_player: int = 2, step_delay: float = 0.5):
        self.env = GridsEnv(animate=True)
        self.agent = agent
        if hasattr(self.agent, "env"):
            self.agent.env = self.env
        self.ai_player = ai_player
        self.step_delay = step_delay
        super().__init__()
        # use the environment state so AI and GUI stay in sync
        self.state = self.env.state
        self.sync_hands()
        self.units = self.state.units
        self.obstacles = self.state.obstacles
        self.last_step = time.time()

    def on_update(self, delta_time):
        super().on_update(delta_time)
        if self.state.winner:
            if not hasattr(self, "_winner_announced"):
                if self.state.winner == self.ai_player:
                    print("AI wins!")
                else:
                    print("You win!" if self.state.winner else "Draw")
                self._winner_announced = True
            return
        if self.state.current_player != self.ai_player:
            return
        if time.time() - self.last_step < self.step_delay:
            return
        obs = self.env._get_obs()
        if hasattr(self.agent, "select_action"):
            action = self.agent.select_action(obs)
        else:
            action = self.agent.act(self.env)
        self.env.step(action)
        # refresh UI state so action points and player display correctly
        self.current_action_points = self.state.current_action_points
        self.current_player = self.state.current_player
        self.units = self.state.units
        self.sync_hands()
        self.last_step = time.time()


def main():
    # Use the trained model when available.
    agent = DQNAgent(GridsEnv())
    agent.load("dqn_model.pth")
    agent.epsilon = 0.0
    window = HumanVsAI(agent)
    arcade.run()


if __name__ == "__main__":
    main()
