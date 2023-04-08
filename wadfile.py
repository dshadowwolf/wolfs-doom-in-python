from data_readers import *
import re
from pygame.math import Vector2 as vec2
import json
import math
from helper_routines import *
from datatypes import tree_node, tree, tree_data

def to_radians(angle):
    return bam16_to_rad(angle)

class WADHeader:
    __slots__ = [ 'MAGIC', 'num_lumps', 'dir_offs' ]

    def __init__(self, file):
        self.MAGIC = "".join([chr(ord(x)) for x in read_4(file)])
        self.num_lumps = read_int(file)
        self.dir_offs = read_int(file)

    def __str__(self):
        return f'MAGIC: {self.MAGIC}\nNumber of Lumps: {self.num_lumps}\nDirectory Offset: 0x{self.dir_offs:08x}'

class WADMap:
    __slots__ = [ 'name', 'THINGS', 'LINEDEFS','SIDEDEFS','VERTEXES','SEGS','SSECTORS','NODES','SECTORS','REJECT','BLOCKMAP']

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'Map: {self.name}'
    
    def load(self, file):
        for c in range(0,10):
            noffs = read_int(file)
            nsz = read_int(file)
            type = ''.join([ chr(a) for a in [ ord(b) for b in read_8(file) ] ])
            offs = file.tell()
            if type == 'THINGS':
                self.THINGS = self.__load_things(file, noffs, nsz)
                file.seek(offs)
            elif type == 'LINEDEFS':
                self.LINEDEFS = self.__load_linedefs(file, noffs, nsz)
                file.seek(offs)
            elif type == 'SIDEDEFS':
                self.SIDEDEFS = self.__load_sidedefs(file, noffs, nsz)
                file.seek(offs)
            elif type == 'VERTEXES':
                self.VERTEXES = self.__load_vertexes(file, noffs, nsz)
                file.seek(offs)
            elif type == 'SEGS':
                self.SEGS = self.__load_segs(file, noffs, nsz)
                file.seek(offs)
            elif type == 'SSECTORS':
                self.SSECTORS = self.__load_ssectors(file, noffs, nsz)
                file.seek(offs)
            elif type == 'NODES':
                raw_data = self.__load_nodes(file, noffs, nsz)
                self.NODES = self.__build_tree(raw_data)
                file.seek(offs)
            elif type == 'SECTORS':
                self.SECTORS = self.__load_sectors(file, noffs, nsz)
                file.seek(offs)
            elif type == 'REJECT':
                self.REJECT = self.__load_reject(file, noffs, nsz)
                file.seek(offs)
            elif type == 'BLOCKMAP':
                self.BLOCKMAP = self.__load_blockmap(file, noffs, nsz)
                file.seek(offs)

    def __build_tree(self, nodemap):
        tree_ = tree()
        # should define a type here...
        tree_.ROOT = self.__make_node(None, len(nodemap)-1, nodemap, 0)
        return tree_

    def __make_node(self, parent, node_index, nodemap, c):
        n = tree_node()
        n.ID = node_index
        n.PARENT = parent
        if node_index >= 32768: # if bit 15 is set, this points to a subsector
            n.TYPE = 1
            n.DATA = node_index - 32768 #self.__subsector_node(n, node_index - 32768)
        else:
            m = nodemap[node_index]
            n.TYPE = 0
            startp = vec2(m[0], m[1])
            endp = vec2(m[2], m[3])
            n.DATA = tree_data(startp, endp, m[4], m[5])
            c += 1
            n.LEFT = self.__make_node(n, m[7], nodemap, c)
            c += 1
            n.RIGHT = self.__make_node(n, m[6], nodemap, c)
        return n
    
    def __subsector_node(self, parent, index):
        return self.SSECTORS[index]
    
    def __load_things(self, file, offset, size):
        num_things = size // 10 # five shorts
        file.seek(offset)
        rv = []
        for th in range(0,num_things):
            pos = vec2(read_short(file), read_short(file))
            facing = read_short(file)
            type = read_short(file)
            flags = read_short(file)
            rv.append((pos,facing,type,flags))
        return rv

    def __load_linedefs(self, file, offset, size):
        num_defs = size // 14 ## each entry is 7 shorts
        file.seek(offset)
        rv = []
        for ld in range(0,num_defs):
            start = read_short(file)
            end = read_short(file)
            flags = read_short(file)
            special = read_short(file)
            sector = read_short(file)
            front = read_short(file)
            back = read_short(file)
            rv.append((start,end,flags,special,sector,front,back))
        return rv

    def __load_sidedefs(self, file, offset, size):
        num_defs = size // 30 # three 8-character names, 3 shorts
        file.seek(offset)
        rv = []
        for sd in range(0,num_defs):
            x_off = read_short(file)
            y_off = read_short(file)
            upper_name = ''.join([ chr(x) for x in [ ord(y) for y in read_8(file)]])
            lower_name = ''.join([ chr(x) for x in [ ord(y) for y in read_8(file)]])
            middle_name = ''.join([ chr(x) for x in [ ord(y) for y in read_8(file)]])
            sector = read_short(file)
            rv.append( (x_off, y_off, upper_name, lower_name, middle_name, sector) )
        return rv

    def __load_vertexes(self, file, offset, size):
        file.seek(offset)
        numverts = size // 4 # each vertex is a pair of signed 16 bit ints
        rv = []
        for v in range(0,numverts):
            x = read_short(file)
            y = read_short(file)
            rv.append(vec2(x,y))
        return rv

    def __load_segs(self, file, offset, size):
        file.seek(offset)
        num_segs = size // 12 # 6 shorts
        rv = []
        for seg in range(0,num_segs):
            start = read_short(file)
            end = read_short(file)
            angle = read_short(file)
            linedef = read_short(file)
            direction = read_short(file)
            offset_distance = read_short(file)
            rv.append((start,end,angle,linedef,direction,offset_distance))
        return rv

    def __load_ssectors(self, file, offset, size):
        num_subsectors = size // 4
        rv = []
        file.seek(offset)
        for subs in range(0,num_subsectors):
            seg_count = read_short(file)
            first_seg = read_short(file)
            rv.append((seg_count, first_seg))
        return rv

    def __load_nodes(self, file, offset, size):
        file.seek(offset)
        rv = []
        while file.tell() < offset+size:
            x_start = read_short(file)
            y_start = read_short(file)
            x_diff = read_short(file)
            y_diff = read_short(file)
            rbt = read_short(file)
            rbb = read_short(file)
            rbl = read_short(file)
            rbr = read_short(file)
            right_box = (vec2(rbl,rbt),vec2(rbr,rbb))
            lbt = read_short(file)
            lbb = read_short(file)
            lbl = read_short(file)
            lbr = read_short(file)
            left_box = (vec2(lbl,lbt),vec2(lbr,lbb))
            right_child = read_unsigned_short(file)
            left_child = read_unsigned_short(file)
            rv.append((x_start,y_start,x_diff,y_diff,right_box, left_box, right_child, left_child))
        return rv

    def __load_sectors(self, file, offset, size):
        num_sectors = size // 26
        file.seek(offset)
        rv = []
        for sector in range(0,num_sectors):
            floor = read_short(file)
            ceiling = read_short(file)
            floor_tex = ''.join([ chr(x) for x in [ ord(y) for y in read_8(file)]])
            ceiling_tex = ''.join([ chr(x) for x in [ ord(y) for y in read_8(file)]])
            light = read_short(file)
            special = read_short(file)
            tag = read_short(file)
            rv.append((floor, ceiling, floor_tex, ceiling_tex, light, special, tag))
        return rv

    def __load_reject(self, file, offset, size):
        pass
        # # size is a bit tetchy, each entry is 4 bytes long, but this thing is _special_
        # # for now... lets load it the special way...
        # # in fact, this whole thing is rather tetchy and works for special purposes
        # # each bit of the bytes read maps into a 5x5 grid 
        # rv = []
        # end = offset+size
        # file.seek(offset)
        # while file.tell() < end:
        #     r = []
        #     r.append(read_unsigned_byte(file))
        #     r.append(read_unsigned_byte(file))
        #     r.append(read_unsigned_byte(file))
        #     r.append(read_unsigned_byte(file))
        #     rv.append(r)
        # return rv

    def __load_blockmap(self, file, offset, size):
        pass
        # # this this is even worse than the f*cking POS REJECTS
        # rv = { 'HEADER': {}, 'MAP': [] }
        # end = offset+size
        # file.seek(offset)
        # # read the header
        # rv['HEADER']['X_GRID'] = read_short(file)
        # rv['HEADER']['Y_GRID'] = read_short(file)
        # rv['HEADER']['NUM_COLS'] = read_short(file)
        # rv['HEADER']['NUM_ROWS'] = read_short(file)
        # bc = rv['HEADER']['NUM_COLS'] * rv['HEADER']['NUM_ROWS']
        # offsets = []
        # for bln in range(0,bc):
        #     offsets.append(read_short(file)*2)
        # for offs in offsets:
        #     mv = []
        #     file.seek(offset) # reset to the start of the blockmap
        #     file.seek(offs, 1) # seek to the start of the map data for this block
        #     v = read_short(file)
        #     while v != 0xFFFF and file.tell() < (offset+size):
        #         mv.append(v)
        #         if file.tell() < (offset+size):
        #             v = read_short(file)
        #         else:
        #             break
        #     rv['MAP'].append(mv)
        # return rv

    def get_map_bounds(self):
        x_sorted = sorted(self.VERTEXES, key=lambda v: v.x)
        x_min, x_max = x_sorted[0].x, x_sorted[-1].x

        y_sorted = sorted(self.VERTEXES, key=lambda v: v.y)
        y_min, y_max = y_sorted[0].y, y_sorted[-1].y

        return x_min, x_max, y_min, y_max
    
