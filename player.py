from pygame.math import Vector2 as vec2
import math

class player:
    __slots__ = [ 'POS', 'ANGLE' ]

    def __init__(self, map):
        pl = map.THINGS[0]
        self.POS = pl[0]
        self.ANGLE = pl[1]

    def __str__(self):
        return f"""
    POSITION: {self.POS}
    ANGLE: {self.ANGLE}"""