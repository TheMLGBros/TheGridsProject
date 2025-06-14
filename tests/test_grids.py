import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch
import arcade
from grids import (
    GridsGame,
    CELL_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    ROWS,
    COLUMNS,
    Teleport,
)
from game_state import GameState
from units import Warrior, Healer, Trebuchet

@pytest.fixture
def game():
    with patch('arcade.Window.__init__', return_value=None), \
         patch('arcade.Sprite') as MockSprite:
        MockSprite.return_value.center_x = 0
        MockSprite.return_value.center_y = 0
        MockSprite.return_value.color = None
        g = GridsGame()
    return g

def test_get_clicked_cell_inside(game):
    # Choose coordinates well within the grid
    x = CELL_SIZE * 2 + 10
    y = CELL_SIZE * 3 + 5
    assert game.get_clicked_cell(x, y) == (3, 2)

def test_get_clicked_cell_outside(game):
    assert game.get_clicked_cell(-1, 10) is None
    assert game.get_clicked_cell(GRID_WIDTH, 10) is None
    assert game.get_clicked_cell(10, GRID_HEIGHT) is None

def test_manhattan_distance(game):
    assert game.manhattan_distance((0, 0), (1, 1)) == 2
    assert game.manhattan_distance((0, 0), (ROWS - 1, COLUMNS - 1)) == (ROWS - 1) + (COLUMNS - 1)


def test_teleport_spell(game):
    teleport = Teleport()
    game.spell_hand.append(teleport)
    unit = next(u for u in game.units if u.owner == game.current_player)
    game.selected_unit = unit
    dest = (0, COLUMNS - 2)
    assert all(not (u.row == dest[0] and u.col == dest[1]) for u in game.units)
    starting_ap = game.current_action_points
    game.play_card(teleport, dest)
    assert unit.row == dest[0] and unit.col == dest[1]
    assert game.current_action_points == starting_ap - teleport.cost


def test_draw_unit_button(game):
    initial = len(game.unit_hand)
    button = game.draw_unit_button
    ap_before = game.current_action_points
    game.on_mouse_press(button['center_x'], button['center_y'], 1, None)
    assert len(game.unit_hand) == initial + 1
    assert game.current_action_points == ap_before - 1


def test_move_unit_single_step(game):
    """Moving a unit one square should not raise an error."""
    unit = None
    dest = None
    for candidate in [u for u in game.units if u.owner == game.current_player]:
        neighbours = [
            (candidate.row, candidate.col + 1),
            (candidate.row, candidate.col - 1),
            (candidate.row + 1, candidate.col),
            (candidate.row - 1, candidate.col),
        ]
        for r, c in neighbours:
            if 0 <= r < ROWS and 0 <= c < COLUMNS and not any(
                other.row == r and other.col == c for other in game.units
            ):
                unit = candidate
                dest = (r, c)
                break
        if dest:
            break

    assert dest is not None, "No available unit with a free neighbouring cell"

    assert game.move_unit(unit, *dest)


def test_unit_removed_on_death():
    """Units reduced to zero health should be removed immediately."""
    state = GameState()
    state.units = []
    attacker = Warrior(0, 0, owner=1)
    target = Warrior(0, 1, owner=2)
    target.health = 10
    state.units = [attacker, target]
    state.attack_unit(attacker, target)
    assert target not in state.units


def test_unit_can_attack_multiple_targets_but_not_same_twice():
    state = GameState()
    state.units = []
    attacker = Warrior(0, 0, owner=1)
    target1 = Warrior(0, 1, owner=2)
    target2 = Warrior(0, 2, owner=2)
    state.units = [attacker, target1, target2]

    assert state.attack_unit(attacker, target1)
    assert state.attack_unit(attacker, target2)

    health_before = target1.health
    assert not state.attack_unit(attacker, target1)
    assert target1.health == health_before

    state.end_turn()
    state.end_turn()  # back to player 1
    assert state.attack_unit(attacker, target1)


def test_get_valid_deploy_squares(game):
    squares = game.get_valid_deploy_squares()
    for r, c in squares:
        assert c == 0
        assert all(not (u.row == r and u.col == c) for u in game.units)


def test_place_unit(game):
    squares = game.get_valid_deploy_squares()
    unit_cls = game.unit_hand[0]
    ap_before = game.current_action_points
    game.place_unit(unit_cls, *squares[0])
    assert any(u.row == squares[0][0] and u.col == squares[0][1] for u in game.units)
    assert len(game.unit_hand) == 2
    assert game.current_action_points == ap_before - 1


def test_healer_heals_friendly_and_not_enemy():
    state = GameState()
    state.units = []
    healer = Healer(0, 0, owner=1)
    ally = Warrior(0, 1, owner=1)
    enemy = Warrior(0, 2, owner=2)
    ally.health = 40
    state.units = [healer, ally, enemy]
    state.attack_unit(healer, ally)
    assert ally.health > 40
    assert ally.health <= ally.max_health
    prev = enemy.health
    state.attack_unit(healer, enemy)
    assert enemy.health == prev


def test_teleport_spell_no_selection(game):
    teleport = Teleport()
    game.spell_hand.append(teleport)
    dest = (0, COLUMNS - 2)
    assert all(
        not (u.row == dest[0] and u.col == dest[1]) for u in game.units
    )
    starting_ap = game.current_action_points
    # intentionally do not set game.selected_unit
    game.play_card(teleport, dest)
    assert any(
        u.owner == game.current_player and u.row == dest[0] and u.col == dest[1]
        for u in game.units
    )
    assert game.current_action_points == starting_ap - teleport.cost


def test_trebuchet_attacks_only_once_per_turn():
    state = GameState()
    state.units = []
    treb = Trebuchet(0, 0, owner=1)
    enemy1 = Warrior(0, 2, owner=2)
    enemy2 = Warrior(0, 3, owner=2)
    state.units = [treb, enemy1, enemy2]

    assert state.attack_unit(treb, enemy1)
    assert not state.attack_unit(treb, enemy2)

    state.end_turn()
    state.end_turn()

    assert state.attack_unit(treb, enemy2)


def test_trebuchet_adjacent_half_damage():
    state = GameState()
    state.units = []
    treb = Trebuchet(0, 0, owner=1)
    enemy = Warrior(0, 1, owner=2)
    state.units = [treb, enemy]
    before = enemy.health
    state.attack_unit(treb, enemy)
    assert before - enemy.health == treb.attack // 2
