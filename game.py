import arcade
import heapq
import random

from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, ROWS, COLUMNS,
                       CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, UI_PANEL_WIDTH)
from units import (Unit, Warrior, Archer, Healer, Trebuchet, Viking)
from cards import (Fireball, Freeze, StrengthUp, MeteoriteStrike, ActionBlock)

class GridsGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.grid_origin_x = 0
        self.grid_origin_y = 0

        self.units = []
        self.obstacles = []

        self.current_action_points = 7
        self.current_player = 1
        self.player1BlockedTurnsTimer = 0
        self.player2BlockedTurnsTimer = 0

        self.unit_deck = []
        self.spell_deck = [Fireball(), Freeze(), StrengthUp(), MeteoriteStrike(), ActionBlock()]
        self.unit_hand = []
        self.spell_hand = []

        self.selected_unit = None
        self.move_squares = []

        self.init_board()
        self.draw_cards(self.spell_deck, self.spell_hand, num=3)

    def init_board(self):
        self.units.append(Unit(ROWS // 2, 0, "Commander", owner=1, health=300, attack=20, move_range=2, attack_range=1, cost=1))
        self.units.append(Unit(ROWS // 2, COLUMNS - 1, "Commander", owner=2, health=20, attack=3, move_range=2, attack_range=1, cost=1))
        self.units.append(Warrior(ROWS // 2, 1, owner=1))
        self.units.append(Archer(ROWS // 2 - 1, 0, owner=1))
        self.units.append(Healer(ROWS // 2 + 1, 0, owner=1))
        self.units.append(Viking(ROWS // 2 + 1, COLUMNS - 1, owner=2))
        self.units.append(Trebuchet(ROWS // 2 - 1, COLUMNS - 1, owner=2))

    def draw_cards(self, deck, hand, num=1):
        for _ in range(num):
            if deck:
                card = deck.pop(0)
                hand.append(card)

    def move_unit(self, unit, target_row, target_col):
        path = self.a_star_pathfinding((unit.row, unit.col), (target_row, target_col))
        if not path or len(path) > unit.move_range:
            print("Move not possible!")
            return False

        for step in path:
            unit.row, unit.col = step
        self.current_action_points -= 1
        print(f"{unit.unit_type} moved to ({unit.row}, {unit.col}). AP left: {self.current_action_points}")
        return True

    def end_turn(self):
        print(f"Ending turn for Player {self.current_player}.")
        self.current_action_points = 7
        self.current_player = 2 if self.current_player == 1 else 1
        self.draw_cards(self.spell_deck, self.spell_hand, num=1)

    def play_card(self, card, target):
        if card in self.spell_hand:
            if self.current_action_points < card.cost:
                print("Not enough action points to play this card.")
                return
            card.play(self, target)
            self.spell_hand.remove(card)
            self.current_action_points -= card.cost
            print(f"Played {card.name}. AP left: {self.current_action_points}")
        else:
            print("Card not in hand!")

    def on_draw(self):
        arcade.Window.clear(self)
        for row in range(ROWS):
            for col in range(COLUMNS):
                x = col * CELL_SIZE + CELL_SIZE / 2
                y = row * CELL_SIZE + CELL_SIZE / 2
                if col == 0 or col == COLUMNS - 1:
                    color = arcade.color.LIGHT_GRAY
                else:
                    color = arcade.color.DARK_GRAY
                if (row, col) in self.move_squares:
                    color = arcade.color.LIGHT_BLUE
                cell_rect = arcade.Rect(
                    left=x - CELL_SIZE/2,
                    right=x + CELL_SIZE/2,
                    bottom=y - CELL_SIZE/2,
                    top=y + CELL_SIZE/2,
                    x=x,
                    y=y,
                    width=CELL_SIZE,
                    height=CELL_SIZE
                )
                arcade.draw_rect_outline(cell_rect, color, border_width=2)
                if (row, col) in self.move_squares:
                    arcade.draw_rect_filled(cell_rect, color)
        for unit in self.units:
            unit.draw()
        panel_x = GRID_WIDTH + UI_PANEL_WIDTH / 2
        panel_rect = arcade.Rect(
            left=panel_x - UI_PANEL_WIDTH / 2,
            right=panel_x + UI_PANEL_WIDTH / 2,
            bottom=0,
            top=SCREEN_HEIGHT,
            x=panel_x,
            y=SCREEN_HEIGHT / 2,
            width=UI_PANEL_WIDTH,
            height=SCREEN_HEIGHT,
        )
        arcade.draw_rect_filled(panel_rect, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_text(f"Player {self.current_player} - AP: {self.current_action_points}", GRID_WIDTH + 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 14)
        y_pos = SCREEN_HEIGHT - 60
        arcade.draw_text("Spell Hand:", GRID_WIDTH + 10, y_pos, arcade.color.WHITE, 12)
        y_pos -= 20
        for idx, card in enumerate(self.spell_hand):
            arcade.draw_text(f"{idx}: {card.name} (Cost: {card.cost})", GRID_WIDTH + 10, y_pos - idx * 20, arcade.color.WHITE, 12)

    def on_mouse_press(self, x, y, button, modifiers):
        print(f"Mouse pressed at ({x}, {y})")
        cell = self.get_clicked_cell(x, y)
        if cell:
            row, col = cell
            print(f"Clicked on cell: ({row}, {col})")
            for unit in self.units:
                if unit.row == row and unit.col == col and unit.owner == self.current_player:
                    self.selected_unit = unit
                    self.move_squares = self.get_valid_move_squares(unit)
                    print(f"Selected unit: {unit.unit_type} (Owner: {unit.owner})")
                    return
            if self.selected_unit and (row, col) in self.move_squares:
                self.move_unit(self.selected_unit, row, col)
                self.move_squares = []
                self.selected_unit = None
        else:
            self.selected_unit = None
            self.move_squares = []

    def get_clicked_cell(self, x, y):
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return None
        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)
        return row, col

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
                if any(unit.row == neighbor[0] and unit.col == neighbor[1] for unit in self.units):
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

    def update(self, delta_time):
        for unit in self.units:
            if unit.frozen_turns > 0:
                unit.frozen_turns -= 1
        if self.player1BlockedTurnsTimer > 0:
            self.player1BlockedTurnsTimer -= 1
        if self.player2BlockedTurnsTimer > 0:
            self.player2BlockedTurnsTimer -= 1


def main():
    window = GridsGame()
    arcade.run()
