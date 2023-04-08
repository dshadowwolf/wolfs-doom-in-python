import pygame as pg
from pygame.math import Vector2 as vec2
from constants import *
from wadfile import WADFile
from renderer import DoomMapRenderer
pg.init()
screen = pg.display.set_mode(WIN_RES)

wad = WADFile('DOOM.WAD')
map = wad.load_map('E1M1')
renderer = DoomMapRenderer(screen, map)

quit = False
dotcolor = pg.Color(255, 255, 255, 255)
while not quit:
    screen.fill('black')
    renderer.render()
    for e in pg.event.get():
        if e.type == pg.QUIT:
            quit = True
    pg.display.flip()