from src.parser import Config
from .scores import Scores
from src.gui import GUI
from .level import Level, RANDOM_SEED
from src.player import level_speed
import importlib
import pygame

# Arrow keys, and the WASD keys by physical position (scancodes), so the
# same keys work as ZQSD on an AZERTY keyboard.
ARROW_KEYS = {pygame.K_UP: "up", pygame.K_DOWN: "down",
              pygame.K_LEFT: "left", pygame.K_RIGHT: "right"}
WASD_SCANCODES = {pygame.KSCAN_W: "up", pygame.KSCAN_S: "down",
                  pygame.KSCAN_A: "left", pygame.KSCAN_D: "right"}


class Gameplay:

    pacman = importlib.import_module("pac-man")
    Pacman = pacman.Pacman

    def __init__(self, pacman: Pacman, config: Config, scores: Scores, gui: GUI) -> None:
        
        self.state_machine = pacman
        self.gui = gui
        self.config = config
        self.scores = scores
        self.level_timer = 0
        self.score = 0
        self.level_index = 0
        self._load_level(0)

    def _load_level(self, level: int) -> None:

        self.level_index = level
        seed = self.config.seed if level == 0 else RANDOM_SEED
        self.level = Level(self.config.levels[level], self.config, seed)
        self.level.player.speed = level_speed(level)
        self.gui.set_layout(*self.level.dimensions)
        self.surface = self.gui.create_maze_surface(self.level.maze)
        self.level_timer = 0

    def update(self, events: list[pygame.event.Event], dt: float) -> None:

        for event in events:
            if event.type == pygame.QUIT:
                self.state_machine.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state_machine.running = False
                if event.key == pygame.K_RETURN:
                    self.state_machine.game_active = False
                    self.state_machine.state = "main_menu"
                    return
                direction = (ARROW_KEYS.get(event.key)
                             or WASD_SCANCODES.get(event.scancode))
                if direction is not None:
                    self.level.player.turn(direction)
        for cell in self.level.player.update(self.level.maze, dt):
            self.score += self.level.eat(cell)
        if self.level.cleared:
            self._next_level()

    def _next_level(self) -> None:
        """Load the next level, or go back to the menu after the last one."""
        if self.level_index + 1 < len(self.config.levels):
            self._load_level(self.level_index + 1)
        else:  # TODO: victory screen and name entry (tasks 8.4 and 9.2)
            self.state_machine.game_active = False
            self.state_machine.state = "main_menu"

    def draw(self) -> None:

        self.gui.draw_maze(self.surface)
        self.gui.draw_pacgums(self.level.available_pacgums, self.level.available_super_pacgums)
        player = self.level.player
        self.gui.draw_player(player.position, player.facing,
                             player.mouth_opening)
        self.gui.draw_hud(self.score, self.level_index + 1)