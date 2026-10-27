from src.parser import Config
from .scores import Scores
from src.gui import GUI
from .level import Level, RANDOM_SEED
from src.ghost import GHOST_SPEED_RATIO
from src.player import level_speed
import importlib
import math
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
        self.score = 0
        self.lives = config.lives
        self.level_index = 0
        self._load_level(0)

    def _load_level(self, level: int) -> None:

        self.level_index = level
        seed = self.config.seed if level == 0 else RANDOM_SEED
        self.level = Level(self.config.levels[level], self.config, seed)
        self.level.player.speed = level_speed(level)
        for ghost in self.level.ghosts:
            ghost.speed = GHOST_SPEED_RATIO * self.level.player.speed
        self.gui.set_layout(*self.level.dimensions)
        self.surface = self.gui.create_maze_surface(self.level.maze)
        self.time_left = float(self.config.level_max_time)  # seconds

    def update(self, events: list[pygame.event.Event], dt: float) -> None:

        for event in events:
            if event.type == pygame.QUIT:
                self.state_machine.running = False
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and self.gui.back_button_hit(event.pos)):
                self._back_to_menu()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._back_to_menu()
                    return
                direction = (ARROW_KEYS.get(event.key)
                             or WASD_SCANCODES.get(event.scancode))
                if direction is not None:
                    self.level.player.turn(direction)
        player = self.level.player
        for cell in player.update(self.level.maze, dt):
            if cell in self.level.available_super_pacgums:
                for ghost in self.level.ghosts:
                    ghost.frighten()
            self.score += self.level.eat(cell)
        for ghost in self.level.ghosts:
            if ghost.edible:
                ghost.flee(player)
            elif not ghost.eaten:
                ghost.chase(player, self.level.maze)
            ghost.update(self.level.maze, dt)
            if ghost.eaten or not ghost.touches(player):
                continue
            if not ghost.edible:
                self._lose_life()
                return
            ghost.get_eaten()
            self.score += self.config.points_per_ghost
        if self.level.cleared:
            self._next_level()
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._time_up()

    def _time_up(self) -> None:
        """Out of time: one life less, then the level timer starts again."""
        self._lose_life()
        self.time_left = float(self.config.level_max_time)

    def _lit_logo(self) -> list[tuple[int, int]]:
        """Return the cells of the "42" still lit, as a gauge of the time.

        The logo empties from the top, one cell at a time, as the time
        left goes down; Level.logo lists its cells row by row, top first.
        """
        logo = self.level.logo
        lit = math.ceil(len(logo) * self.time_left
                        / self.config.level_max_time)
        return logo[len(logo) - lit:]

    def _next_level(self) -> None:
        """Load the next level, or go back to the menu after the last one."""
        if self.level_index + 1 < len(self.config.levels):
            self._load_level(self.level_index + 1)
        else:  # TODO: victory screen and name entry (tasks 8.4 and 9.2)
            self._back_to_menu()

    def _back_to_menu(self) -> None:
        """End this game session and show the main menu."""
        self.state_machine.game_active = False
        self.state_machine.state = "main_menu"

    def _lose_life(self) -> None:
        """Pac-Man was caught: one life less, then everyone restarts."""
        self.lives -= 1
        if self.lives <= 0:  # TODO: game-over screen and name entry (8.4)
            self._back_to_menu()
            return
        self.level.player.respawn()
        for ghost in self.level.ghosts:
            ghost.respawn()

    def draw(self) -> None:

        self.gui.draw_maze(self.surface)
        self.gui.draw_logo(self._lit_logo())
        self.gui.draw_pacgums(self.level.available_pacgums, self.level.available_super_pacgums)
        for ghost in self.level.ghosts:
            self.gui.draw_ghost(ghost.position, ghost.name, ghost.facing,
                                ghost.fright_time, ghost.eaten)
        player = self.level.player
        self.gui.draw_player(player.position, player.facing,
                             player.mouth_opening)
        self.gui.draw_hud(self.score, self.level_index + 1, self.lives,
                          self.time_left)