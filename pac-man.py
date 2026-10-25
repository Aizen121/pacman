import sys
import pygame
from src.parser import Parser
from src.gui import GUI
from src.game.scores import Scores
from src.constants import FULLSCREEN

# State opened by each main-menu entry, in the order of the menu
MENU_STATES = ["game", "highscores", "instructions", "exit"]


class Pacman: 

    def __init__(self, config_file: str) -> None:
        self.config = Parser.get_config(config_file)
        
        pygame.init()
        sizes = pygame.display.get_desktop_sizes()
        width, height = sizes[0] if sizes else (1400, 800)
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((width, height),
                                                  pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width * 9 // 10,
                                                   height * 9 // 10))
        pygame.display.set_caption("Pac-man @ 42")
        self.running: bool = True
        self.state: str = "main_menu"
        self.win: bool = None
        self.current_level = 0
        self.scores = Scores(self.config.highscore_filename)
        self.gui = GUI(self.screen, self)
        self.menu_index = 0
        self.game_active = False
        self.finished = False
        self._run()

    def _main_menu(self, events: list[pygame.event.Event],
                   dt: float) -> None:

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                index = self.gui.menu_item_at(event.pos)
                if index is not None:
                    self.menu_index = index
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                index = self.gui.menu_item_at(event.pos)
                if index is not None:
                    self._open(index)
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(MENU_STATES)
                elif event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(MENU_STATES)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    self._open(self.menu_index)
                    return
        self.gui.draw_main_menu(self.menu_index)

    def _open(self, index: int) -> None:
        """Open the screen of the menu entry index, or quit on EXIT."""
        if MENU_STATES[index] == "exit":
            self.running = False
        else:
            self.state = MENU_STATES[index]

    def _wants_back(self, event: pygame.event.Event) -> bool:
        """Tell whether event asks to go back to the main menu."""
        if event.type == pygame.KEYDOWN:
            return event.key in (pygame.K_ESCAPE, pygame.K_RETURN)
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.gui.back_button_hit(event.pos))

    def _highscores(self, events: list[pygame.event.Event],
                    dt: float) -> None:

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif self._wants_back(event):
                self.state = "main_menu"
                return
        self.gui.draw_highscores(self.scores)

    def _instructions(self, events: list[pygame.event.Event],
                      dt: float) -> None:

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif self._wants_back(event):
                self.state = "main_menu"
                return
        self.gui.draw_instructions(self.config)

    def _game(self, events: list[pygame.event.Event], dt: int) -> None:
    
        from src.game.gameplay import Gameplay
        
        if not self.game_active:
            self.gameplay = Gameplay(self, self.config, self.scores, self.gui)
            self.game_active = True 
        self.gameplay.update(events, dt)
        self.gameplay.draw()
        if self.finished:
            self.state = "game_end"


    # def game_end(self, events, dt) -> None:

    def _run(self) -> None:

        program_states = {
            "main_menu": self._main_menu,
            "highscores": self._highscores,
            "instructions": self._instructions,
            "game": self._game,
            # "game_end": self._end_game,
        }

        clock = pygame.time.Clock()

        try:
            while self.running:
                dt = clock.tick(60) / 1000.0
                events = pygame.event.get()
                program_states[self.state](events, dt)
                pygame.display.flip()
        except KeyboardInterrupt:
            print("Error: Main Loop: Program Interrupted.\n")
            pygame.quit()
            sys.exit(1)


def main() -> None:

    if len(sys.argv) != 2 or not sys.argv[1].endswith(".json"):
        print("Error: Wrong arguments.\nUsage: python3 pac-man.py config.json")
        sys.exit(1)
    else:
        Pacman(sys.argv[1])


if __name__ == "__main__":
    main()
