import arcade
import random
import heapq

# -------------------------
# Constants and Configurations
# -------------------------
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Grids Prototype"

ROWS = 7
COLUMNS = 10
CELL_SIZE = 64
GRID_WIDTH = COLUMNS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
UI_PANEL_WIDTH = SCREEN_WIDTH - GRID_WIDTH

# -------------------------
# Base Classes for Game Entities
# -------------------------
class GameEntity:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def draw(self):
        pass

# -------------------------
# Unit Classes
# -------------------------
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
        # Different colors based on owner
        color = arcade.color.BLUE if self.owner == 1 else arcade.color.RED
        # Center coordinates for the unit's cell
        x = self.col * CELL_SIZE + CELL_SIZE / 2
        y = self.row * CELL_SIZE + CELL_SIZE / 2
        # For simplicity, draw a circle representing the unit
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

# Unit Subclasses
class Warrior(Unit):
    def __init__(self, row, col, owner):
        # Example stats; adjust as needed
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

# -------------------------
# Card Classes
# -------------------------
class Card:
    def __init__(self, name, cost, description):
        self.name = name
        self.cost = cost
        self.description = description
      
    def play(self, game, target):
        """Override this method in subclasses to implement card effects."""
        raise NotImplementedError

class Fireball(Card):
    def __init__(self):
        super().__init__("Fireball", cost=1, description="Creates a lingering fire effect lasting 4 turns, burned targets take 10 between turns, 15 when standing in the fire.")
    
    def play(self, game, target):
        # For demonstration: if target is a Unit, reduce its health.
        if isinstance(target, Unit):
            target.health -= 3
            print(f"{target.unit_type} hit by Fireball! New health: {target.health}")
        else:
            print("Fireball played on grid cell", target)

        # Additional lingering effects can be implemented here.

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
            target.attack += 10  # This boost is temporary; you can add logic to revert it at turn end.
            print(f"{target.unit_type}'s attack increased to {target.attack}.")

class MeteoriteStrike(Card):
    def __init__(self):
        super().__init__("Meteorite Strike", cost=2, description="Deals 40 damage to a target square and knocks back adjacent units.")
    
    def play(self, game, target):
        # Assume target is a tuple: (row, col)
        print("Meteorite Strike at", target)
        for unit in game.units:
            if unit.row == target[0] and unit.col == target[1]:
                unit.health -= 40
                print(f"{unit.unit_type} took damage from Meteorite Strike, health is now {unit.health}.")
        # Knockback logic can be added here.
        

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


