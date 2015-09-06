import random
import pygame as pg
from .. import tools, prepare
from ..components.grid import AutomataGrid
from ..components.labels import Button, ButtonGroup
from ..components.seeds import PATTERNS

class Sim(tools._State):
    def __init__(self):
        super(Sim, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        self.cell_size = 8
        self.tick_length = 500
        self.min_tick_length = 20
        self.max_tick_length = 1000
        self.timer = 0
        self.running = False

    def make_buttons(self):
        self.buttons = ButtonGroup()
        Button((0, 0, 100, 40), self.buttons, idle_image=prepare.GFX["menu-button"], 
                  hover_image=prepare.GFX["menu-button-solid"], call=self.leave_sim)
        Button((0, 50, 100, 40), self.buttons, idle_image=prepare.GFX["random-button"], 
                  hover_image=prepare.GFX["random-button-solid"], call=self.randomize,
                  bindings=(pg.K_r,))
        if self.rule_name in PATTERNS:
            Button((0, 100, 100, 40), self.buttons, idle_image=prepare.GFX["pattern-button"], 
                      hover_image=prepare.GFX["pattern-button-solid"], call=self.pick_pattern,
                      bindings=(pg.K_p,))
        top = 720
        styles = ("Squares", "Lines", "Circles")
        left = 0
        for style in styles:
            img_name = "{}-button".format(style.lower())
            solid_name = "{}-button-solid".format(style.lower())
            img = prepare.GFX[img_name]
            solid_img = prepare.GFX[solid_name]
            Button(((left, top), img.get_size()), self.buttons, idle_image=img,
                      hover_image=solid_img, call=self.change_draw_style, args=style)
            left += img.get_width() + 5
        top += 20    
        for name in self.grid.colors:
            surf = pg.Surface((135, 10)).convert()
            for x, color in enumerate(self.grid.colors[name].values()):
                pg.draw.rect(surf, color, (x * 15, 0, 15, 10))
            surf.set_alpha(200)
            Button((0, top, 135, 10), self.buttons, idle_image=surf,
                      call=self.change_palette, args=name)
            top += 12
            
    def change_draw_style(self, draw_style):
        self.grid.draw_mode = draw_style
        
    def change_palette(self, palette_name):
        self.grid.colormap = self.grid.colors[palette_name]
        
    def pick_pattern(self, *args):
        self.done = True
        self.persist["grid"] = self.grid
        self.next = "PATTERNMENU"
        self.running = False
        
    def leave_sim(self, *args):
        self.next = "MENU"
        self.running = False
        self.done = True
        
    def randomize(self, *args):
        for cell in self.grid.grid.values():
            cell.alive = random.choice((True, False))
    
    def toggle_running(self):
        self.running = not self.running
        
    def set_caption(self):
        birth = "".join((str(x) for x in self.grid.birth_nums))
        survive = "".join((str(x) for x in self.grid.survive_nums))
        cap = "{} B{}/S{}  Tick Length: {}ms".format(
                  self.rule_name,birth, survive, self.tick_length)
        pg.display.set_caption(cap)
        
    def startup(self, persistent):
        self.running = False
        self.persist = persistent
        rule_name = self.persist["rule"]
        self.rule_name = rule_name
        w, h = self.screen_rect.size
        staggered = "Staggered" in rule_name
        if self.persist["grid"] is None:
            self.grid = AutomataGrid(w, h, self.cell_size, rule_name, staggered=staggered)
        else:
            self.grid = self.persist["grid"]
        self.make_buttons()
        
        self.set_caption()
        self.pattern = self.persist["pattern"]
        
    def get_event(self, event):
        self.buttons.get_event(event)
        if self.pattern is not None:
            self.pattern.get_event(event, self.grid)
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_SPACE:
                self.toggle_running()
            
                
        elif event.type == pg.MOUSEBUTTONUP:
            if not self.running:
                if self.pattern is None:
                    for cell in self.grid.grid.values():
                        if cell.rect.collidepoint(event.pos):
                            cell.alive = not cell.alive
                
    def update(self, keys, dt):
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)
        if self.pattern is not None:
            self.pattern.update(self.grid)
            if not self.pattern.active:
                self.pattern = None
        if keys[pg.K_UP]:
            self.tick_length = max(self.min_tick_length, self.tick_length - 10)
            self.set_caption()
        if keys[pg.K_DOWN]:
            self.tick_length = min(self.max_tick_length, self.tick_length + 10)
            self.set_caption()
        if self.running:
            self.timer += dt
            if self.timer > self.tick_length:
                self.timer -= self.tick_length
                self.grid.update()
            
        
    def draw(self, surface):     
        surface.fill(pg.Color("black"))
        if not self.running:
            for cell in [x for x in self.grid.grid.values() if x.alive]:
                pg.draw.rect(surface, pg.Color("antiquewhite"), cell.rect)
            if self.pattern is not None:
                self.pattern.draw(surface)
                          
            surface.blit(self.grid.overlay, (0, 0))
        else:
            self.grid.draw(surface)
        self.buttons.draw(surface)
        
    