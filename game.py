import arcade
import heapq
import random

from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, ROWS, COLUMNS,
                       CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, UI_PANEL_WIDTH)
from units import (Unit, Warrior, Archer, Healer, Trebuchet, Viking)
from cards import (
    Fireball,
    Freeze,
    StrengthUp,
    MeteoriteStrike,
    ActionBlock,
    Teleport,
)

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

        self.unit_deck = [
            Warrior,
            Archer,
            Healer,
            Trebuchet,
            Viking,
        ]
        self.spell_deck = [
            Fireball(),
            Freeze(),
            StrengthUp(),
            MeteoriteStrike(),
            ActionBlock(),
            Teleport(),
        ]
        self.unit_hand = []
        self.spell_hand = []

        self.selected_unit = None
        self.selected_card_index = None
        self.move_squares = []
        self.attack_targets = []

        # UI element rectangles
        self.end_turn_button = {
            'center_x': GRID_WIDTH + UI_PANEL_WIDTH / 2,
            'center_y': 40,
            'width': 120,
            'height': 30,
        }
        self.draw_card_button = {
            'center_x': GRID_WIDTH + UI_PANEL_WIDTH / 2,
            'center_y': 80,
            'width': 120,
            'height': 30,
        }
        self.draw_unit_button = {
            'center_x': GRID_WIDTH + UI_PANEL_WIDTH / 2,
            'center_y': 120,
            'width': 120,
            'height': 30,
        }
        self.card_rects = []
        self.unit_card_rects = []

        self.init_board()
        self.draw_cards(self.spell_deck, self.spell_hand, num=3)
        self.draw_cards(self.unit_deck, self.unit_hand, num=3)

    def point_in_rect(self, x, y, rect):
        left = rect['center_x'] - rect['width'] / 2
        right = rect['center_x'] + rect['width'] / 2
        bottom = rect['center_y'] - rect['height'] / 2
        top = rect['center_y'] + rect['height'] / 2
        return left <= x <= right and bottom <= y <= top

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

        unit.start_move(path)
        self.current_action_points -= 1
        final_row, final_col = path[-1]
        print(
            f"{unit.unit_type} moved to ({final_row}, {final_col}). AP left: {self.current_action_points}"
        )
        return True

    def attack_unit(self, attacker, target):
        if target.health <= 0:
            return
        target.health -= attacker.attack
        print(
            f"{attacker.unit_type} attacked {target.unit_type} for {attacker.attack} damage. Target health: {target.health}"
        )
        # Knock back one square if possible
        dr = target.row - attacker.row
        dc = target.col - attacker.col
        knock_row = target.row + (1 if dr > 0 else -1 if dr < 0 else 0)
        knock_col = target.col + (1 if dc > 0 else -1 if dc < 0 else 0)
        if 0 <= knock_row < ROWS and 0 <= knock_col < COLUMNS:
            if not any(u.row == knock_row and u.col == knock_col for u in self.units):
                target.start_move([(knock_row, knock_col)])

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
        for target in self.attack_targets:
            x = target.col * CELL_SIZE + CELL_SIZE / 2
            y = target.row * CELL_SIZE + CELL_SIZE / 2
            rect = arcade.Rect(
                left=x - CELL_SIZE / 2,
                right=x + CELL_SIZE / 2,
                bottom=y - CELL_SIZE / 2,
                top=y + CELL_SIZE / 2,
                x=x,
                y=y,
                width=CELL_SIZE,
                height=CELL_SIZE,
            )
            arcade.draw_rect_filled(rect, arcade.color.DARK_RED)
        for unit in self.units:
            unit.draw()
        panel_x = GRID_WIDTH + UI_PANEL_WIDTH / 2

        arcade.draw_lbwh_rectangle_filled(
            GRID_WIDTH,
            0,
            UI_PANEL_WIDTH,
            SCREEN_HEIGHT,
            arcade.color.DARK_SLATE_GRAY,
        )
        arcade.draw_text(f"Player {self.current_player} - AP: {self.current_action_points}", GRID_WIDTH + 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 14)
        # Draw buttons

        arcade.draw_lbwh_rectangle_filled(

            self.end_turn_button['center_x'] - self.end_turn_button['width'] / 2,
            self.end_turn_button['center_y'] - self.end_turn_button['height'] / 2,
            self.end_turn_button['width'],
            self.end_turn_button['height'],
            arcade.color.GRAY,
        )
        arcade.draw_text(
            "End Turn",
            self.end_turn_button['center_x'],
            self.end_turn_button['center_y'],
            arcade.color.WHITE,
            12,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_lbwh_rectangle_filled(
            self.draw_card_button['center_x'] - self.draw_card_button['width'] / 2,
            self.draw_card_button['center_y'] - self.draw_card_button['height'] / 2,
            self.draw_card_button['width'],
            self.draw_card_button['height'],
            arcade.color.GRAY,
        )
        arcade.draw_text(
            "Draw Spell",
            self.draw_card_button['center_x'],
            self.draw_card_button['center_y'],
            arcade.color.WHITE,
            12,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_lbwh_rectangle_filled(
            self.draw_unit_button['center_x'] - self.draw_unit_button['width'] / 2,
            self.draw_unit_button['center_y'] - self.draw_unit_button['height'] / 2,
            self.draw_unit_button['width'],
            self.draw_unit_button['height'],
            arcade.color.GRAY,
        )
        arcade.draw_text(
            "Draw Unit",
            self.draw_unit_button['center_x'],
            self.draw_unit_button['center_y'],
            arcade.color.WHITE,
            12,
            anchor_x="center",
            anchor_y="center",
        )

        # Draw spell hand
        y_pos = SCREEN_HEIGHT - 100
        arcade.draw_text("Spell Hand:", GRID_WIDTH + 10, y_pos + 20, arcade.color.WHITE, 12)
        self.card_rects = []
        for idx, card in enumerate(self.spell_hand):
            rect = {
                'center_x': panel_x,
                'center_y': y_pos - idx * 30,
                'width': UI_PANEL_WIDTH - 20,
                'height': 24,
            }
            color = arcade.color.LIGHT_GREEN if idx == self.selected_card_index else arcade.color.DARK_SLATE_GRAY

            arcade.draw_lbwh_rectangle_filled(
                rect['center_x'] - rect['width'] / 2,
                rect['center_y'] - rect['height'] / 2,
                rect['width'],
                rect['height'],
                color,
            )
            text_x = rect['center_x'] - rect['width'] / 2 + 5
            text_y = rect['center_y'] - 8
            arcade.draw_text(
                f"{idx}: {card.name} (Cost: {card.cost})",
                text_x,
                text_y,
                arcade.color.WHITE,
                12,
            )
            self.card_rects.append(rect)

        # Draw unit hand
        unit_y = y_pos - len(self.spell_hand) * 30 - 60
        arcade.draw_text("Unit Hand:", GRID_WIDTH + 10, unit_y + 20, arcade.color.WHITE, 12)
        self.unit_card_rects = []
        for idx, unit_cls in enumerate(self.unit_hand):
            rect = {
                'center_x': panel_x,
                'center_y': unit_y - idx * 30,
                'width': UI_PANEL_WIDTH - 20,
                'height': 24,
            }
            arcade.draw_lbwh_rectangle_filled(
                rect['center_x'] - rect['width'] / 2,
                rect['center_y'] - rect['height'] / 2,
                rect['width'],
                rect['height'],
                arcade.color.DARK_SLATE_GRAY,
            )
            text_x = rect['center_x'] - rect['width'] / 2 + 5
            text_y = rect['center_y'] - 8
            arcade.draw_text(
                unit_cls.__name__,
                text_x,
                text_y,
                arcade.color.WHITE,
                12,
            )
            self.unit_card_rects.append(rect)

    def on_mouse_press(self, x, y, button, modifiers):
        print(f"Mouse pressed at ({x}, {y})")
        # Click within UI panel
        if x >= GRID_WIDTH:
            if self.point_in_rect(x, y, self.end_turn_button):
                self.end_turn()
                return
            if self.point_in_rect(x, y, self.draw_card_button):
                self.draw_cards(self.spell_deck, self.spell_hand, num=1)
                return
            if self.point_in_rect(x, y, self.draw_unit_button):
                self.draw_cards(self.unit_deck, self.unit_hand, num=1)
                return
            for idx, rect in enumerate(self.card_rects):
                if self.point_in_rect(x, y, rect):
                    self.selected_card_index = idx
                    print(f"Selected card: {self.spell_hand[idx].name}")
                    return
            return

        cell = self.get_clicked_cell(x, y)
        if cell:
            row, col = cell
            print(f"Clicked on cell: ({row}, {col})")

            # If a card is selected, play it on this target
            if self.selected_card_index is not None and self.selected_card_index < len(self.spell_hand):
                target_unit = None
                for unit in self.units:
                    if unit.row == row and unit.col == col:
                        target_unit = unit
                        break
                target = target_unit if target_unit else (row, col)
                card = self.spell_hand[self.selected_card_index]
                self.play_card(card, target)
                self.selected_card_index = None
                return

            for unit in self.units:
                if unit.row == row and unit.col == col:
                    if unit.owner == self.current_player:
                        self.selected_unit = unit
                        self.move_squares = self.get_valid_move_squares(unit)
                        self.attack_targets = self.get_attackable_units(unit)
                        print(
                            f"Selected unit: {unit.unit_type} (Owner: {unit.owner})"
                        )
                        return
                    elif (
                        self.selected_unit
                        and unit in self.attack_targets
                        and self.selected_unit.owner == self.current_player
                    ):
                        self.attack_unit(self.selected_unit, unit)
                        self.attack_targets = []
                        self.move_squares = []
                        self.selected_unit = None
                        return
            if self.selected_unit and (row, col) in self.move_squares:
                self.move_unit(self.selected_unit, row, col)
                self.attack_targets = self.get_attackable_units(self.selected_unit)
                self.move_squares = []
                return
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

    def on_update(self, delta_time):
        for unit in self.units:
            if unit.frozen_turns > 0:
                unit.frozen_turns -= 1
            unit.update_animation(delta_time)
        if self.player1BlockedTurnsTimer > 0:
            self.player1BlockedTurnsTimer -= 1
        if self.player2BlockedTurnsTimer > 0:
            self.player2BlockedTurnsTimer -= 1
        self.units = [u for u in self.units if u.health > 0]


def main():
    window = GridsGame()
    arcade.run()