# -------------------------
# Main Game Class
# -------------------------
class GridsGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.grid_origin_x = 0
        self.grid_origin_y = 0

        # Game state lists
        self.units = []         # List of Unit objects
        self.obstacles = []     # List of obstacles (not fully implemented here)
        
        # Turn-based system
        self.current_action_points = 7
        self.current_player = 1  # 1 or 2
        self.player1BlockedTurnsTimer = 0
        self.player2BlockedTurnsTimer = 0

        # Card decks and hands (spell cards for this prototype)
        self.unit_deck = []   # Can be populated later
        self.spell_deck = [Fireball(), Freeze(), StrengthUp(), MeteoriteStrike(), ActionBlock()]
        self.unit_hand = []
        self.spell_hand = []

        # For UI selection
        self.selected_unit = None
        self.move_squares = []

        self.init_board()
        # Draw initial spell hand (for example, draw 3 cards)
        self.draw_cards(self.spell_deck, self.spell_hand, num=3)

    def init_board(self):
        # Place obstacles in the middle of the board (if any) – skipped for brevity

        # Deploy initial units:
        # For prototype purposes, deploy commanders in the deployment zones:
        # Player 1's commander on the left; Player 2's commander on the right.
        self.units.append(Unit(ROWS // 2, 0, "Commander", owner=1, health=300, attack=20, move_range=2, attack_range=1,cost=1))
        self.units.append(Unit(ROWS // 2, COLUMNS - 1, "Commander", owner=2, health=20, attack=3, move_range=2, attack_range=1,cost=1))

        # For demonstration, we'll add a few unit instances for player 1 on the left deployment zone.
        self.units.append(Warrior(ROWS // 2, 1, owner=1))
        self.units.append(Archer(ROWS // 2 - 1, 0, owner=1))
        self.units.append(Healer(ROWS // 2 + 1, 0, owner=1))
        # And add a couple for player 2 on the right deployment zone.
        self.units.append(Viking(ROWS // 2 + 1, COLUMNS - 1, owner=2))
        self.units.append(Trebuchet(ROWS // 2 - 1, COLUMNS - 1, owner=2))

    def draw_cards(self, deck, hand, num=1):
        for _ in range(num):
            if deck:
                card = deck.pop(0)
                hand.append(card)

    def move_unit(self, unit, target_row, target_col):
        """
        Moves the unit step by step along the shortest path to the target cell.
        """
        path = self.a_star_pathfinding((unit.row, unit.col), (target_row, target_col))
        if not path or len(path) > unit.move_range:
            print("Move not possible!")
            return False

        # Move the unit step by step along the path
        for step in path:
            unit.row, unit.col = step
            #self.current_action_points -= 1
            #if self.current_action_points <= 0:
            #    break  # Stop moving if out of AP

        self.current_action_points -= 1
        
        print(f"{unit.unit_type} moved to ({unit.row}, {unit.col}). AP left: {self.current_action_points}")
        return True


    def end_turn(self):
        print(f"Ending turn for Player {self.current_player}.")
        # Reset action points.
        self.current_action_points = 7
        # Switch current player.
        self.current_player = 2 if self.current_player == 1 else 1
        # Draw a card at the start of turn (for spells).
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
        # Use clear() as we are in a game loop.
        arcade.Window.clear(self)

        # Draw grid cells.
        for row in range(ROWS):
            for col in range(COLUMNS):
                x = col * CELL_SIZE + CELL_SIZE / 2
                y = row * CELL_SIZE + CELL_SIZE / 2
                # Deployment zones on left and right
                if col == 0 or col == COLUMNS - 1:
                    color = arcade.color.LIGHT_GRAY
                else:
                    color = arcade.color.DARK_GRAY


                # Highlight valid move squares (semi-transparent)
                if (row, col) in self.move_squares:
                    color = arcade.color.LIGHT_BLUE  # Adding transparency
                # Create a rectangle for the cell.
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

        # Draw units.
        for unit in self.units:
            unit.draw()

        # Draw UI panel on the right.
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

        # Display the spell hand.
        y_pos = SCREEN_HEIGHT - 60
        arcade.draw_text("Spell Hand:", GRID_WIDTH + 10, y_pos, arcade.color.WHITE, 12)
        y_pos -= 20
        for idx, card in enumerate(self.spell_hand):
            arcade.draw_text(f"{idx}: {card.name} (Cost: {card.cost})", GRID_WIDTH + 10, y_pos - idx * 20, arcade.color.WHITE, 12)


    def on_mouse_press(self, x, y, button, modifiers):
        # This method is simplified; you would normally add logic to:

        # - Select a unit (if clicking on a cell with a unit).
        # - Command a selected unit to move.
        # - Or select and play a card from the UI.
        print(f"Mouse pressed at ({x}, {y})")
        # For example, you could check if the click is within the grid,
        # then decide whether to move a unit or interact with the UI.
        # (Left as an exercise for further development.)

        cell = self.get_clicked_cell(x, y)
    
        if cell:
            row, col = cell
            print(f"Clicked on cell: ({row}, {col})")

            # Check if a unit is in the clicked cell
            for unit in self.units:
                if unit.row == row and unit.col == col and unit.owner == self.current_player:
                    self.selected_unit = unit
                    self.move_squares = self.get_valid_move_squares(unit)  # Update move squares
                    print(f"Selected unit: {unit.unit_type} (Owner: {unit.owner})")
                    return
            
            # If clicking on a move square, move the unit
            if self.selected_unit and (row, col) in self.move_squares:
                self.move_unit(self.selected_unit, row, col)
                self.move_squares = []  # Clear move highlights after moving
                self.selected_unit = None  # Deselect unit

        # If clicking outside grid (e.g., on UI), clear selections
        else:
            self.selected_unit = None
            self.move_squares = []
        #ui clicks goes here ...


    def get_clicked_cell(self, x, y):
        """
        Given the x, y coordinates of a mouse click, return the grid cell (row, col).
        Returns None if the click is outside the grid.
        """
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return None  # Click was outside the grid

        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)

        return row, col  # Return the row and column as a tuple

    def get_valid_move_squares(self, unit):
        """
        Returns a list of valid move squares for the unit based on A* pathfinding.
        """
        valid_moves = []
        
        for row in range(ROWS):
            for col in range(COLUMNS):
                if (row, col) == (unit.row, unit.col):  # Skip the unit's own position
                    continue
                path = self.a_star_pathfinding((unit.row, unit.col), (row, col))
                if path and len(path) <= unit.move_range:  # Ensure within move range
                    valid_moves.append((row, col))
        
        return valid_moves

    def a_star_pathfinding(self, start, goal):
        """
        Uses A* algorithm to find the shortest path from start (row, col) to goal (row, col).
        Returns a list of (row, col) steps to reach the goal or an empty list if unreachable.
        """
        # Directions for movement (Up, Down, Left, Right)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Priority queue for A*
        open_list = []
        heapq.heappush(open_list, (0, start))  # (F-cost, (row, col))
        
        came_from = {}  # To reconstruct the path
        g_score = {start: 0}
        f_score = {start: self.manhattan_distance(start, goal)}

        while open_list:
            _, current = heapq.heappop(open_list)

            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()  # We built the path backwards
                return path  # Return valid path

            # Explore neighbors
            for dr, dc in directions:
                neighbor = (current[0] + dr, current[1] + dc)
                if not (0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLUMNS):
                    continue  # Skip out-of-bounds cells
                if any(unit.row == neighbor[0] and unit.col == neighbor[1] for unit in self.units):
                    continue  # Skip cells occupied by units
                
                tentative_g_score = g_score[current] + 1  # Cost of moving to a neighbor
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.manhattan_distance(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))
        
        return []  # No path found

    def manhattan_distance(self, cell1, cell2):
        """
        Computes the Manhattan distance between two cells.
        """
        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])


    def update(self, delta_time):
        # Here you would update timers (e.g., frozen_turns decrement) and other game logic.
        for unit in self.units:
            if unit.frozen_turns > 0:
                unit.frozen_turns -= 1
        
        if self.player1BlockedTurnsTimer > 0:
            self.player1BlockedTurnsTimer -= 1

        if self.player2BlockedTurnsTimer > 0:
            self.player2BlockedTurnsTimer -= 1
        


# -------------------------
# Main Execution
# -------------------------
def main():
    window = GridsGame()
    arcade.run()

if __name__ == "__main__":
    main()
