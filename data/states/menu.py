import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup


class Menu(tools._State):
    def __init__(self):
        super(Menu, self).__init__()
        self.screen_rect = prepare.SCREEN.get_rect()
        self.buttons = ButtonGroup()
        self.make_buttons()
        
    def make_buttons(self):
        names = ("Conway", "High Life", "Day and Night",
                      "Life Without Death", "Seeds", "Gnarl",
                      "Serviettes", "Walled Cities", "Maze",
                      "Maze w/ Mice")    
        w, h = 250, 65
        cx, cy = self.screen_rect.center
        left1 = cx - (w + 20)
        left2 = cx + 20
        top = 10
        space = 10
        style = {
                "text_color": pg.Color("gray80"),
                "hover_text_color": pg.Color("gray90"),
                "fill_color": pg.Color("gray20"),
                "hover_fill_color": pg.Color("gray30")}
        for name in names:
            Button((left1, top, w, h), self.buttons, text=name, hover_text=name,
                      call=self.start_sim, args=name, **style)
            s_name = "{} {}".format("Staggered", name)
            Button((left2, top, w, h), self.buttons, text=s_name, hover_text=s_name,
                      call=self.start_sim, args=s_name, font_size=24, **style)
            top += h + space
            
    def start_sim(self, rule):
        self.persist["rule"] = rule
        self.persist["pattern"] = None
        self.persist["grid"] = None
        self.next = "SIM"
        self.done = True
        
    def startup(self, persistent):
        self.persist = persistent
        pg.display.set_caption("Automata")
        
    def get_event(self, event):
        self.buttons.get_event(event)
        if event.type == pg.QUIT:
            self.quit = True
        elif (event.type == pg.KEYUP and 
              event.key == pg.K_ESCAPE):
            self.quit = True
        
    def update(self, keys, dt):
        self.buttons.update(pg.mouse.get_pos())
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.buttons.draw(surface)
       
    

