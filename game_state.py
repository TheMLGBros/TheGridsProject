# Game state logic for grids environment
import heapq
from collections import deque
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
        self.fires = {}

        # None while the game is ongoing, otherwise set to the winning player's
        # number (1 or 2).
        self.winner = None

        # stateful selections used by some cards
        self.selected_unit = None

        # each player gets their own identical decks to ensure fairness
        unit_types = [Warrior, Archer, Healer, Trebuchet, Viking]
        # Temporarily exclude Teleport to simplify the learning task
        spell_types = [Fireball, Freeze, StrengthUp, MeteoriteStrike, ActionBlock]
        self.unit_decks = {1: [], 2: []}
        self.spell_decks = {1: [], 2: []}
        for player in (1, 2):
            for _ in range(2):  # two copies of each card/unit
                self.unit_decks[player].extend(unit_types)
                self.spell_decks[player].extend(card() for card in spell_types)
            random.shuffle(self.unit_decks[player])
            random.shuffle(self.spell_decks[player])

        # each player maintains separate hands for units and spells
        self.hands = {1: [], 2: []}
        self.unit_hands = {1: [], 2: []}
        self.spell_hands = {1: [], 2: []}

        self.init_board()
        # give each player an initial hand of three spell and three unit cards
        for player in (1, 2):
            self.draw_cards(self.spell_decks[player], player, num=3)
            self.draw_cards(self.unit_decks[player], player, num=3)

        # convenience references for the current player
        self.refresh_player_hands()

    # ------------------------------------------------------------------
    def check_winner(self):
        """Update the winner attribute based on remaining commanders."""
        p1_alive = any(
            u.unit_type == "Commander" and u.owner == 1 for u in self.units
        )
        p2_alive = any(
            u.unit_type == "Commander" and u.owner == 2 for u in self.units
        )
        if not p1_alive and not p2_alive:
            self.winner = None
        elif not p1_alive:
            self.winner = 2
        elif not p2_alive:
            self.winner = 1
        else:
            self.winner = None

    def remove_dead_units(self):
        """Remove units with no health and check for a winner."""
        self.units[:] = [u for u in self.units if u.health > 0]
        self.check_winner()

    def refresh_player_hands(self):
        """Update convenience references for the current player."""
        self.hand = self.hands[self.current_player]
        self.unit_hand = self.unit_hands[self.current_player]
        self.spell_hand = self.spell_hands[self.current_player]

    # expose the current player's decks for compatibility with older code
    @property
    def unit_deck(self):
        return self.unit_decks[self.current_player]

    @property
    def spell_deck(self):
        return self.spell_decks[self.current_player]

    def init_board(self):
        # start with only the two commanders on the board
        self.units.append(
            Unit(
                ROWS // 2,
                0,
                "Commander",
                owner=1,
                health=150,
                attack=20,
                move_range=2,
                attack_range=1,
                cost=1,
            )
        )
        self.units.append(
            Unit(
                ROWS // 2,
                COLUMNS - 1,
                "Commander",
                owner=2,
                health=150,
                attack=20,
                move_range=2,
                attack_range=1,
                cost=1,
            )
        )

    def draw_cards(self, deck, player, num=1, ap_cost=0):
        """Draw cards from ``deck`` into ``player``'s hand.

        Returns ``True`` if at least one card was drawn. ``ap_cost`` represents
        the action point cost per card and will be subtracted when a card is
        successfully drawn.
        """
        drawn = False
        hand = self.hands[player]
        for _ in range(num):
            if deck and len(hand) < HAND_CAPACITY:
                if ap_cost and self.current_action_points < ap_cost:
                    break
                card = deck.pop(0)
                hand.append(card)
                if isinstance(card, Card):
                    self.spell_hands[player].append(card)
                elif isinstance(card, type) and issubclass(card, Unit):
                    self.unit_hands[player].append(card)
                if ap_cost:
                    self.current_action_points -= ap_cost
                drawn = True
        return drawn

    def get_valid_deploy_squares(self, player=None):
        """Return free squares on the deployment column for the player."""
        if player is None:
            player = self.current_player
        col = 0 if player == 1 else COLUMNS - 1
        valid = []
        for row in range(ROWS):
            if not any(u.row == row and u.col == col for u in self.units):
                valid.append((row, col))
        return valid

    def place_unit(self, unit_cls, row, col):
        """Deploy a unit from the player's hand onto the board."""
        player = self.current_player
        if unit_cls not in self.unit_hands[player]:
            return None
        if (player == 1 and col != 0) or (player == 2 and col != COLUMNS - 1):
            return None
        if any(u.row == row and u.col == col for u in self.units):
            return None
        unit = unit_cls(row, col, owner=player)
        cost = getattr(unit, "deploy_cost", 1)
        if self.current_action_points < cost:
            return None
        self.unit_hands[player].remove(unit_cls)
        if unit_cls in self.hands[player]:
            self.hands[player].remove(unit_cls)
        self.units.append(unit)
        self.current_action_points -= cost
        self.refresh_player_hands()
        return unit

    # ---------- Core game mechanics ----------
    def move_unit(self, unit, target_row, target_col, animate=False):
        if unit.frozen_turns > 0:
            return False
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
        if attacker.frozen_turns > 0:
            return False

        if attacker.unit_type == "Trebuchet" and attacker.has_attacked:
            return False


        if target in attacker.attacked_targets:
            return False

        if attacker.unit_type == "Healer":
            if attacker.owner == target.owner:
                # Heal friendly target up to its maximum health
                target.health = min(target.health + attacker.attack, target.max_health)
                print(
                    f"{attacker.unit_type} heals {target.unit_type}! {target.unit_type} health is now {target.health}."
                )
                return True
            else:
                # Healers cannot damage enemies
                return False
              
        if target.health <= 0:
            return
        dist = self.manhattan_distance((attacker.row, attacker.col), (target.row, target.col))
        damage = attacker.attack
        if attacker.unit_type == "Trebuchet" and dist == 1:
            damage = attacker.attack // 2
        target.health -= damage
        print(
            f"{attacker.unit_type} attacks {target.unit_type}! {target.unit_type} health is now {target.health}."
        )
        if target.health <= 0:
            # remove defeated unit immediately so its cell becomes free and
            # check if the game has been won.
            self.remove_dead_units()
            # remove defeated unit immediately so its cell becomes free
            self.units[:] = [u for u in self.units if u is not target]
            attacker.has_attacked = True
            attacker.attacked_targets.add(target)
            return True

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
                    # knockback.
                    target.pixel_x = knock_col * CELL_SIZE + CELL_SIZE / 2
                    target.pixel_y = knock_row * CELL_SIZE + CELL_SIZE / 2
                    target.target_pixel_x = target.pixel_x
                    target.target_pixel_y = target.pixel_y
                    target.move_queue = []
        attacker.has_attacked = True
        attacker.attacked_targets.add(target)
        return True

    def end_turn(self):
        # apply status effects at the end of each turn before switching players
        self.process_turn_effects()
        for unit in self.units:
            unit.has_attacked = False
            unit.attacked_targets.clear()
        self.current_player = 2 if self.current_player == 1 else 1
        if self.current_player == 1 and self.player1BlockedTurnsTimer > 0:
            self.player1BlockedTurnsTimer -= 1
            self.current_action_points = 4
        elif self.current_player == 2 and self.player2BlockedTurnsTimer > 0:
            self.player2BlockedTurnsTimer -= 1
            self.current_action_points = 4
        else:
            self.current_action_points = 7
        # card drawing is now an explicit action rather than automatic
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
        # cards may defeat units (including commanders)
        self.remove_dead_units()
        self.refresh_player_hands()
        return True

    # ---------- Helpers ----------
    def get_valid_move_squares(self, unit):
        """Return all squares the given ``unit`` can reach this turn."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([(unit.row, unit.col, 0)])
        visited = {(unit.row, unit.col)}
        valid_moves = []

        while queue:
            row, col, dist = queue.popleft()
            if dist >= unit.move_range:
                continue
            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                if not (0 <= nr < ROWS and 0 <= nc < COLUMNS):
                    continue
                if (nr, nc) in visited:
                    continue
                if any(u.row == nr and u.col == nc for u in self.units):
                    continue
                visited.add((nr, nc))
                valid_moves.append((nr, nc))
                queue.append((nr, nc, dist + 1))

        return valid_moves

    def get_attackable_units(self, unit):
        if unit.unit_type == "Trebuchet" and unit.has_attacked:
            return []
        targets = []
        for other in self.units:
            if unit.unit_type == "Healer":
                if (
                    other.owner == unit.owner
                    and other is not unit
                    and other not in unit.attacked_targets
                ):
                    dist = self.manhattan_distance((unit.row, unit.col), (other.row, other.col))
                    if dist <= unit.attack_range:
                        targets.append(other)
            else:
                if (
                    other.owner != unit.owner
                    and other not in unit.attacked_targets
                ):
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

    def process_turn_effects(self):
        for unit in self.units:
            if unit.frozen_turns > 0:
                unit.frozen_turns -= 1
            if unit.burn_turns > 0:
                unit.health -= 10
                unit.burn_turns -= 1
            if (unit.row, unit.col) in self.fires:
                unit.health -= 15
        # decrement fire durations and clean up
        expired = []
        for pos in list(self.fires.keys()):
            self.fires[pos] -= 1
            if self.fires[pos] <= 0:
                expired.append(pos)
        for pos in expired:
            del self.fires[pos]
        # modify the list in-place so external references remain valid
        self.remove_dead_units()
