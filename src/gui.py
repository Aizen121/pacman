"""All the drawing: menus, maze, characters and HUD.

Only MLX-like primitives are used: pixels (set_at), images (blit) and text
(string_put). Positions are computed from the size of the window.
"""
import math

import pygame

from src.constants import (BG_COLOR, BOTTOM, DIM_COLOR, EYE_COLOR,
                           FACING_ANGLES, FLASH_COLOR, FLASH_TIME, FONT,
                           FRIGHT_COLOR, GHOST_COLORS, HIGHLIGHT_COLOR,
                           LEFT, LOGO, LOGO_COLOR, MARGIN, MAZE_LEFT,
                           MOUTH_ANGLES, PACGUM_COLOR, PACMAN_COLOR,
                           PUPIL_COLOR, RIGHT, TEXT_COLOR, TILE, TOP, WALL,
                           WALL_COLOR)
from src.game.scores import Scores
from src.parser import Config

MENU_ITEMS = ("START", "HIGHSCORES", "INSTRUCTIONS", "EXIT")
MENU_HINT = "UP/DOWN or MOUSE: choose - ENTER or CLICK: open - ESC: quit"
CREDITS = ("This project has been created as part of the 42 curriculum "
           "by rvaz-da-")
BACK_LABEL = "< BACK (ESC)"
RANKS = ("1ST", "2ND", "3RD", "4TH", "5TH", "6TH", "7TH", "8TH", "9TH",
         "10TH")