class WADDirEntry:
    __slots__ = [ 'offset', 'size', 'name', 'base_offset' ]

    def __init__(self, base, offs, sz, n):
        self.offset = offs
        self.size = sz
        self.name = n
        self.base_offset = base

    def __str__(self):
        return f'Name: {self.name}\nOffset: 0x{self.offset:08X}\nsize: {self.size/1024:2.02f}kb'
    
class WADDir:
    __slots__ = 'lumps'
    def __init__(self, wad_header, file):
        self.lumps = []
        file.seek(wad_header.dir_offs)
        lcount = 0
        while lcount < wad_header.num_lumps:
            base_offs = file.tell()
            offs = read_int(file)
            size = read_int(file)
            name = ''.join([ chr(a) for a in [ ord(b) for b in read_8(file) ] ])
            self.lumps.append(WADDirEntry(base_offs, offs,size,name))
            lcount += 1

    def __str__(self):
        rv = [ "DIRECTORY" ]
        for lump in self.lumps:
            rv.append(str(lump))
        return '\n'.join(rv)
        
    def get_entry_named(self, name):
        for l in self.lumps:
            if l.name == name:
                return l
        return None
    
class WADFile:
    __slots__ = ['NAME', 'DIRECTORY', 'HEADER']

    def __init__(self, filename):
        self.NAME = filename
        with open(filename, 'rb') as f:
            self.HEADER = WADHeader(f)
            self.DIRECTORY = WADDir(self.HEADER,f)

    def load_map(self, mapname):
        with open(self.NAME, 'rb') as file:
            m = WADMap(mapname)
            d_ent = self.DIRECTORY.get_entry_named(mapname)
            if d_ent is None:
                print(f'Map {mapname} not found in WAD File {self.NAME}')
                return
            file.seek(d_ent.base_offset)
            # the next few bits are a throw-away to clear the map-marker entry
            a = read_int(file)
            a = read_int(file)
            a = read_8(file)
            m.load(file)
        return m
