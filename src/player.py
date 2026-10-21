"""Pac-Man's movement on the maze grid."""
import math

from src.constants import BOTTOM, LEFT, RIGHT, TOP

BASE_SPEED = 4.0  # cells per second on the first level
SPEED_PER_LEVEL = 0.2  # added for each following level

# direction -> (dx, dy, wall bit that closes this side of a cell)
DIRECTIONS: dict[str, tuple[int, int, int]] = {
    "up": (0, -1, TOP),
    "down": (0, 1, BOTTOM),
    "left": (-1, 0, LEFT),
    "right": (1, 0, RIGHT),
}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


def level_speed(index: int) -> float:
    """Return the player speed on the level at position index (0 = first)."""
    return BASE_SPEED + SPEED_PER_LEVEL * index


def can_move(maze: list[list[int]], cell: tuple[int, int],
             direction: str) -> bool:
    """Tell whether no wall closes that side of the cell."""
    x, y = cell
    return maze[y][x] & DIRECTIONS[direction][2] == 0


class Player:
    """Pac-Man: glides from cell to cell and never crosses a wall."""

    def __init__(self, start_position: tuple[int, int],
                 speed: float = BASE_SPEED) -> None:
        """Create the player, standing still on its starting cell.

        Args:
            start_position: Starting cell (x, y).
            speed: Speed in cells per second.
        """
        self.start_position, self.speed = start_position, speed
        self.cell = start_position  # cell being left, or occupied if still
        self.progress = 0.0  # 0 = on self.cell, 1 = on the next cell
        self.direction: str | None = None  # current movement
        self.wanted: str | None = None  # last direction asked by the player
        self.facing = "right"  # last movement, where the mouth points

    @property
    def position(self) -> tuple[float, float]:
        """Return the position in cells, between two cells while moving."""
        x, y = self.cell
        if self.direction is None:
            return float(x), float(y)
        dx, dy, _ = DIRECTIONS[self.direction]
        return x + dx * self.progress, y + dy * self.progress

    @property
    def mouth_opening(self) -> float:
        """Return how open the mouth is, from 0 (closed) to 1 (wide open).

        It closes on each cell centre and opens wide halfway, so Pac-Man
        chomps once per cell; when still, the mouth stays half open.
        """
        if self.direction is None:
            return 0.5
        return abs(math.sin(math.pi * self.progress))

    def turn(self, direction: str) -> None:
        """Remember the asked direction; a U-turn happens immediately."""
        self.wanted = direction
        if (self.direction is not None and self.progress > 0
                and direction == OPPOSITE[self.direction]):
            dx, dy, _ = DIRECTIONS[self.direction]
            self.cell = (self.cell[0] + dx, self.cell[1] + dy)
            self.progress = 1 - self.progress
            self.direction = direction
            self.facing = direction

    def update(self, maze: list[list[int]], dt: float) -> None:
        """Move speed * dt cells along the corridors.

        On each cell centre the player takes the wanted direction if it is
        open, otherwise keeps going straight, and stops against a wall.
        """
        distance = self.speed * dt
        while distance > 0:
            if self.progress == 0:
                self.direction = self._next_direction(maze)
            if self.direction is None:
                return
            self.facing = self.direction
            remaining = 1 - self.progress
            if distance < remaining:
                self.progress += distance
                return
            distance -= remaining
            dx, dy, _ = DIRECTIONS[self.direction]
            self.cell = (self.cell[0] + dx, self.cell[1] + dy)
            self.progress = 0.0

    def _next_direction(self, maze: list[list[int]]) -> str | None:
        """Return the direction to follow from a cell centre, or None."""
        for direction in (self.wanted, self.direction):
            if direction is not None and can_move(maze, self.cell, direction):
                return direction
        return None
