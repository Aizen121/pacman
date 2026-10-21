import math
import pygame
from .constants import (FONT, LOGO, PACMAN, TILE, TOP, RIGHT, BOTTOM, LEFT,
                        WALL_COLOR, WALL, MAZE_LEFT, MARGIN, LOGO_COLOR)
from .constants import (FACING_ANGLES, MOUTH_ANGLES, PACMAN_COLOR, TEXT_COLOR,
                        GHOST_COLORS, EYE_COLOR, PUPIL_COLOR)
from src.game.scores import Scores


class GUI:

    def __init__(self, screen: pygame.Surface, program: "Pacman") -> None:

        self.screen = screen
        self.program = program
        self.logo = pygame.image.load(LOGO).convert_alpha()
        self.player = pygame.image.load(PACMAN).convert_alpha()
        self.tile, self.wall = TILE, WALL
        self.offset = (MAZE_LEFT, MARGIN)
        self._make_sprites()
        self.hud_font = pygame.font.Font(FONT, 20)

    def set_layout(self, width: int, height: int) -> None:
        """Fit a maze of width x height cells in the window.

        Cells are at most TILE pixels wide: small mazes keep that size and
        big ones shrink until they fit. The maze is centred in the area
        right of the HUD, and the sprites are redrawn at the new size.
        """
        area_w = self.screen.get_width() - MAZE_LEFT - MARGIN
        area_h = self.screen.get_height() - 2 * MARGIN
        self.tile = min(TILE, area_w // width, area_h // height)
        self.wall = max(1, WALL * self.tile // TILE)
        self.offset = (MAZE_LEFT + (area_w - width * self.tile) // 2,
                       MARGIN + (area_h - height * self.tile) // 2)
        self._make_sprites()

    def _make_sprites(self) -> None:
        """Draw the pacgum and Pac-Man sprites for the current cell size."""
        scale = self.tile / TILE
        self.pacgum_sprite = self.make_circle_sprite(
            max(1, round(3 * scale)), (255, 253, 208))
        self.super_sprite = self.make_circle_sprite(
            max(2, round(6 * scale)), (255, 253, 208))
        radius = max(3, round((TILE // 2 - 4) * scale))
        self.pacman_frames = {
            (facing, frame): self.make_pacman_sprite(radius, angle, mouth)
            for facing, angle in FACING_ANGLES.items()
            for frame, mouth in enumerate(MOUTH_ANGLES)
        }
        self.ghost_frames = {
            (name, facing): self.make_ghost_sprite(radius, color, angle)
            for name, color in GHOST_COLORS.items()
            for facing, angle in FACING_ANGLES.items()
        }
 
    @staticmethod
    def fill_circle(surface: pygame.Surface, color: tuple[int, int, int],
                    cx: int, cy: int, radius: int) -> None:

        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= r2:
                    surface.set_at((cx + dx, cy + dy), color)

    def make_circle_sprite(self, radius: int, color: tuple[int, int, int]) -> pygame.Surface:
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
        look_x = round(math.cos(math.radians(facing)) * radius / 8)
        look_y = round(math.sin(math.radians(facing)) * radius / 8)
        eye_y = radius - round(radius * 0.2)
        for side in (-1, 1):
            eye_x = radius + side * round(radius * 0.4)
            GUI.fill_circle(sprite, EYE_COLOR, eye_x, eye_y,
                            max(1, round(radius * 0.3)))
            GUI.fill_circle(sprite, PUPIL_COLOR, eye_x + look_x,
                            eye_y + look_y, max(1, round(radius * 0.15)))
        return sprite

    def string_put(self, x: int, y: int, color: tuple[int, int, int],
                   font: pygame.font.Font, text: str) -> None:

        string = font.render(text, False, color)
        self.screen.blit(string, (x, y))

    def draw_cursor(self, x: int, y: int, size: int, color: tuple[int, int, int]) -> None:

        medial_point = size // 2

        for row in range(size):
            width = size * (medial_point - abs(row - medial_point)) // medial_point
            for px in range(width):
                self.screen.set_at((x + px, y + row), color)

    def draw_main_menu(self, menu_index: int) -> None:

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (300, 20))

        font = pygame.font.Font(FONT, 30)
        self.string_put(500, 300, (255, 253, 208), font, "1 START")
        self.string_put(500, 370, (255, 253, 208), font, "2 HIGHSCORES")
        self.string_put(500, 440, (255, 253, 208), font, "3 INSTRUCTIONS")
        self.string_put(500, 510, (255, 253, 208), font, "4 EXIT")
        self.string_put(10, 650, (255, 253, 208), font, "© This project has been created as part of the")
        self.string_put(10, 700, (255, 253, 208), font, "42 curriculum by rvaz-da-")

        if menu_index == 0:
            self.draw_cursor(470, 300, 20, (255, 253, 208))
        elif menu_index == 1:
            self.draw_cursor(470, 370, 20, (255, 253, 208))
        elif menu_index == 2:
            self.draw_cursor(470, 440, 20, (255, 253, 208)) 
        elif menu_index == 3:
            self.draw_cursor(470, 510, 20, (255, 253, 208))

    def draw_highscores(self, scores: Scores) -> None:

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (300, 20))

        title_font = pygame.font.Font(FONT, 50)
        self.string_put(415, 280, (255, 253, 208), title_font, "HIGH SCORES")
        
        top_ten = scores.fetch_entries()
        small_font = pygame.font.Font(FONT, 20)
        self.draw_cursor(80, 700, 20, (255, 253, 208))
        self.string_put(110, 703, (255, 253, 208), small_font, "Back")
        if top_ten == []: 
            self.string_put(520, 500, (255, 253, 208), small_font, "No scores yet :(")
            return

        rank_font = pygame.font.Font(FONT, 25)
        positions = ["1ST", "2ND", "3RD", "4TH", "5TH", "6TH", "7TH", "8TH", "9TH", "10TH"]
        sx, sy = 370, 350
        for i, position in enumerate(positions[:len(top_ten)]):
            sy += 35
            self.string_put(sx, sy, (255, 253, 208), rank_font, position)
            pos_w = rank_font.size("W"*4)[0]
            sp_w = rank_font.size(" ")[0]
            name_x = sx + pos_w + sp_w
            self.string_put(name_x, sy, (255, 253, 208), rank_font, top_ten[i]["name"])
            name_w = rank_font.size("W"*15)[0]
            self.string_put(name_x + name_w + 15, sy, (255, 253, 208), rank_font, top_ten[i]["score"])
 
    def draw_instructions(self) -> None:

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (300, 200))

        title_font = pygame.font.Font(FONT, 50)
        # self.string_put( , (255, 253, 208), title_font, "INSTRUCTIONS")

    def draw_rect(self, surface: pygame.Surface, color: tuple[int, int, int], x: int, y: int, w: int, h: int) -> None:

        for py in range(y, y + h):
            for px in range(x, x + w):
                surface.set_at((px, py), color) 

    def create_maze_surface(self, maze: list[list[int]]) -> pygame.Surface:

        tile, wall = self.tile, self.wall
        surface = pygame.Surface((len(maze[0]) * tile, len(maze) * tile))

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                px, py = x * tile, y * tile
                if cell == 15:
                    self.draw_rect(surface, LOGO_COLOR, px, py, tile, tile)
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

    def draw_pacgums(self, available_pg: set[tuple[int, int]], available_spg: set[tuple[int, int]]) -> None:

        ox, oy = self.offset
        tile = self.tile
        w_pg, h_pg = self.pacgum_sprite.get_size()
        w_spg, h_spg = self.super_sprite.get_size()

        for x, y in available_pg:
            px = ox + x * tile + (tile - w_pg) // 2
            py = oy + y * tile + (tile - h_pg) // 2
            self.screen.blit(self.pacgum_sprite, (px, py))
        for x, y in available_spg:
            px = ox + x * tile + (tile - w_spg) // 2
            py = oy + y * tile + (tile - h_spg) // 2
            self.screen.blit(self.super_sprite, (px, py))

    def draw_maze(self, maze_surface: pygame.Surface) -> None:
    
        self.screen.fill((0, 0, 0))
        self.screen.blit(maze_surface, self.offset)
        self.draw_cursor(80, 700, 20, (255, 253, 208))
        self.string_put(110, 703, (255, 253, 208), self.hud_font, "Back")

    def draw_player(self, pos: tuple[float, float], facing: str,
                    opening: float) -> None:

        frame = round(opening * (len(MOUTH_ANGLES) - 1))
        self._blit_on_cell(self.pacman_frames[(facing, frame)], pos)

    def draw_ghost(self, pos: tuple[float, float], name: str,
                   facing: str) -> None:
        """Draw a ghost, its eyes looking where it goes."""
        self._blit_on_cell(self.ghost_frames[(name, facing)], pos)

    def _blit_on_cell(self, sprite: pygame.Surface,
                      pos: tuple[float, float]) -> None:
        """Draw sprite centred on pos, given in cells (can be between two)."""
        ox, oy = self.offset
        width, height = sprite.get_size()
        px = ox + pos[0] * self.tile + (self.tile - width) // 2
        py = oy + pos[1] * self.tile + (self.tile - height) // 2
        self.screen.blit(sprite, (px, py))

    def draw_hud(self, score: int, level: int, lives: int) -> None:
        """Draw the score, the level number and the lives left of the maze."""
        self.string_put(30, 60, TEXT_COLOR, self.hud_font, "SCORE")
        self.string_put(30, 95, TEXT_COLOR, self.hud_font, str(score))
        self.string_put(30, 160, TEXT_COLOR, self.hud_font, "LEVEL")
        self.string_put(30, 195, TEXT_COLOR, self.hud_font, str(level))
        self.string_put(30, 260, TEXT_COLOR, self.hud_font, "LIVES")
        self.string_put(30, 295, TEXT_COLOR, self.hud_font, str(lives))
