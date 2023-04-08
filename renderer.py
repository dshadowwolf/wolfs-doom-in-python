import pygame as pg
from pygame.math import Vector2 as vec2
from constants import *
from player import player
import numpy as np
import math
from helper_routines import *
import json

class DoomMapRenderer:
    def __init__(self, screen, map):
        self.__map__ = map
        self.__screen__ = screen
        self.__player__ = player(map)
        self.x_min, self.x_max, self.y_min, self.y_max = map.get_map_bounds()
        self.vertexes = [vec2(self.remap_x(v.x), self.remap_y(v.y)) for v in map.VERTEXES]

    def remap_x(self, n, out_min=30, out_max=WIDTH-30):
        return int((max(self.x_min, min(n, self.x_max)) - self.x_min) * (
                out_max - out_min) / (self.x_max - self.x_min) + out_min)

    def remap_y(self, n, out_min=30, out_max=HEIGHT-30):
        return int(HEIGHT - (max(self.y_min, min(n, self.y_max)) - self.y_min) * (
                out_max - out_min) / (self.y_max - self.y_min) - out_min)

    def __position_on_backside_of_node(self, node, pos):
        if node.TYPE != 0:
            raise Exception("SSECTOR handed to __position_on_backside_of_node!")
        px = pos.x
        py = pos.y
        d = node.DATA
        nx = d.SPLITTER_START.x
        ny = d.SPLITTER_START.y
        n = vec2(px - nx, py - ny)
        return (n.x * d.SPLITTER_DIFF.y - n.y * d.SPLITTER_DIFF.x) <= 0

    def __bbox_in_fov(self, box, player):
        # setup fast-access data bits...
        px, py = player.POS
        facing = player.ANGLE
        left, top, right, bottom = box[0].x, box[0].y, box[1].x, box[1].y

        # the following are just to stop issues with getting wrapping of values wrong
        # when building lists to check visibility
        a, b = vec2(left, bottom), vec2(left, top)
        c, d = vec2(right, top), vec2(right, bottom)
        sides = ()
        # get the right sets of things to check based on player position
        if px < left:
            if py > top:
                sides = (b, a), (c, b)
            elif py < bottom:
                sides = (b, a), (a, d)
            else:
                sides = (b, a),
        elif px > right: 
            if py > top: 
                sides = (c, b), (d, c)
            elif py < bottom:
                sides = (a, d), (d, c)
            else:
                sides = (d, c),
        else:
            if py > top:
                sides = (c, b),
            elif py < bottom:
                sides = (a, d),
            else:
                return True

        # quick math shite for checking if we've got visibility
        for vect1, vect2 in sides:
            a1 = self.__point_at(vect1)   # get a viewing angle from the player to the first vertex
            a2 = self.__point_at(vect2)   # get a viewing angle from the player to the second vertex

            sp = (a1 - a2) % 360          # normalize the difference in the resulting angles

            a1 -= player.ANGLE            # subtract the players facing angle from the angle pointing towards
                                          # the first vertex from the player, this should normalize a chunk...
            check_v = (a1 + H_FOV) % 360  # add half the FOV back in, mod-360 to hold it to a valid range
            if check_v > FOV:             # we might be outside the players FOV
                if check_v > sp + FOV:    # if true we're definitely outside the players FOV for this pair, lets check the next...
                    continue
            return True                   # we're in the players FOV
        
        return False                      # definitively, no chance, for the player to see this

    def __point_at(self, vertex):
        delta = vertex - self.__player__.POS
        return math.degrees(math.atan2(delta.y, delta.x))

    def __walk_tree(self, current_node, player_object):
        ssectors = { 'RIGHT': [], 'LEFT': [] }
        if current_node.TYPE == 1:
            raise Exception('SSECTOR passed to __walk_tree')
        if self.__position_on_backside_of_node(current_node, player_object.POS):
            if current_node.LEFT.TYPE == 0:
                wres = self.__walk_tree(current_node.LEFT, player_object)
                for side, values in wres.items():
                    for v in values:
                        ssectors[side].append(v)
                if self.__bbox_in_fov(current_node.DATA.RIGHT_BBOX, player_object):
                    if current_node.RIGHT.TYPE == 0:
                        for side, values in self.__walk_tree(current_node.RIGHT, player_object).items():
                            if len(values) <= 0:
                                continue
                            for v in values:
                                ssectors[side].append(v)
                    else:
                        ssectors['RIGHT'].append(current_node.RIGHT.DATA)
            else:
                ssectors['LEFT'].append(current_node.LEFT.DATA)
        else:
            if current_node.RIGHT.TYPE == 0:
                wres = self.__walk_tree(current_node.RIGHT, player_object)
                for side, values in wres.items():
                    for v in values:
                        ssectors[side].append(v)
                if self.__bbox_in_fov(current_node.DATA.LEFT_BBOX, player_object):
                    if current_node.LEFT.TYPE == 0:
                        for side, values in self.__walk_tree(current_node.LEFT, player_object).items():
                            if len(values) <= 0:
                                continue
                            for v in values:
                                ssectors[side].append(v)
            else:
                ssectors['RIGHT'].append(current_node.RIGHT.DATA)
        return ssectors
    
    def __build_draw_list(self):
        # walk the BSP tree, using the players position and view angle to determine if a given nodes bounding box is within the players FOV.
        # if it is, traverse down it to get the sub-sectors and add them to a drawing list
        ssectors = self.__walk_tree(self.__map__.NODES.ROOT, self.__player__)
        seg_list = []
        for ssc in ssectors['LEFT']:
            subsect = self.__map__.SSECTORS[ssc]
            for c in range(0,subsect[0]):
                seg_list.append(self.__map__.SEGS[c+subsect[1]])
            # draw left-side subsectors
        for ssc in ssectors['RIGHT']:
            subsect = self.__map__.SSECTORS[ssc]
            for c in range(0,subsect[0]):
                seg_list.append(self.__map__.SEGS[c+subsect[1]])
            # draw right-side subsectors
        draw_list = []
        for seg in seg_list:
            sv = self.__map__.VERTEXES[seg[0]]
            ev = self.__map__.VERTEXES[seg[1]]
            msv = vec2(self.remap_x(sv.x), self.remap_y(sv.y))
            mev = vec2(self.remap_x(ev.x), self.remap_y(ev.y))
            draw_list.append({'START': msv, 'END': mev})
        return draw_list
    
    def __render_bsp_path_to_player(self):
        cnode = self.__map__.NODES.ROOT
        #self.__walk_or_render_subsectors(cnode)
        segs_to_draw = self.__build_draw_list()
        for seg in segs_to_draw:
            pg.draw.line(self.__screen__, pg.Color(57,255,20,255), seg['START'], seg['END'] )

    def render(self):
        for line in self.__map__.LINEDEFS:
            lstart = self.vertexes[line[0]]
            lend = self.vertexes[line[1]]
            pg.draw.line(self.__screen__, pg.Color(128,128,128,128), lstart, lend, 2)
        # Carmack has the Doom engine using 90 where the math would use 0...
        player_x = self.remap_x(self.__player__.POS.x)
        player_y = self.remap_y(self.__player__.POS.y)
        facing_angle_corrected = -self.__player__.ANGLE + 90
        # instead of using the deg_to_rad from helper_routines, use the Python standard library version
        # for some reason the deg_to_rad() results in the inverse result...
        side_1_s = math.sin(math.radians(facing_angle_corrected - H_FOV))
        side_1_c = math.cos(math.radians(facing_angle_corrected - H_FOV))
        side_2_s = math.sin(math.radians(facing_angle_corrected + H_FOV))
        side_2_c = math.cos(math.radians(facing_angle_corrected + H_FOV))
        fov_ex_1, fov_ey_1 = self.remap_x(self.__player__.POS.x + HEIGHT * side_1_s), self.remap_y(self.__player__.POS.y + HEIGHT * side_1_c)
        fov_ex_2, fov_ey_2 = self.remap_x(self.__player__.POS.x + HEIGHT * side_2_s), self.remap_y(self.__player__.POS.y + HEIGHT * side_2_c)
        pg.draw.line(self.__screen__, pg.Color('orange'), (player_x, player_y), (fov_ex_1, fov_ey_1), 2)
        pg.draw.line(self.__screen__, pg.Color('orange'), (player_x, player_y), (fov_ex_2, fov_ey_2), 2)
        pg.draw.circle(self.__screen__, pg.Color('orange'), (player_x, player_y), 2)
        self.__render_bsp_path_to_player()
