class Window:
    def __init__(self, *args, **kwargs):
        pass

class Sprite:
    def __init__(self, *args, **kwargs):
        self.center_x = 0
        self.center_y = 0
        self.color = None
    def draw(self):
        pass

class color:
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (211, 211, 211)
    DARK_GRAY = (169, 169, 169)
    LIGHT_BLUE = (173, 216, 230)
    DARK_SPRING_GREEN = (23, 114, 69)
    ORANGE = (255, 165, 0)
    DARK_RED = (139, 0, 0)
    DARK_SLATE_GRAY = (47, 79, 79)
    GRAY = (128, 128, 128)
    LIGHT_GREEN = (144, 238, 144)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