class GUI:
    """Draws every screen of the game in the window."""

    def __init__(self, screen: pygame.Surface, program: object) -> None:
        """Load the assets and size the fonts and icons to the window.

        Args:
            screen: The window surface.
            program: The application (kept for the menus).
        """
        self.screen = screen
        self.program = program
        self.width, self.height = screen.get_size()
        self.logo = pygame.image.load(LOGO).convert_alpha()
        self.title_font = pygame.font.Font(FONT, max(20, self.height // 16))
        self.menu_font = pygame.font.Font(FONT, max(14, self.height // 26))
        self.hud_font = pygame.font.Font(FONT, max(10, self.height // 40))
        self.small_font = pygame.font.Font(FONT, max(8, self.height // 70))
        icon = max(6, self.height // 50)  # radius of the menu and HUD icons
        self.icon_pacman = self.make_pacman_sprite(icon, 0, 60)
        self.icon_ghosts = [self.make_ghost_sprite(icon, color, 0)
                            for color in GHOST_COLORS.values()]
        self.icon_frightened = self.make_ghost_sprite(icon, FRIGHT_COLOR, 0)
        self.icon_pacgum = self.make_circle_sprite(max(2, icon // 4),
                                                   PACGUM_COLOR)
        self.icon_super = self.make_circle_sprite(max(3, icon // 2),
                                                  PACGUM_COLOR)
        # the HUD panel on the left is at least wide enough for BACK
        self.panel_width = max(MAZE_LEFT, self.back_rect().right + MARGIN)
        self.tile, self.wall = TILE, WALL
        self.offset = (self.panel_width, MARGIN)
        self._make_sprites()

    # ------------------------------------------------------------ layout

    def set_layout(self, width: int, height: int) -> None:
        """Fit a maze of width x height cells in the window.

        Cells are at most TILE pixels wide: small mazes keep that size and
        big ones shrink until they fit. The maze is centred in the area
        right of the HUD, and the sprites are redrawn at the new size.
        """
        area_w = self.width - self.panel_width - MARGIN
        area_h = self.height - 2 * MARGIN
        self.tile = min(TILE, area_w // width, area_h // height)
        self.wall = max(1, WALL * self.tile // TILE)
        self.offset = (self.panel_width + (area_w - width * self.tile) // 2,
                       MARGIN + (area_h - height * self.tile) // 2)
        self._make_sprites()

    def _menu_top(self) -> int:
        """Return the y of the centre of the first main-menu entry."""
        return (self._logo_top() + self.logo.get_height()
                + self.height * 16 // 100)

    def _logo_top(self) -> int:
        """Return the y of the top of the logo on the main menu."""
        return self.height * 5 // 100

    def menu_rects(self) -> list[pygame.Rect]:
        """Return the clickable area of each main-menu entry."""
        step = self.menu_font.get_height() * 22 // 10
        rects = []
        for index, label in enumerate(MENU_ITEMS):
            text_w, text_h = self.menu_font.size(label)
            rect = pygame.Rect(0, 0, text_w + 4 * text_h, 2 * text_h)
            rect.center = (self.width // 2, self._menu_top() + index * step)
            rects.append(rect)
        return rects

    def back_rect(self) -> pygame.Rect:
        """Return the area of the BACK button, bottom left."""
        text_w, text_h = self.hud_font.size(BACK_LABEL)
        return pygame.Rect(MARGIN, self.height - MARGIN - 2 * text_h,
                           text_w + 2 * text_h, 2 * text_h)

    def menu_item_at(self, pos: tuple[int, int]) -> int | None:
        """Return the index of the main-menu entry under pos, or None."""
        for index, rect in enumerate(self.menu_rects()):
            if rect.collidepoint(pos):
                return index
        return None

    def back_button_hit(self, pos: tuple[int, int]) -> bool:
        """Tell whether pos is on the BACK button."""
        return self.back_rect().collidepoint(pos)

    # ------------------------------------------------------------ sprites

    def _make_sprites(self) -> None:
        """Draw the pacgum, Pac-Man and ghost sprites for the cell size."""
        scale = self.tile / TILE
        self.pacgum_sprite = self.make_circle_sprite(
            max(1, round(3 * scale)), PACGUM_COLOR)
        self.super_sprite = self.make_circle_sprite(
            max(2, round(6 * scale)), PACGUM_COLOR)
        # the inside of a "42" cell, between its walls
        inner = self.tile - 2 * self.wall
        self.logo_sprite = pygame.Surface((inner, inner))
        self.draw_rect(self.logo_sprite, LOGO_COLOR, 0, 0, inner, inner)
        radius = max(3, round((TILE // 2 - 4) * scale))
        self.pacman_frames = {
            (facing, frame): self.make_pacman_sprite(radius, angle, mouth)
            for facing, angle in FACING_ANGLES.items()
            for frame, mouth in enumerate(MOUTH_ANGLES)
        }
        ghost_colors = {**GHOST_COLORS, "frightened": FRIGHT_COLOR,
                        "flashing": FLASH_COLOR}
        self.ghost_frames = {
            (name, facing): self.make_ghost_sprite(radius, color, angle)
            for name, color in ghost_colors.items()
            for facing, angle in FACING_ANGLES.items()
        }
        for facing, angle in FACING_ANGLES.items():
            self.ghost_frames[("eyes", facing)] = self.make_eyes_sprite(
                radius, angle)

    @staticmethod
    def fill_circle(surface: pygame.Surface, color: tuple[int, int, int],
                    cx: int, cy: int, radius: int) -> None:
        """Paint a disc on surface, pixel by pixel."""
        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= r2:
                    surface.set_at((cx + dx, cy + dy), color)

    def make_circle_sprite(self, radius: int,
                           color: tuple[int, int, int]) -> pygame.Surface:
        """Return a transparent sprite holding a disc."""
        size = radius * 2 + 1
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        self.fill_circle(sprite, color, radius, radius, radius)
        return sprite

    @staticmethod
    def make_pacman_sprite(radius: int, facing: float,
                           mouth: float) -> pygame.Surface:
        """Draw Pac-Man pixel by pixel: a disc minus the mouth wedge.

        Args:
            radius: Radius in pixels.
            facing: Direction of the mouth in degrees (0 = right, 90 = down).
            mouth: Opening of the mouth in degrees (0 = closed).
        """
        size = radius * 2 + 1
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                angle = math.degrees(math.atan2(dy, dx))
                if abs((angle - facing + 180) % 360 - 180) < mouth / 2:
                    continue  # inside the mouth
                sprite.set_at((radius + dx, radius + dy), PACMAN_COLOR)
        return sprite

    @staticmethod
    def make_ghost_sprite(radius: int, color: tuple[int, int, int],
                          facing: float) -> pygame.Surface:
        """Draw a ghost pixel by pixel: round head, wavy skirt, eyes.

        Args:
            radius: Half the width of the sprite, in pixels.
            color: Color of the body.
            facing: Where the eyes look, in degrees (0 = right, 90 = down).
        """
        size = radius * 2 + 1
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        skirt = max(2, radius // 3)  # height of the wavy bottom
        wave = size / 3  # width of one of the 3 waves
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dy < 0:  # round head
                    inside = dx * dx + dy * dy <= radius * radius
                elif dy <= radius - skirt:  # straight body
                    inside = True
                else:  # waves pointing down
                    centre = ((dx + radius) // wave + 0.5) * wave - radius
                    inside = (abs(dx - centre) * skirt
                              <= (radius - dy) * wave / 2)
                if inside:
                    sprite.set_at((radius + dx, radius + dy), color)
        GUI.draw_eyes(sprite, radius, facing)
        return sprite

    @staticmethod
    def make_eyes_sprite(radius: int, facing: float) -> pygame.Surface:
        """Draw only the eyes of a ghost: what is left once it is eaten."""
        size = radius * 2 + 1
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        GUI.draw_eyes(sprite, radius, facing)
        return sprite

    @staticmethod
    def draw_eyes(sprite: pygame.Surface, radius: int,
                  facing: float) -> None:
        """Paint the two eyes of a ghost, looking towards facing (degrees)."""
        look_x = round(math.cos(math.radians(facing)) * radius / 8)
        look_y = round(math.sin(math.radians(facing)) * radius / 8)
        eye_y = radius - round(radius * 0.2)
        for side in (-1, 1):
            eye_x = radius + side * round(radius * 0.4)
            GUI.fill_circle(sprite, EYE_COLOR, eye_x, eye_y,
                            max(1, round(radius * 0.3)))
            GUI.fill_circle(sprite, PUPIL_COLOR, eye_x + look_x,
                            eye_y + look_y, max(1, round(radius * 0.15)))

    # ------------------------------------------------------------ primitives

    def string_put(self, x: int, y: int, color: tuple[int, int, int],
                   font: pygame.font.Font, text: str) -> None:
        """Draw text with its top-left corner at (x, y)."""
        string = font.render(text, False, color)
        self.screen.blit(string, (x, y))

    def _text(self, font: pygame.font.Font, text: str,
              color: tuple[int, int, int], x: int, y: int,
              align: str = "left") -> None:
        """Draw text with its top at y; x is its left, centre or right."""
        if align == "center":
            x -= font.size(text)[0] // 2
        elif align == "right":
            x -= font.size(text)[0]
        self.string_put(x, y, color, font, text)

    def draw_rect(self, surface: pygame.Surface, color: tuple[int, int, int],
                  x: int, y: int, w: int, h: int) -> None:
        """Paint a filled rectangle on surface, pixel by pixel."""
        for py in range(y, y + h):
            for px in range(x, x + w):
                surface.set_at((px, py), color)

    def _frame(self, rect: pygame.Rect, color: tuple[int, int, int],
               thickness: int = 2) -> None:
        """Paint the outline of rect on the screen."""
        x, y, w, h = rect
        sides = ((x, y, w, thickness), (x, y + h - thickness, w, thickness),
                 (x, y, thickness, h), (x + w - thickness, y, thickness, h))
        for side in sides:
            self.draw_rect(self.screen, color, *side)

    def _title(self, text: str) -> int:
        """Draw a screen title at the top and return the y below it."""
        top = self.height * 7 // 100
        self._text(self.title_font, text, HIGHLIGHT_COLOR, self.width // 2,
                   top, "center")
        return top + self.title_font.get_height() * 2

    def _draw_back_button(self) -> None:
        """Draw the BACK button, lit when the mouse is over it."""
        rect = self.back_rect()
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        self._frame(rect, HIGHLIGHT_COLOR if hovered else WALL_COLOR)
        text_h = self.hud_font.get_height()
        self._text(self.hud_font, BACK_LABEL,
                   HIGHLIGHT_COLOR if hovered else TEXT_COLOR,
                   rect.centerx, rect.centery - text_h // 2, "center")

    # ------------------------------------------------------------ menus

    def draw_main_menu(self, menu_index: int) -> None:
        """Draw the logo, the parade of characters and the menu entries."""
        self.screen.fill(BG_COLOR)
        self.screen.blit(self.logo, ((self.width - self.logo.get_width())
                                     // 2, self._logo_top()))
        self._draw_parade(self._logo_top() + self.logo.get_height()
                          + self.height * 5 // 100)
        for index, rect in enumerate(self.menu_rects()):
            label = MENU_ITEMS[index]
            selected = index == menu_index
            text_w, text_h = self.menu_font.size(label)
            self._text(self.menu_font, label,
                       HIGHLIGHT_COLOR if selected else TEXT_COLOR,
                       rect.centerx, rect.centery - text_h // 2, "center")
            if selected:
                icon = self.icon_pacman
                self.screen.blit(icon, (rect.centerx - text_w // 2
                                        - icon.get_width() * 2,
                                        rect.centery - icon.get_height() // 2))
        small_h = self.small_font.get_height()
        self._text(self.small_font, MENU_HINT, DIM_COLOR, self.width // 2,
                   self.height - MARGIN - small_h * 4, "center")
        self._text(self.small_font, "© " + CREDITS, TEXT_COLOR,
                   self.width // 2, self.height - MARGIN - small_h, "center")

    def _draw_parade(self, centre_y: int) -> None:
        """Draw the four ghosts chasing Pac-Man, who chases three pacgums."""
        icons = [*self.icon_ghosts, self.icon_pacman]
        step = self.icon_pacman.get_width() * 3 // 2
        x = self.width // 2 - (len(icons) + 2) * step // 2
        for icon in icons:
            self.screen.blit(icon, (x, centre_y - icon.get_height() // 2))
            x += step
        for _ in range(3):
            dot = self.icon_pacgum
            self.screen.blit(dot, (x + step // 3, centre_y
                                   - dot.get_height() // 2))
            x += step * 2 // 3

    def draw_highscores(self, scores: Scores) -> None:
        """Draw the top 10, or a message when there is no score yet."""
        self.screen.fill(BG_COLOR)
        top = self._title("HIGH SCORES")
        entries = scores.fetch_entries()
        if not entries:
            self._text(self.menu_font, "NO SCORES YET", TEXT_COLOR,
                       self.width // 2, self.height // 2, "center")
        row_h = self.hud_font.get_height() * 2
        table_w = self.hud_font.size("10TH  " + "W" * 10 + "  " + "9" * 12)[0]
        left = (self.width - table_w) // 2
        name_x = left + self.hud_font.size("10TH  ")[0]
        for rank, entry in zip(RANKS, entries):
            self._text(self.hud_font, rank, HIGHLIGHT_COLOR, left, top)
            self._text(self.hud_font, str(entry.get("name", "?"))[:10],
                       TEXT_COLOR, name_x, top)
            self._text(self.hud_font, str(entry.get("score", "")),
                       TEXT_COLOR, left + table_w, top, "right")
            top += row_h
        self._draw_back_button()

    def draw_instructions(self, config: Config) -> None:
        """Draw the controls and the rules, with the points of the config."""
        self.screen.fill(BG_COLOR)
        top = self._title("INSTRUCTIONS")
        rows: list[tuple[pygame.Surface | None, str, str]] = [
            (None, "CONTROLS", ""),
            (None, "ARROWS / WASD (ZQSD)", "move Pac-Man"),
            (None, "ESC", "back to the menu"),
            (None, "MOUSE", "choose and click in the menus"),
            (None, "", ""),
            (None, "RULES", ""),
            (self.icon_pacgum, "PACGUM", f"{config.points_per_pacgum} pts"),
            (self.icon_super, "SUPER-PACGUM",
             f"{config.points_per_super_pacgum} pts"),
            (self.icon_ghosts[0], "GHOST", "costs a life"),
            (self.icon_frightened, "BLUE GHOST",
             f"{config.points_per_ghost} pts"),
            (None, "", ""),
            (None, "Eat every pacgum to clear the level.", ""),
            (None, f"{len(config.levels)} levels, {config.lives} lives.", ""),
        ]
        row_h = self.hud_font.get_height() * 2
        key_w = max(self.hud_font.size(key)[0] for _, key, text in rows
                    if text)
        text_w = max(self.hud_font.size(text)[0] for _, _, text in rows)
        gap = self.hud_font.size("   ")[0]
        left = (self.width - key_w - gap - text_w) // 2
        middle = left + key_w + gap
        for icon, key, text in rows:
            heading = key in ("CONTROLS", "RULES")
            if icon is not None:
                self.screen.blit(icon, (left - icon.get_width() - gap // 2,
                                        top + (self.hud_font.get_height()
                                               - icon.get_height()) // 2))
            self._text(self.hud_font, key,
                       HIGHLIGHT_COLOR if heading else TEXT_COLOR, left, top)
            self._text(self.hud_font, text, TEXT_COLOR, middle, top)
            top += row_h
        self._draw_back_button()

    # ------------------------------------------------------------ game

    def create_maze_surface(self, maze: list[list[int]]) -> pygame.Surface:
        """Draw the walls of maze once, on a surface blitted every frame.

        The "42" cells stay empty here: draw_logo fills them every frame.
        """
        tile, wall = self.tile, self.wall
        surface = pygame.Surface((len(maze[0]) * tile, len(maze) * tile))
        surface.fill(BG_COLOR)
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                px, py = x * tile, y * tile
                if cell & TOP:
                    self.draw_rect(surface, WALL_COLOR, px, py, tile, wall)
                if cell & RIGHT:
                    self.draw_rect(surface, WALL_COLOR, px + tile - wall, py,
                                   wall, tile)
                if cell & BOTTOM:
                    self.draw_rect(surface, WALL_COLOR, px, py + tile - wall,
                                   tile, wall)
                if cell & LEFT:
                    self.draw_rect(surface, WALL_COLOR, px, py, wall, tile)
        return surface

    def draw_pacgums(self, available_pg: set[tuple[int, int]],
                     available_spg: set[tuple[int, int]]) -> None:
        """Draw the pacgums and super-pacgums left in the level."""
        for x, y in available_pg:
            self._blit_on_cell(self.pacgum_sprite, (x, y))
        for x, y in available_spg:
            self._blit_on_cell(self.super_sprite, (x, y))

    def draw_maze(self, maze_surface: pygame.Surface) -> None:
        """Clear the screen, then draw the maze and the BACK button."""
        self.screen.fill(BG_COLOR)
        self.screen.blit(maze_surface, self.offset)
        self._draw_back_button()

    def draw_logo(self, cells: list[tuple[int, int]]) -> None:
        """Fill these cells of the "42"; the others stay empty."""
        ox, oy = self.offset
        for x, y in cells:
            px = ox + x * self.tile + self.wall
            py = oy + y * self.tile + self.wall
            self.screen.blit(self.logo_sprite, (px, py))

    def draw_player(self, pos: tuple[float, float], facing: str,
                    opening: float) -> None:
        """Draw Pac-Man, his mouth open by opening (0 to 1)."""
        frame = round(opening * (len(MOUTH_ANGLES) - 1))
        self._blit_on_cell(self.pacman_frames[(facing, frame)], pos)

    @staticmethod
    def ghost_look(name: str, fright_time: float,
                   eaten: bool = False) -> str:
        """Return which frames to draw: own, blue, flashing or eyes only.

        An edible ghost is blue, and flashes white 4 times per second
        during its last FLASH_TIME seconds. An eaten one is only eyes.
        """
        if eaten:
            return "eyes"
        if fright_time <= 0:
            return name
        if fright_time < FLASH_TIME and int(fright_time * 8) % 2 == 1:
            return "flashing"
        return "frightened"

    def draw_ghost(self, pos: tuple[float, float], name: str, facing: str,
                   fright_time: float = 0.0, eaten: bool = False) -> None:
        """Draw a ghost, its eyes looking where it goes."""
        look = self.ghost_look(name, fright_time, eaten)
        self._blit_on_cell(self.ghost_frames[(look, facing)], pos)

    def _blit_on_cell(self, sprite: pygame.Surface,
                      pos: tuple[float, float]) -> None:
        """Draw sprite centred on pos, given in cells (can be between two)."""
        ox, oy = self.offset
        width, height = sprite.get_size()
        px = ox + pos[0] * self.tile + (self.tile - width) // 2
        py = oy + pos[1] * self.tile + (self.tile - height) // 2
        self.screen.blit(sprite, (px, py))

    @staticmethod
    def format_time(seconds: float) -> str:
        """Return seconds as m:ss, rounded up: 90 -> "1:30", 0.2 -> "0:01"."""
        whole = max(0, math.ceil(seconds))
        return f"{whole // 60}:{whole % 60:02d}"

    def draw_hud(self, score: int, level: int, lives: int,
                 time_left: float) -> None:
        """Draw the score, level, time and lives left of the maze."""
        y = MARGIN * 2
        for label, value in (("SCORE", str(score)), ("LEVEL", str(level)),
                             ("TIME", self.format_time(time_left))):
            self._text(self.hud_font, label, HIGHLIGHT_COLOR, MARGIN, y)
            y += self.hud_font.get_height() * 3 // 2
            self._text(self.menu_font, value, TEXT_COLOR, MARGIN, y)
            y += self.menu_font.get_height() * 2
        self._text(self.hud_font, "LIVES", HIGHLIGHT_COLOR, MARGIN, y)
        y += self.hud_font.get_height() * 3 // 2
        icon = self.icon_pacman
        step = icon.get_width() * 3 // 2
        per_row = max(1, (self.panel_width - 2 * MARGIN) // step)
        for life in range(lives):
            self.screen.blit(icon, (MARGIN + life % per_row * step,
                                    y + life // per_row * step))
