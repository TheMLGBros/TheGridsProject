# Game state logic for grids environment
import heapq
import random
from constants import ROWS, COLUMNS, CELL_SIZE, HAND_CAPACITY
from units import (
    Unit,
    Warrior,
    Archer,
    Healer,
    Trebuchet,
    Viking,
)
from cards import (
    Card,
    Fireball,
    Freeze,
    StrengthUp,
    MeteoriteStrike,
    ActionBlock,
    Teleport,
)

class GameState:
    """Headless game state detached from rendering."""

    def __init__(self):
        self.units = []
        self.obstacles = []
        self.current_action_points = 7
        self.current_player = 1
        self.player1BlockedTurnsTimer = 0
        self.player2BlockedTurnsTimer = 0

        # stateful selections used by some cards
        self.selected_unit = None

        self.unit_deck = [Warrior, Archer, Healer, Trebuchet, Viking]
        self.spell_deck = [
            Fireball(),
            Freeze(),
            StrengthUp(),
            MeteoriteStrike(),
            ActionBlock(),
            Teleport(),
        ]

        # hands are unique per player but share one combined list of units and spells
        self.hands = {1: [], 2: []}
        self.unit_hands = {1: [], 2: []}
        self.spell_hands = {1: [], 2: []}

        self.init_board()
        # give the starting player an initial hand
        self.draw_cards(self.spell_deck, self.current_player, num=3)
        self.draw_cards(self.unit_deck, self.current_player, num=3)

        # convenience references for the current player
        self.refresh_player_hands()

    def refresh_player_hands(self):
        """Update convenience references for the current player."""
        self.hand = self.hands[self.current_player]
        self.unit_hand = self.unit_hands[self.current_player]
        self.spell_hand = self.spell_hands[self.current_player]

    def init_board(self):
        self.units.append(Unit(ROWS // 2, 0, "Commander", owner=1, health=300, attack=20, move_range=2, attack_range=1, cost=1))
        self.units.append(Unit(ROWS // 2, COLUMNS - 1, "Commander", owner=2, health=20, attack=3, move_range=2, attack_range=1, cost=1))
        self.units.append(Warrior(ROWS // 2, 1, owner=1))
        self.units.append(Archer(ROWS // 2 - 1, 0, owner=1))
        self.units.append(Healer(ROWS // 2 + 1, 0, owner=1))
        self.units.append(Viking(ROWS // 2 + 1, COLUMNS - 1, owner=2))
        self.units.append(Trebuchet(ROWS // 2 - 1, COLUMNS - 1, owner=2))

    def draw_cards(self, deck, player, num=1):
        """Draw cards from a deck into the specified player's hand."""
        hand = self.hands[player]
        for _ in range(num):
            if deck and len(hand) < HAND_CAPACITY:
                card = deck.pop(0)
                hand.append(card)
                if isinstance(card, Card):
                    self.spell_hands[player].append(card)
                elif isinstance(card, type) and issubclass(card, Unit):
                    self.unit_hands[player].append(card)

    # ---------- Core game mechanics ----------
    def move_unit(self, unit, target_row, target_col, animate=False):
        path = self.a_star_pathfinding((unit.row, unit.col), (target_row, target_col))
        if not path or len(path) > unit.move_range:
            return False
        final_row, final_col = path[-1]
        if animate:
            unit.start_move(path)
        else:
            unit.row = final_row
            unit.col = final_col
            unit.pixel_x = final_col * CELL_SIZE + CELL_SIZE / 2
            unit.pixel_y = final_row * CELL_SIZE + CELL_SIZE / 2
            unit.target_pixel_x = unit.pixel_x
            unit.target_pixel_y = unit.pixel_y
            unit.move_queue = []
        self.current_action_points -= 1
        return True

    def attack_unit(self, attacker, target):
        if target.health <= 0:
            return
        target.health -= attacker.attack
        dr = target.row - attacker.row
        dc = target.col - attacker.col
        knock_row = target.row + (1 if dr > 0 else -1 if dr < 0 else 0)
        knock_col = target.col + (1 if dc > 0 else -1 if dc < 0 else 0)
        if 0 <= knock_row < ROWS and 0 <= knock_col < COLUMNS:
            if not any(u.row == knock_row and u.col == knock_col for u in self.units):
                if attacker != target:
                    target.row = knock_row
                    target.col = knock_col
                    # keep pixel values in sync with logical position so
                    # pathfinding and rendering remain consistent after
                    # knockback. Missing this update previously meant units
                    # could visually stay in place while their logical
                    # location changed, allowing other units to occupy the
                    # same square.
                    target.pixel_x = knock_col * CELL_SIZE + CELL_SIZE / 2
                    target.pixel_y = knock_row * CELL_SIZE + CELL_SIZE / 2
                    target.target_pixel_x = target.pixel_x
                    target.target_pixel_y = target.pixel_y
                    target.move_queue = []
        return True

    def end_turn(self):
        self.current_action_points = 7
        self.current_player = 2 if self.current_player == 1 else 1
        self.draw_cards(self.spell_deck, self.current_player, num=1)
        self.refresh_player_hands()

    def play_card(self, card, target):
        player = self.current_player
        if card not in self.spell_hands[player]:
            return False
        if self.current_action_points < card.cost:
            return False
        card.play(self, target)
        self.spell_hands[player].remove(card)
        if card in self.hands[player]:
            self.hands[player].remove(card)
        self.current_action_points -= card.cost
        self.refresh_player_hands()
        return True

    # ---------- Helpers ----------
    def get_valid_move_squares(self, unit):
        valid_moves = []
        for row in range(ROWS):
            for col in range(COLUMNS):
                if (row, col) == (unit.row, unit.col):
                    continue
                path = self.a_star_pathfinding((unit.row, unit.col), (row, col))
                if path and len(path) <= unit.move_range:
                    valid_moves.append((row, col))
        return valid_moves

    def get_attackable_units(self, unit):
        targets = []
        for other in self.units:
            if other.owner != unit.owner:
                dist = self.manhattan_distance((unit.row, unit.col), (other.row, other.col))
                if dist <= unit.attack_range:
                    targets.append(other)
        return targets

    def a_star_pathfinding(self, start, goal):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        open_list = []
        heapq.heappush(open_list, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.manhattan_distance(start, goal)}
        while open_list:
            _, current = heapq.heappop(open_list)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            for dr, dc in directions:
                neighbor = (current[0] + dr, current[1] + dc)
                if not (0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLUMNS):
                    continue
                if any(u.row == neighbor[0] and u.col == neighbor[1] for u in self.units):
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.manhattan_distance(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))
        return []

    def manhattan_distance(self, cell1, cell2):
        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])

    def update(self):
        for unit in self.units:
            if unit.frozen_turns > 0:
                unit.frozen_turns -= 1
        self.units = [u for u in self.units if u.health > 0]
