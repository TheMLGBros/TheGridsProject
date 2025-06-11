import arcade
from game_state import GameState

from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, ROWS, COLUMNS,
                       CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, UI_PANEL_WIDTH)
from units import (Unit, Warrior, Archer, Healer, Trebuchet, Viking)
from cards import (
    Card,
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

        # game state containing units and rules
        self.state = GameState()

        # convenience references used by UI code
        self.unit_deck = self.state.unit_deck
        self.spell_deck = self.state.spell_deck
        self.hand = self.state.hand
        self.unit_hand = self.state.unit_hand
        self.spell_hand = self.state.spell_hand
        self.player1BlockedTurnsTimer = self.state.player1BlockedTurnsTimer
        self.player2BlockedTurnsTimer = self.state.player2BlockedTurnsTimer
        self.current_action_points = self.state.current_action_points
        self.current_player = self.state.current_player
        self.sync_hands()

        self.units = self.state.units
        self.obstacles = self.state.obstacles

        self.selected_card_index = None
        self.move_squares = []
        self.attack_targets = []
        self.deploy_squares = []
        self.selected_unit_class = None

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

    def sync_hands(self):
        """Refresh hand references from the underlying game state."""
        self.hand = self.state.hand
        self.unit_hand = self.state.unit_hand
        self.spell_hand = self.state.spell_hand

    # expose selected_unit through the underlying game state
    @property
    def selected_unit(self):
        return self.state.selected_unit

    @selected_unit.setter
    def selected_unit(self, value):
        self.state.selected_unit = value

    def point_in_rect(self, x, y, rect):
        left = rect['center_x'] - rect['width'] / 2
        right = rect['center_x'] + rect['width'] / 2
        bottom = rect['center_y'] - rect['height'] / 2
        top = rect['center_y'] + rect['height'] / 2
        return left <= x <= right and bottom <= y <= top

    def init_board(self):
        self.state.init_board()

    def draw_cards(self, deck, player, num=1, ap_cost=0):
        self.state.draw_cards(deck, player, num, ap_cost=ap_cost)
        self.current_action_points = self.state.current_action_points
        self.sync_hands()

    def move_unit(self, unit, target_row, target_col):
        result = self.state.move_unit(unit, target_row, target_col, animate=True)
        self.current_action_points = self.state.current_action_points
        return result

    def attack_unit(self, attacker, target):
        self.state.attack_unit(attacker, target)

    def end_turn(self):
        self.state.end_turn()
        self.current_action_points = self.state.current_action_points
        self.current_player = self.state.current_player
        self.sync_hands()

    def play_card(self, card, target):
        result = self.state.play_card(card, target)
        self.current_action_points = self.state.current_action_points
        self.sync_hands()
        return result

    def get_valid_deploy_squares(self):
        return self.state.get_valid_deploy_squares()

    def place_unit(self, unit_cls, row, col):
        unit = self.state.place_unit(unit_cls, row, col)
        self.current_action_points = self.state.current_action_points
        self.units = self.state.units
        if unit:
            print(f"Deployed {unit.unit_type} at ({row}, {col})")
        self.sync_hands()
        return unit

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
                if (row, col) in self.deploy_squares:
                    color = arcade.color.DARK_SPRING_GREEN
                if (row, col) in self.state.fires:
                    color = arcade.color.ORANGE
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
                if (
                    (row, col) in self.move_squares
                    or (row, col) in self.deploy_squares
                    or (row, col) in self.state.fires
                ):
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

        # Draw combined hand for current player
        y_pos = SCREEN_HEIGHT - 100
        arcade.draw_text("Hand:", GRID_WIDTH + 10, y_pos + 20, arcade.color.WHITE, 12)
        self.card_rects = []
        for idx, item in enumerate(self.hand):
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
            if isinstance(item, Card):
                label = f"{idx}: {item.name} (Cost: {item.cost})"
            else:
                label = item.__name__
            arcade.draw_text(
                label,
                text_x,
                text_y,
                arcade.color.WHITE,
                12,
            )
            self.card_rects.append(rect)

    def on_mouse_press(self, x, y, button, modifiers):
        print(f"Mouse pressed at ({x}, {y})")
        # Click within UI panel
        if x >= GRID_WIDTH:
            if self.point_in_rect(x, y, self.end_turn_button):
                self.end_turn()
                return
            if self.point_in_rect(x, y, self.draw_card_button):
                self.draw_cards(self.spell_deck, self.current_player, num=1, ap_cost=1)
                return
            if self.point_in_rect(x, y, self.draw_unit_button):
                self.draw_cards(self.unit_deck, self.current_player, num=1, ap_cost=1)
                return
            for idx, rect in enumerate(self.card_rects):
                if self.point_in_rect(x, y, rect):
                    self.selected_card_index = idx
                    item = self.hand[idx]
                    if isinstance(item, Card):
                        print(f"Selected card: {item.name}")
                        self.deploy_squares = []
                        self.selected_unit_class = None
                    else:
                        print(f"Selected unit: {item.__name__}")
                        self.selected_unit_class = item
                        self.deploy_squares = self.get_valid_deploy_squares()
                    return
            return

        cell = self.get_clicked_cell(x, y)
        if cell:
            row, col = cell
            print(f"Clicked on cell: ({row}, {col})")

            # If a card is selected, play or deploy it on this target
            if self.selected_card_index is not None and self.selected_card_index < len(self.hand):
                selected = self.hand[self.selected_card_index]
                if isinstance(selected, Card):
                    target_unit = None
                    for unit in self.units:
                        if unit.row == row and unit.col == col:
                            target_unit = unit
                            break
                    target = target_unit if target_unit else (row, col)
                    self.play_card(selected, target)
                    self.selected_card_index = None
                    return
                elif isinstance(selected, type) and issubclass(selected, Unit):
                    if (row, col) in self.deploy_squares:
                        self.place_unit(selected, row, col)
                        self.selected_card_index = None
                        self.deploy_squares = []
                        self.selected_unit_class = None
                    return

            for unit in self.units:
                if unit.row == row and unit.col == col:
                    if unit.owner == self.current_player:
                        self.selected_unit = unit
                        self.move_squares = self.get_valid_move_squares(unit)
                        self.attack_targets = self.get_attackable_units(unit)
                        print("Selected unit:", unit.describe())
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
            self.deploy_squares = []
            self.selected_unit_class = None
            
    def get_clicked_cell(self, x, y):
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return None
        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)
        return row, col

    def get_valid_move_squares(self, unit):
        return self.state.get_valid_move_squares(unit)

    def get_attackable_units(self, unit):
        return self.state.get_attackable_units(unit)

    def a_star_pathfinding(self, start, goal):
        return self.state.a_star_pathfinding(start, goal)

    def manhattan_distance(self, cell1, cell2):
        return self.state.manhattan_distance(cell1, cell2)

    def on_update(self, delta_time):
        for unit in self.state.units:
            unit.update_animation(delta_time)
        self.player1BlockedTurnsTimer = self.state.player1BlockedTurnsTimer
        self.player2BlockedTurnsTimer = self.state.player2BlockedTurnsTimer
        self.current_action_points = self.state.current_action_points
        self.current_player = self.state.current_player
        self.sync_hands()

def main():
    window = GridsGame()
    arcade.run()
