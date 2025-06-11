class Window:
    def __init__(self, *args, **kwargs):
        pass
    def clear(self, *args, **kwargs):
        pass

class Sprite:
    def __init__(self, *args, **kwargs):
        self.center_x = 0
        self.center_y = 0
        self.color = None

def draw_sprite(sprite):
    pass

def draw_rect_outline(*args, **kwargs):
    pass

def draw_rect_filled(*args, **kwargs):
    pass

def draw_lbwh_rectangle_filled(*args, **kwargs):
    pass

def draw_text(*args, **kwargs):
    pass

class Rect:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class color:
    LIGHT_GRAY = DARK_GRAY = LIGHT_BLUE = DARK_RED = GRAY = WHITE = DARK_SLATE_GRAY = BLUE = RED = LIGHT_GREEN = 0
