class Window:
    def __init__(self, *args, **kwargs):
        pass

class Rect:
    def __init__(self, left=0, right=0, bottom=0, top=0, x=0, y=0, width=0, height=0):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class _Color:
    pass

color = _Color()
for name in [
    'DARK_SLATE_GRAY', 'WHITE', 'LIGHT_GRAY', 'DARK_GRAY',
    'LIGHT_BLUE', 'GRAY', 'LIGHT_GREEN', 'BLUE', 'RED']:
    setattr(color, name, (0, 0, 0))

def draw_rect_filled(*args, **kwargs):
    pass

def draw_rect_outline(*args, **kwargs):
    pass

def draw_circle_filled(*args, **kwargs):
    pass

def draw_text(*args, **kwargs):
    pass

# Provide alias for compatibility with older versions
# In real arcade, there is draw_rectangle_filled but in this stub we map it

def draw_rectangle_filled(*args, **kwargs):
    draw_rect_filled(*args, **kwargs)

def run(*args, **kwargs):
    pass
