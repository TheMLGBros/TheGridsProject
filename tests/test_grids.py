import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch
import arcade
from grids import GridsGame, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, ROWS, COLUMNS

@pytest.fixture
def game():
    with patch('arcade.Window.__init__', return_value=None):
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
