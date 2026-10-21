"""Tests for the pixel-drawn Pac-Man sprite of src/gui.py."""
from src.gui import GUI

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
