from units import Unit

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
            target.health -= 3
            print(f"{target.unit_type} hit by Fireball! New health: {target.health}")
        else:
            print("Fireball played on grid cell", target)

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
        for unit in game.units:
            if unit.row == target[0] and unit.col == target[1]:
                unit.health -= 40
                print(f"{unit.unit_type} took damage from Meteorite Strike, health is now {unit.health}.")

class ActionBlock(Card):
    def __init__(self):
        super().__init__("Action Block", cost=3, description="locks 3 of an enemy's action for 4 turn.")

    def play(self, game, target):
        if isinstance(target, Unit):
            if target.owner == 1:
                game.player1BlockedTurnsTimer = 3
                print("player 1 actions are blocked for 3 turns.")
            else:
                game.player2BlockedTurnsTimer = 3
                print("player 2 actions are blocked for 3 turns.")
