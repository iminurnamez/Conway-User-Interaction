from collections import deque
import pygame as pg
from .. import tools, prepare
from ..components.seeds import PATTERNS
from ..components.labels import Label, Button, ButtonGroup


class Pattern(object):
    def __init__(self, charmap, cell_size):
        self.cell_size = cell_size
        self.cells_wide = len(charmap[0])
        self.cells_tall = len(charmap)
        self.make_rotations(charmap)
        self.active = True
        self.current_rotation = self.rotations[0]
        self.make_surface()
        
        
    def make_surface(self):    
        size = self.cell_size
        self.surf = pg.Surface((len(self.current_rotation[0]) *  size, 
                                       len(self.current_rotation) * size)).convert_alpha()
        self.surf.fill((0,0,0,0))
        for y, row in enumerate(self.current_rotation):
            for x, char in enumerate(row):
                if char == "X":
                    pg.draw.rect(self.surf, pg.Color("white"),
                                      (x * size, y * size, size, size))
                                              
        
    def make_rotations(self, charmap):
        new_rows = []
        rows = charmap
        for i in range(self.cells_wide):
            new_rows.append("".join((row[i] for row in rows)))
        rt90 = new_rows
        rt180 = [row[::-1] for row in rows]
        rt270 = [r[::-1] for r in rt90]
        self.rotations = deque([charmap, rt90, rt180, rt270])
    
    def add_to_grid(self, grid):
        tl = self.topleft_index
        for x in range(len(self.current_rotation[0])):
            for y in range(len(self.current_rotation)):
                indx = tl[0] + x, tl[1] + y
                grid.grid[indx].alive = self.current_rotation[y][x] == "X"
        self.active = False
        
    def get_event(self, event, grid):
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                if self.active:
                    self.add_to_grid(grid)
            elif event.button == 3:
                if self.active:
                    self.active = False
        elif event.type == pg.KEYUP:
            if self.active:
                if event.key == pg.K_LEFT:
                    self.rotations.rotate(-1)
                    self.current_rotation = self.rotations[0]
                    self.make_surface()
                if event.key == pg.K_RIGHT:
                    self.rotations.rotate(1)
                    self.current_rotation = self.rotations[0]
                    self.make_surface()
                    
    def update(self, grid):
        cell_size = grid.cell_size
        mx, my = pg.mouse.get_pos()
        cell_index = mx // cell_size, my // cell_size
        self.topleft_index = cell_index
        self.topleft = cell_index[0] * self.cell_size, cell_index[1] *  self.cell_size
                        
    def draw(self, surface):
        if self.active:
            surface.blit(self.surf, self.topleft)
            
            
class PatternMenu(tools._State):
    def __init__(self):
        super(PatternMenu, self).__init__()
        self.screen_rect = prepare.SCREEN.get_rect()
        self.font = None
        
    def startup(self, persistent):
        self.persist = persistent
        cell_size = self.persist["grid"].cell_size
        rule = self.persist["rule"]
        stills = PATTERNS[rule]["Still Lifes"]
        oscillators = PATTERNS[rule]["Oscillators"]
        ships = PATTERNS[rule]["Spaceships"]
        methuselas = PATTERNS[rule]["Methuselas"]
        guns = PATTERNS[rule]["Guns"]
        self.stills = [Pattern(still, cell_size) for still in stills]
        self.oscillators = [Pattern(oscillator, cell_size) for oscillator in oscillators]
        self.ships = [Pattern(ship, cell_size) for ship in ships]
        self.methuselas = [Pattern(methusela, cell_size) for methusela in methuselas]
        self.guns = [Pattern(gun, cell_size) for gun in guns]
        self.make_menu()
        
    def choose_pattern(self, pattern):
        self.persist["pattern"] = pattern
        self.done = True
        self.next = "SIM"
        
    def make_menu(self):
        size = self.persist["grid"].cell_size
        self.labels = []
        self.buttons = ButtonGroup()
        top = 10
        left = 20
        title_space = 15
        group_space = 20
        line_space = 100
        element_space = 20
        titles_to_patterns = [("Still Lifes", self.stills), ("Oscillators", self.oscillators),
                                      ("Spaceships", self.ships), ("Methuselas", self.methuselas),
                                      ("Guns", self.guns)]
        for title, patterns in titles_to_patterns:
            if patterns:
                label = Label(self.font, 24, title, pg.Color("gray80"), {"topleft": (left, top)})
                self.labels.append(label)
                top += label.rect.height + title_space            
                for p in patterns:
                    if left + p.surf.get_width() > self.screen_rect.right:
                        left = 20
                        top += line_space
                    Button(((left, top), p.surf.get_size()), self.buttons, idle_image=p.surf,
                              call=self.choose_pattern, args=p)
                    left += p.surf.get_width() + element_space
                top += group_space + line_space
                left = 20
        instruct1 = Label(self.font, 16, "Left-click to select a pattern", pg.Color("gray80"),
                                {"midtop": (self.screen_rect.centerx, self.screen_rect.bottom - 50)})
        instruct2 = Label(self.font, 16, "Right-click to cancel", pg.Color("gray80"),
                                {"midtop": (self.screen_rect.centerx, self.screen_rect.bottom - 30)})
        self.labels.extend([instruct1, instruct2])                        
    def get_event(self, event):
        self.buttons.get_event(event)
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                self.done = True
                self.persist["pattern"] = None
                self.next = "SIM"                
            
        
    def update(self, keys, dt):
        self.buttons.update(pg.mouse.get_pos())
        
    def draw(self, surface):
        surface.fill(pg.Color("gray20"))
        for label in self.labels:
            label.draw(surface)
        self.buttons.draw(surface)
        
        