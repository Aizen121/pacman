"""Tests for src/gui.py: the Pac-Man sprite and the maze layout."""
from pathlib import Path

import pygame
import pytest

from src.constants import MAZE_LEFT
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
