"""Tests for src/gui.py: the Pac-Man sprite and the maze layout."""
from pathlib import Path

import pygame
import pytest

from src.constants import (EYE_COLOR, GHOST_COLORS, LOGO_COLOR, MAZE_LEFT,
                           PUPIL_COLOR)
from src.game.scores import Scores
from src.gui import GUI
from src.parser import Config

ROOT = Path(__file__).resolve().parent.parent

RADIUS = 20


def is_drawn(facing: float, mouth: float, dx: int, dy: int) -> bool:
    """Tell whether the pixel at (dx, dy) from the centre is painted."""
    sprite = GUI.make_pacman_sprite(RADIUS, facing, mouth)
    return sprite.get_at((RADIUS + dx, RADIUS + dy)).a == 255


def test_closed_mouth_is_a_full_disc() -> None:
    """With the mouth closed, both sides of the disc are painted."""
    assert is_drawn(0, 0, 15, 0)
    assert is_drawn(0, 0, -15, 0)


def test_open_mouth_points_where_pacman_faces() -> None:
    """The mouth is a transparent wedge on the facing side only."""
    assert not is_drawn(0, 90, 15, 0)  # facing right: hole on the right
    assert is_drawn(0, 90, -15, 0)
    assert not is_drawn(270, 90, 0, -15)  # facing up: hole on top
    assert is_drawn(270, 90, 0, 15)


def test_corners_stay_transparent() -> None:
    """Pixels outside the disc are never painted."""
    assert not is_drawn(0, 0, -RADIUS, -RADIUS)


@pytest.fixture
def gui(monkeypatch: pytest.MonkeyPatch) -> GUI:
    """The GUI on a 1400 x 800 screen, without a window."""
    monkeypatch.chdir(ROOT)  # the assets are loaded with relative paths
    pygame.init()
    return GUI(pygame.display.set_mode((1400, 800)), None)


@pytest.mark.parametrize("size, tile", [(5, 50), (15, 50), (20, 37),
                                        (42, 17), (50, 15)])
def test_cell_size_fits_the_window(gui: GUI, size: int, tile: int) -> None:
    """Small mazes keep 50 px cells; bigger ones get smaller cells."""
    gui.set_layout(size, size)
    assert gui.tile == tile


def test_every_default_level_fits_on_screen(gui: GUI) -> None:
    """Each default level is fully visible, right of the HUD."""
    for level in Config().levels:
        gui.set_layout(level.width, level.height)
        x, y = gui.offset
        assert x >= MAZE_LEFT and y >= 0
        assert x + level.width * gui.tile <= 1400
        assert y + level.height * gui.tile <= 800


def test_pacman_stays_smaller_than_a_cell(gui: GUI) -> None:
    """The sprites are redrawn at the size of the new cells."""
    for size in (15, 42, 50):
        gui.set_layout(size, size)
        assert gui.pacman_frames[("right", 0)].get_width() < gui.tile


def test_logo_sprite_fills_a_cell_inside_its_walls(gui: GUI) -> None:
    """A lit "42" cell is cream, between the walls of the cell."""
    for size in (15, 42):
        gui.set_layout(size, size)
        inner = gui.tile - 2 * gui.wall
        assert gui.logo_sprite.get_size() == (inner, inner)
        assert tuple(gui.logo_sprite.get_at((0, 0)))[:3] == LOGO_COLOR


@pytest.mark.parametrize("seconds, shown", [
    (90, "1:30"), (89.2, "1:30"), (59.5, "1:00"), (9, "0:09"),
    (0.2, "0:01"), (0, "0:00"), (600, "10:00")])
def test_time_is_shown_as_minutes_and_seconds(seconds: float,
                                              shown: str) -> None:
    """The HUD shows the time left as m:ss, rounded up."""
    assert GUI.format_time(seconds) == shown


def test_ghost_sprite_shape() -> None:
    """Round head, body color in the middle, transparent corners."""
    red = GHOST_COLORS["blinky"]
    sprite = GUI.make_ghost_sprite(RADIUS, red, 0)
    assert tuple(sprite.get_at((RADIUS, 1)))[:3] == red
    assert tuple(sprite.get_at((RADIUS, RADIUS)))[:3] == red
    assert sprite.get_at((0, 0)).a == 0


def pupils_x(facing: float) -> float:
    """Return the mean x of the pupil pixels of a ghost sprite."""
    sprite = GUI.make_ghost_sprite(RADIUS, GHOST_COLORS["blinky"], facing)
    size = sprite.get_width()
    xs = [x for x in range(size) for y in range(size)
          if tuple(sprite.get_at((x, y)))[:3] == PUPIL_COLOR]
    return sum(xs) / len(xs)


def test_ghost_eyes_look_where_it_goes() -> None:
    """The pupils move to the right or to the left of the eyes."""
    assert pupils_x(0) > RADIUS > pupils_x(180)


@pytest.mark.parametrize("fright_time, look", [
    (0.0, "pinky"), (5.0, "frightened"), (1.9, "flashing"),
    (1.8, "frightened")])
def test_edible_ghosts_are_blue_then_flash(fright_time: float,
                                           look: str) -> None:
    """Blue while edible, flashing white in the last FLASH_TIME seconds."""
    assert GUI.ghost_look("pinky", fright_time) == look


def test_eaten_ghosts_are_only_eyes() -> None:
    """An eaten ghost shows its eyes, without a body."""
    assert GUI.ghost_look("pinky", 3.0, eaten=True) == "eyes"
    sprite = GUI.make_eyes_sprite(RADIUS, 0)
    assert sprite.get_at((RADIUS, RADIUS)).a == 0  # no body
    colors = {tuple(sprite.get_at((x, y)))[:3]
              for x in range(sprite.get_width())
              for y in range(sprite.get_height())}
    assert EYE_COLOR in colors and PUPIL_COLOR in colors


@pytest.mark.parametrize("size", [(1280, 720), (1440, 900), (1920, 1080)])
def test_every_screen_draws_on_usual_screens(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        size: tuple[int, int]) -> None:
    """Menus, scores, instructions and HUD draw on usual screen sizes."""
    monkeypatch.chdir(ROOT)
    pygame.init()
    gui = GUI(pygame.display.set_mode(size), None)
    gui.draw_main_menu(1)
    gui.draw_highscores(Scores(str(tmp_path / "scores.json")))
    gui.draw_instructions(Config())
    gui.draw_hud(1234, 2, 9, 87.2)
    for rect in gui.menu_rects() + [gui.back_rect()]:
        assert 0 <= rect.top and rect.bottom <= size[1]


def test_menu_entries_are_clickable(gui: GUI) -> None:
    """Each entry answers to a click on its centre, and only there."""
    for index, rect in enumerate(gui.menu_rects()):
        assert gui.menu_item_at(rect.center) == index
    assert gui.menu_item_at((0, 0)) is None


def test_back_button_is_clickable(gui: GUI) -> None:
    """The BACK button, bottom left, answers to a click on it."""
    rect = gui.back_rect()
    assert gui.back_button_hit(rect.center)
    assert not gui.back_button_hit((gui.width - 1, 0))
    assert rect.right < gui.width // 3
