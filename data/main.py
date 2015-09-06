from . import prepare,tools
from .states import sim, menu, pattern_menu

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"SIM": sim.Sim(),
                  "MENU": menu.Menu(),
                  "PATTERNMENU": pattern_menu.PatternMenu()}
    controller.setup_states(states, "MENU")
    controller.main()
