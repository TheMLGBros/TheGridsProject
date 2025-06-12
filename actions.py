from enum import IntEnum

class ActionType(IntEnum):
    """Enumeration of possible action types in the environment."""
    MOVE = 0
    DEPLOY = 1
    PLAY_CARD = 2
    END_TURN = 3
    ATTACK = 4
    DRAW_SPELL = 5
    DRAW_UNIT = 6
