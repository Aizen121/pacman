"""Tests for src/ghost.py: how a ghost chooses its way."""
import pytest

from src.game.level import Level
from src.ghost import Ghost
from src.parser import Config, LevelSize
from src.player import Player

# 3 x 3 ring around a closed cell (15); (0, 1) is a dead end that only
# opens upwards: a wall separates it from (0, 2).
RING = [[9, 5, 3], [14, 15, 10], [13, 5, 6]]


def test_default_speed_is_90_percent_of_pacman() -> None:
    """Ghosts are a bit slower than Pac-Man."""
    assert Ghost("blinky", (0, 0)).speed == pytest.approx(3.6)


def test_follows_the_corridors_not_the_straight_line() -> None:
    """(0, 1) is next to the target as the crow flies, but a dead end."""
    ghost = Ghost("blinky", (0, 0))
    ghost.target = (0, 2)
    assert ghost.choose_direction(RING) == "right"


def test_never_turns_back_on_its_own() -> None:
    """Even with its target behind, a ghost keeps going."""
    ghost = Ghost("blinky", (1, 0))
    ghost.direction, ghost.target = "right", (0, 0)
    assert ghost.choose_direction(RING) == "right"


def test_turns_back_in_a_dead_end() -> None:
    """In a dead end, going back is the only way out."""
    ghost = Ghost("blinky", (0, 1))
    ghost.direction = "down"
    assert ghost.choose_direction(RING) == "up"


def test_blinky_aims_at_pacman() -> None:
    """Blinky's target is the cell of Pac-Man."""
    ghost, player = Ghost("blinky", (2, 0)), Player((0, 2))
    ghost.chase(player)
    assert ghost.target == (0, 2)


def test_catches_a_still_pacman_on_a_real_maze() -> None:
    """From its corner, Blinky reaches Pac-Man in the middle of a maze."""
    level = Level(LevelSize(width=15, height=15), Config(), 42)
    ghost, player = level.ghosts[0], level.player
    for _ in range(60 * 20):  # at most 20 seconds
        ghost.chase(player)
        ghost.update(level.maze, 1 / 60)
        if ghost.touches(player):
            break
    assert ghost.touches(player)


def test_touches_means_less_than_half_a_cell() -> None:
    """Two movers touch when they are less than half a cell apart."""
    ghost, other = Ghost("blinky", (0, 0)), Ghost("blinky", (1, 0))
    assert not ghost.touches(other)
    other.direction, other.progress = "left", 0.6  # now at x = 0.4
    assert ghost.touches(other)
