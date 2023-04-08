from pygame.math import Vector2 as vec2

class tree_node:
    __slots__ = [ 'PARENT', 'LEFT', 'RIGHT', 'DATA', 'TYPE', 'ID' ]
    def __str__(self):
        return f"""DATA: {self.DATA}
TYPE: {"leaf" if self.TYPE == 1 else "node"}
ID: {self.ID if self.TYPE == 0 else self.ID - 32768}"""

class tree_data:
    __slots__ = [ 'SPLITTER_START', 'SPLITTER_DIFF', 'RIGHT_BBOX', 'LEFT_BBOX' ]

    def __init__(self, sstart, sdiff, rbox, lbox):
        self.SPLITTER_START = sstart
        self.SPLITTER_DIFF = sdiff
        self.RIGHT_BBOX = rbox
        self.LEFT_BBOX = lbox

    def __str__(self):

        return "{\n"f"""
    'SPLITTER_START': ({self.SPLITTER_START.x}, {self.SPLITTER_START.y}),
    'SPLITTER_DIFF': ({self.SPLITTER_DIFF.x}, {self.SPLITTER_DIFF.y}),
    'BOXES': """+"{"+f""" 
        'RIGHT': {self.RIGHT_BBOX}, 
        'LEFT': {self.LEFT_BBOX}        
    """+"}\n}"

class tree:
    __slots__ = 'ROOT'
