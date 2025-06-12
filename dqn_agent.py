import random
from collections import deque
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from grids_env import GridsEnv
from constants import ROWS, COLUMNS

# Size of the discrete action space. There are seven action types
# (move, deploy, play card, end turn, attack, draw spell, draw unit) so the action space must account
# for all of them.
ACTION_SIZE = 7 * 20 * ROWS * COLUMNS


def action_to_index(action: Tuple[int, int, int, int]) -> int:
    atype, idx, row, col = action
    return ((atype * 20 + idx) * ROWS + row) * COLUMNS + col


def index_to_action(index: int) -> Tuple[int, int, int, int]:
    col = index % COLUMNS
    index //= COLUMNS
    row = index % ROWS
    index //= ROWS
    idx = index % 20
    atype = index // 20
    return atype, idx, row, col


def obs_to_tensor(obs: dict) -> torch.Tensor:
    arr = np.concatenate(
        [
            np.array(
                [
                    obs["current_player"],
                    obs["action_points"],
                    obs["opponent_hand"],
                ],
                dtype=np.float32,
            ),
            obs["board_owner"].astype(np.float32).flatten(),
            obs["board_health"].astype(np.float32).flatten(),
            obs["unit_hand"].astype(np.float32).flatten(),
            obs["spell_hand"].astype(np.float32).flatten(),
        ]
    )
    return torch.from_numpy(arr)


class QNetwork(nn.Module):
    def __init__(self, obs_size: int, action_size: int):
        super().__init__()
        self.fc1 = nn.Linear(obs_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.out = nn.Linear(128, action_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.out(x)


class DQNAgent:
    """Minimal DQN agent for the Grids environment."""

    def __init__(self, env: GridsEnv, lr: float = 1e-3, gamma: float = 0.99,
                 buffer_size: int = 10000, batch_size: int = 64,
                 epsilon_start: float = 1.0, epsilon_end: float = 0.1,
                 epsilon_decay: int = 1000, target_update: int = 100):
        self.env = env
        obs_size = len(obs_to_tensor(env.reset()[0]))
        self.policy_net = QNetwork(obs_size, ACTION_SIZE)
        self.target_net = QNetwork(obs_size, ACTION_SIZE)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=lr)
        self.gamma = gamma
        self.batch_size = batch_size
        self.buffer = deque(maxlen=buffer_size)
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.target_update = target_update
        self.steps_done = 0

    def save(self, path: str) -> None:
        """Persist the agent's policy network to disk."""
        torch.save(self.policy_net.state_dict(), path)

    def load(self, path: str) -> None:
        """Load network weights from ``path`` into the policy and target nets."""
        state_dict = torch.load(path, map_location="cpu")
        self.policy_net.load_state_dict(state_dict)
        self.target_net.load_state_dict(state_dict)

    def select_action(self, obs: dict) -> Tuple[int, int, int, int]:
        valid_actions = self.env.valid_actions()
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        state = obs_to_tensor(obs).unsqueeze(0)
        with torch.no_grad():
            q_values = self.policy_net(state)[0]
        indices = [action_to_index(a) for a in valid_actions]
        best_index = indices[int(torch.argmax(q_values[indices]).item())]
        return index_to_action(best_index)

    def store(self, *transition):
        self.buffer.append(transition)

    def sample(self):
        batch = random.sample(self.buffer, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        states = torch.stack([obs_to_tensor(o) for o in states])
        actions = torch.tensor([action_to_index(a) for a in actions])
        rewards = torch.tensor(rewards, dtype=torch.float32)
        next_states = torch.stack([obs_to_tensor(o) for o in next_states])
        dones = torch.tensor(dones, dtype=torch.float32)
        return states, actions, rewards, next_states, dones

    def update(self):
        if len(self.buffer) < self.batch_size:
            return
        states, actions, rewards, next_states, dones = self.sample()
        q_values = self.policy_net(states).gather(1, actions.view(-1, 1)).squeeze()
        with torch.no_grad():
            next_q = self.target_net(next_states).max(1)[0]
            target = rewards + self.gamma * next_q * (1 - dones)
        loss = F.mse_loss(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.steps_done % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        self.steps_done += 1

    def decay_epsilon(self):
        self.epsilon = max(
            self.epsilon_end,
            self.epsilon - (1.0 - self.epsilon_end) / self.epsilon_decay,
        )

