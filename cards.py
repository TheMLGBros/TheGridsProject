import random
from units import Unit
from constants import CELL_SIZE, ROWS, COLUMNS

class Card:
    def __init__(self, name, cost, description):
        self.name = name
        self.cost = cost
        self.description = description

    def play(self, game, target):
        raise NotImplementedError

class Fireball(Card):
    def __init__(self):
        super().__init__("Fireball", cost=1,
                         description="Creates a lingering fire effect lasting 4 turns, burned targets take 10 between turns, 15 when standing in the fire.")

    def play(self, game, target):
        if isinstance(target, Unit):
            row, col = target.row, target.col
            target.burn_turns = 2
            target.health -= 15
            print(f"{target.unit_type} hit by Fireball! New health: {target.health}")
        else:
            row, col = target
            print("Fireball played on grid cell", target)
        game.fires[(row, col)] = 4

class Freeze(Card):
    def __init__(self):
        super().__init__("Freeze", cost=1, description="Freezes a unit for 4 turns.")

    def play(self, game, target):
        if isinstance(target, Unit):
            target.frozen_turns = 4
            print(f"{target.unit_type} is frozen for 4 turns.")

class StrengthUp(Card):
    def __init__(self):
        super().__init__("Strength Up", cost=1, description="Increases unit attack damage temporarily.")

    def play(self, game, target):
        if isinstance(target, Unit):
            target.attack += 10
            print(f"{target.unit_type}'s attack increased to {target.attack}.")

class MeteoriteStrike(Card):
    def __init__(self):
        super().__init__("Meteorite Strike", cost=2, description="Deals 40 damage to a target square and knocks back adjacent units.")

    def play(self, game, target):
        print("Meteorite Strike at", target)
        row, col = target if not isinstance(target, Unit) else (target.row, target.col)
        for unit in list(game.units):
            if unit.row == row and unit.col == col:
                unit.health -= 40
                print(
                    f"{unit.unit_type} took damage from Meteorite Strike, health is now {unit.health}."
                )
        # knock back adjacent units
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in offsets:
            ar, ac = row + dr, col + dc
            for unit in game.units:
                if unit.row == ar and unit.col == ac:
                    dest_r, dest_c = ar + dr, ac + dc
                    if 0 <= dest_r < ROWS and 0 <= dest_c < COLUMNS and not any(
                        u.row == dest_r and u.col == dest_c for u in game.units
                    ):
                        unit.row = dest_r
                        unit.col = dest_c
                        unit.pixel_x = dest_c * CELL_SIZE + CELL_SIZE / 2
                        unit.pixel_y = dest_r * CELL_SIZE + CELL_SIZE / 2
                        unit.target_pixel_x = unit.pixel_x
                        unit.target_pixel_y = unit.pixel_y

class ActionBlock(Card):
    def __init__(self):
        super().__init__("Action Block", cost=3, description="locks 3 of an enemy's action for 4 turn.")

    def play(self, game, target):
        if isinstance(target, Unit):
            if target.owner == 1:
                game.player1BlockedTurnsTimer = 2
                print("player 1 actions are blocked for 2 turns.")
            else:
                game.player2BlockedTurnsTimer = 2
                print("player 2 actions are blocked for 2 turns.")


class Teleport(Card):
    def __init__(self):
        super().__init__(
            "Teleport",
            cost=4,
            description="Teleport a friendly unit to any square on the board.",
        )

    def play(self, game, target):
        unit = game.selected_unit
        if not unit or unit.owner != game.current_player:
            # If no unit is selected (e.g. AI usage), pick a random friendly unit
            friendly = [u for u in game.units if u.owner == game.current_player]
            if not friendly:
                print("No friendly unit available for teleport.")
                return
            unit = random.choice(friendly)

        if isinstance(target, Unit):
            dest_row, dest_col = target.row, target.col
        else:
            dest_row, dest_col = target

        if any(u.row == dest_row and u.col == dest_col for u in game.units):
            print("Destination occupied!")
            return

        unit.row = dest_row
        unit.col = dest_col
        unit.pixel_x = dest_col * CELL_SIZE + CELL_SIZE / 2
        unit.pixel_y = dest_row * CELL_SIZE + CELL_SIZE / 2
        unit.target_pixel_x = unit.pixel_x
        unit.target_pixel_y = unit.pixel_y
        unit.move_queue = []
        print(f"Teleported {unit.unit_type} to ({dest_row}, {dest_col}).")
