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
    game.on_mouse_press(button['center_x'], button['center_y'], 1, None)
    assert len(game.unit_hand) == initial + 1
