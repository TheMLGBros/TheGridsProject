import arcade
from constants import CELL_SIZE
from entities import GameEntity

class Unit(GameEntity):
    def __init__(self, row, col, unit_type, owner, health, attack, move_range, attack_range, cost):
        super().__init__(row, col)
        self.unit_type = unit_type
        self.owner = owner  # e.g., player 1 or 2
        self.health = health
        self.attack = attack
        self.move_range = move_range
        self.attack_range = attack_range
        self.cost = cost
        # Additional status flags
        self.frozen_turns = 0
        self.action_blocked = False

    def draw(self):
        color = arcade.color.BLUE if self.owner == 1 else arcade.color.RED
        x = self.col * CELL_SIZE + CELL_SIZE / 2
        y = self.row * CELL_SIZE + CELL_SIZE / 2
        arcade.draw_circle_filled(x, y, CELL_SIZE / 2 - 4, color)
        arcade.draw_text(
            self.unit_type,
            x,
            y,
            arcade.color.WHITE,
            10,
            anchor_x="center",
            anchor_y="center",
        )

class Warrior(Unit):
    def __init__(self, row, col, owner):
        super().__init__(row, col, "Warrior", owner, health=100, attack=40, move_range=2, attack_range=1, cost=2)

class Archer(Unit):
    def __init__(self, row, col, owner):
        super().__init__(row, col, "Archer", owner, health=80, attack=20, move_range=2, attack_range=4, cost=2)

class Healer(Unit):
    def __init__(self, row, col, owner):
        super().__init__(row, col, "Healer", owner, health=80, attack=30, move_range=3, attack_range=3, cost=2)

class Trebuchet(Unit):
    def __init__(self, row, col, owner):
        super().__init__(row, col, "Trebuchet", owner, health=70, attack=20, move_range=1, attack_range=99, cost=3)

class Viking(Unit):
    def __init__(self, row, col, owner):
        super().__init__(row, col, "Viking", owner, health=90, attack=60, move_range=1, attack_range=1, cost=2)
