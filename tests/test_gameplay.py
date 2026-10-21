"""Tests for src/game/gameplay.py: eating, score and level changes."""
from pathlib import Path

import pygame
import pytest

from src.game.gameplay import Gameplay
from src.game.scores import Scores
from src.gui import GUI
from src.parser import Config
from src.player import DIRECTIONS, can_move

ROOT = Path(__file__).resolve().parent.parent


class FakeApp:
    """Stands for the Pacman state machine."""

    running = True
    game_active = True
    state = "game"


@pytest.fixture
def app() -> FakeApp:
    """The fake state machine the game session talks to."""
    return FakeApp()


@pytest.fixture
def gameplay(app: FakeApp, monkeypatch: pytest.MonkeyPatch,
             tmp_path: Path) -> Gameplay:
    """A game session on the default configuration, without a window."""
    monkeypatch.chdir(ROOT)  # the assets are loaded with relative paths
    pygame.init()
    screen = pygame.display.set_mode((1400, 800))
    scores = Scores(str(tmp_path / "scores.json"))
    return Gameplay(app, Config(), scores, GUI(screen, app))


def clear(gameplay: Gameplay) -> None:
    """Eat everything in the current level at once."""
    gameplay.level.available_pacgums.clear()
    gameplay.level.available_super_pacgums.clear()


def test_eating_a_pacgum_adds_its_points(gameplay: Gameplay) -> None:
    """Reaching a cell with a pacgum eats it and adds 10 points."""
    level = gameplay.level
    start = level.player_start
    direction = next(d for d in DIRECTIONS if can_move(level.maze, start, d))
    dx, dy, _ = DIRECTIONS[direction]
    target = (start[0] + dx, start[1] + dy)
    level.available_pacgums.add(target)
    level.player.turn(direction)
    gameplay.update([], 1 / level.player.speed)  # exactly one cell
    assert target not in level.available_pacgums
    assert gameplay.score == 10
    gameplay.draw()  # the HUD shows the score without error


def test_clearing_a_level_loads_the_next_one(gameplay: Gameplay) -> None:
    """With nothing left to eat, the next level starts; the score stays."""
    gameplay.score = 1234
    clear(gameplay)
    gameplay.update([], 0)
    assert gameplay.level_index == 1
    assert gameplay.level.dimensions == (10, 10)
    assert gameplay.score == 1234


def test_last_level_returns_to_the_menu(gameplay: Gameplay,
                                        app: FakeApp) -> None:
    """After the last level, the game goes back to the main menu."""
    gameplay._load_level(len(gameplay.config.levels) - 1)
    clear(gameplay)
    gameplay.update([], 0)
    assert app.state == "main_menu"
    assert app.game_active is False
