import arcade

from constants import CELL_SIZE


class GameEntity:
    """Base class for anything placed on the grid."""

    def __init__(self, row: int, col: int, sprite: arcade.Sprite):
        self.row = row
        self.col = col

        self.sprite = sprite
        self.sprite.center_x = col * CELL_SIZE + CELL_SIZE / 2
        self.sprite.center_y = row * CELL_SIZE + CELL_SIZE / 2

    def draw(self):
        """Draw the entity using its sprite texture."""
        arcade.draw_sprite(self.sprite)
