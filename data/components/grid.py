from collections import defaultdict
import pygame as pg
from .. import prepare

class Cell(object):    
    def __init__(self, index, center, cell_size, offsets):
        self.index = index
        self.rect = pg.Rect((0,0), (cell_size, cell_size))
        self.rect.center = center
        self.neighbor_indices = [(self.index[0] + offset[0], self.index[1] + offset[1])
                                         for offset in offsets]
        self.alive = False
        self.connections = []
        self.old_connections = []
        self.last_alive = self.alive
        self.num_live_neighbors = 0
        
    def get_connections(self, world):
        if self.alive:
            grid = world.grid
            connections = []
            for indx in self.neighbor_indices:
                try:
                    other_cell = grid[indx]
                except KeyError:
                    other_cell = None
                if other_cell and other_cell.alive:
                    connections.append((self.rect.center, other_cell.rect.center))            
            self.connections = connections
            
    def get_live_neighbors(self, world):
        grid = world.grid
        num_live_neighbors = 0
        for indx in self.neighbor_indices:
            try:
                other_cell = grid[indx]
            except KeyError:
                if world.infinite and self.alive:
                    w, h = self.rect.size
                    x, y = indx[0] *  w, indx[1] *  h
                    cx, cy = x * (w//2), y * (h//2)
                    if not world.staggered:
                        grid[indx] = Cell(indx, (x + (w//2), y + (h//2)), w, world.moore_offsets)
                    elif not indx[0] % 2:
                        grid[indx] = Cell(indx, (x + (w//2), y + (h//2)), w, world.even_offsets)
                    else:
                        grid[indx] = Cell(indx, (x + (w//2), y + h), w, world.odd_offsets)
                    other_cell = grid[indx]
                else:
                    other_cell = None
            if other_cell and other_cell.alive:
                num_live_neighbors += 1
        self.num_live_neighbors = num_live_neighbors

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        
class AutomataGrid(object):
    colors = {"Warm":  {x: pg.Color(250, 250 - (x*25), 5) for x in range(8, -1, -1)},
                                 #0: pg.Color("oldlace"),
                                 #1: pg.Color("palegoldenrod"),
                                 #2: pg.Color("yellow1"),
                                 #3: pg.Color("yellow3"),
                                 #4: pg.Color("orange1"),
                                 #5: pg.Color("orange4"),
                                 #6: pg.Color("orangered"),
                                 #7: pg.Color("red1"),
                                 #8: pg.Color("red3")},
                  "Cool":  {0: pg.Color(127,201,255),
                               1: pg.Color(114,181,229),
                               2: pg.Color(102,161,204),
                               3: pg.Color(89,141,178),
                               4: pg.Color(76,121,153),
                               5: pg.Color(63,100,127),
                               6: pg.Color(51,80,102),
                               7: pg.Color(38,60,76),
                               8: pg.Color(25,41,51)},
                  "Monochrome": {num: pg.Color("gray{}".format(x))
                            for num, x in enumerate(range(20, 101, 10))},
                  "White": {num: pg.Color("antiquewhite") for num in range(9)}
                 }                         
    rules = {"Conway": ((3,), (2, 3)),
                "Staggered Conway": ((3,), (2,3)),
                "High Life": ((3,6), (2,3)),
                "Staggered High Life": ((3,6), (2,3)),
                "Day and Night": ((3,6,7,8), (3,4,6,7,8)),
                "Staggered Day and Night": ((3,6,7,8), (3,4,6,7,8)),
                "Life Without Death": ((3,), (0,1,2,3,4,5,6,7,8)),
                "Staggered Life Without Death": ((3,), (0,1,2,3,4,5,6,7,8)),
                "Seeds": ((2,), tuple()),
                "Staggered Seeds": ((2,), tuple()),
                "Gnarl": ((1,), (1,)),
                "Serviettes": ((2,3,4), tuple()),
                "Walled Cities": ((4,5,6,7,8), (2,3,4,5)),
                "Maze": ((3,), (1,2,3,4,5)),
                "Maze w/ Mice": ((3,7), (1,2,3,4,5))}
    for rname in ("Gnarl", "Serviettes", "Walled Cities", "Maze", "Maze w/ Mice"):
        rules["Staggered {}".format(rname)] = rules[rname]
    even_offsets = ((-1,0), (0,-1), (1,0), (1,1), (0,1), (-1,1))
    odd_offsets = ((-1,-1), (0,-1), (1,-1), (1,0), (0,1), (-1,0))
    moore_offsets = [(x, y) for x in (-1, 0, 1) for y in (-1, 0, 1) if (x, y) != (0, 0)]
    
    def __init__(self, width, height, cell_size, rule="Conway", 
                      staggered=False, infinite=True, palette="Monochrome"):
        self.sim_name = rule
        self.staggered = staggered
        self.infinite = infinite
        self.birth_nums = self.rules[rule][0]
        self.survive_nums = self.rules[rule][1]
        self.line_weight = 2
        self.connections = {}
        self.colormap = self.colors[palette]
        self.make_grid(width, height, cell_size)
        self.make_overlay(width, height, cell_size)
        self.draw_mode = "Squares"
        self.cell_size = cell_size
        
    def make_overlay(self, width, height, cell_size):
        self.overlay = pg.Surface((width, height)).convert_alpha()
        self.overlay.fill((0,0,0,0))
        color = pg.Color("gray30")
        if self.staggered:
            for cell in self.grid.values():
                pg.draw.rect(self.overlay, color, cell.rect, 1)
        else:
            for x in range(0, width + 1, cell_size):
                pg.draw.line(self.overlay, color, (x, 0), (x, height), 2)
            for y in range(0, height + 1, cell_size):
                pg.draw.line(self.overlay, color, (0, y), (width, y), 2)
        
    def make_grid(self, width, height, cell_size):
        self.grid = {}
        for column, x in enumerate(range(cell_size//2, width, cell_size)):
            for row, y in enumerate(range(cell_size//2, height, cell_size)):
                if not self.staggered:
                    self.grid[(column, row)] = Cell((column, row), (x, y), cell_size, self.moore_offsets)
                elif not column % 2:
                    self.grid[(column, row)] = Cell((column, row), (x, y), cell_size, self.even_offsets)
                else:
                    self.grid[(column, row)] = Cell((column, row), (x, y + cell_size//2), cell_size, self.odd_offsets)
        self.end_column = column
        self.end_row = row
        
    def update(self):
        for cel in self.grid.values():
            cel.get_live_neighbors(self)
        for cell_ in self.grid.values():
            if cell_.alive:
                if cell_.num_live_neighbors not in self.survive_nums:
                    cell_.alive = False
            else:
                if cell_.num_live_neighbors in self.birth_nums:
                    cell_.alive = True   
        
        for a_cell in self.grid.values():
            a_cell.get_connections(self)
        connections = defaultdict(set)
        for cell in [x for x in self.grid.values() if x.alive]:
            num = len(cell.connections)
            for c1, c2 in cell.connections:
                swaps = [((c1[0], c1[1]), (c2[1], c2[0])),
                              ((c1[1], c1[0]), (c2[0], c2[1])),
                              ((c1[1], c1[0]), (c2[1], c2[0]))]
                if not any((s in connections[num] for s in swaps)):
                    connections[num].add((c1, c2))
        for c in sorted(connections.keys(), reverse=True):
            for connection in connections[c]:
                for i in range(c):
                    if connection in connections[i]:
                        connections[i].remove(connection)
        self.connections = connections
        
        
           
    def draw(self, surface):
        if self.draw_mode == "Lines":
            for num in self.connections:
                for c1, c2 in self.connections[num]:
                    pg.draw.line(surface, self.colormap[num], c1, c2, self.line_weight)
        elif self.draw_mode == "Squares":
            for cell in [c for c in self.grid.values() if c.alive]:
                pg.draw.rect(surface, self.colormap[cell.num_live_neighbors], cell.rect.inflate(-2, -2))
        elif self.draw_mode == "Circles":
            for cell in [c for c in self.grid.values() if c.alive]:
                pg.draw.circle(surface, self.colormap[cell.num_live_neighbors], cell.rect.center, (cell.rect.width//2))
                