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
        """Draw the entity using basic shapes.

        Arcade 3.x removed the ``Sprite.draw`` method that earlier versions
        relied on. Instead of drawing the sprite directly we replicate the
        behaviour using :func:`arcade.draw_circle_filled` which works for the
        ``SpriteCircle`` objects used throughout the project.
        """
        radius = self.sprite.width / 2
        arcade.draw_circle_filled(
            self.sprite.center_x,
            self.sprite.center_y,
            radius,
            self.sprite.color,
        )
